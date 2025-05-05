# *************************************************************************** #
# Calculate DG (Deckungsgrad) per polygon.
# Needs a detailed VHM, usually 1.5m max.
#
# Definition of stand layers (Bestandesschichten)
#
# Keine Schicht (ks): < 40 cm
# Unterschicht (us): 40cm bis 1/3 der Oberhoehe (hdom)
# Mittelschicht (ms): 1/3 bis 2/3 der Oberhoehe (hdom)
# Oberschicht (os): 2/3 bis 3/3 der Oberhoehe (hdom)
# Ueberhaelter (ueb): > hmax
# DG Bestand: os + ueb (hdom < 14m: ms + os + ueb)
#
# --> Also see e.g. LFI definition (DE): https://www.lfi.ch/publikationen/publ/LFI4_Anleitung_2017.pdf
#
# Authors: Hannes Horneber, Dominique Weber, Christoph Schaller (BFH-HAFL)
# *************************************************************************** #
"""
/***************************************************************************
    TBk: Toolkit Bestandeskarte (QGIS Plugin)
    Toolkit for the generating and processing forest stand maps
    Copyright (C) 2025 BFH-HAFL (hannes.horneber@bfh.ch, christian.rosset@bfh.ch)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
 ***************************************************************************/
"""

import processing
from datetime import timedelta
import time

from tbk_qgis.tbk.general.tbk_utilities import *


def calculate_dg(working_root,
                 stands_dg,
                 tmp_output_folder,
                 dg_dir,
                 vhm,
                 del_tmp=True):
    print("--------------------------------------------")
    print("START DG calculation...")

    # Create dg layer output directory
    if not os.path.exists(dg_dir):
        os.makedirs(dg_dir)

    # DG file names
    dg_file_names = {
        "ks": "dg_layer_ks.tif",
        "us": "dg_layer_us.tif",
        "ms": "dg_layer_ms.tif",
        "os": "dg_layer_os.tif",
        "ueb": "dg_layer_ueb.tif",
        "main": "dg_layer.tif"
    }

    # Dictionary containing the path to the crown coverage files
    dg_files = {key: os.path.join(dg_dir, filename) for key, filename in dg_file_names.items()}

    # Temporary files
    tmp_files_names = {
        "ks_max": "dg_ks_max.tif",
        "us_min": "dg_us_min.tif",
        "ms_min": "dg_ms_min.tif",
        "lim_os": "dg_lim_os.tif",
        "lim_ueb": "dg_lim_ueb.tif",
        "lim_dg": "dg_lim_dg.tif"
    }

    # Dictionary containing the path to temp files
    tmp_files = {key: os.path.join(tmp_output_folder, filename) for key, filename in tmp_files_names.items()}

    # Layer threshold values (based on NFI definition, www.lfi.ch)
    max_height_ks = 1.0
    min_height_us = 1.0
    min_height_hdom_factor_ms = 1.0 / 3.0
    min_height_hdom_factor_os = 2.0 / 3.0
    min_height_hmax_factor_ueb = 1.0

    ########################################################################

    stands_layer = QgsVectorLayer(stands_dg, "stands", "ogr")

    # Add DG limits fields per stand
    with edit(stands_layer):
        provider = stands_layer.dataProvider()
        provider.addAttributes([QgsField("dg_ks_max", QVariant.Double),
                                QgsField("dg_us_min", QVariant.Double),
                                QgsField("dg_ms_min", QVariant.Double),
                                QgsField("dg_os_min", QVariant.Double),
                                QgsField("dg_ueb_min", QVariant.Double),
                                QgsField("dg_min", QVariant.Double)])
        stands_layer.updateFields()

        # Calculate DG limits per stand
        print("calculating DG limits...")

        for f in stands_layer.getFeatures():
            f["dg_ks_max"] = max_height_ks
            f["dg_us_min"] = min_height_us
            f["dg_ms_min"] = f["hdom"] * min_height_hdom_factor_ms
            f["dg_os_min"] = f["hdom"] * min_height_hdom_factor_os
            f["dg_ueb_min"] = f["hmax"] * min_height_hmax_factor_ueb
            if f["hdom"] < 14:
                # fix small stands issue
                f["dg_min"] = f["hdom"] * min_height_hdom_factor_ms
            else:
                f["dg_min"] = f["dg_os_min"]

            stands_layer.updateFeature(f)

    # create a list (for iteration) with dg-classes to be calculated
    # assign: 1. a column_prefix, 2. a limit (dg_lim_field),
    # 3. - 5. the necessary raster layers (dg_tmp_file_b and C as well as dg_layer_file)
    # and 6. the raster calculator formula for each dg-type
    field_file_pairs = [
        ['dg_ueb_', 'dg_ueb_min', tmp_files['lim_ueb'], None, dg_files["ueb"], '((A>B) & True)*1'],
        ['dg_os_', 'dg_os_min', tmp_files['lim_os'], tmp_files['lim_ueb'], dg_files["os"], '((A>B) & (A<=C))*1'],
        ['dg_ms_', 'dg_ms_min', tmp_files['ms_min'], tmp_files['lim_os'], dg_files["ms"], '((A>B) & (A<=C))*1'],
        ['dg_us_', 'dg_us_min', tmp_files['us_min'], tmp_files['ms_min'], dg_files["us"], '((A>=B) & (A<=C))*1'],
        ['dg_ks_', 'dg_ks_max', tmp_files['ks_max'], tmp_files['us_min'], dg_files["ks"], '((A<B) & True)*1'],
        ['dg_', 'dg_min', tmp_files['lim_dg'], tmp_files['ks_max'], dg_files["main"], '((A>B) & True)*1']
    ]

    # Produce final "1" / "0" raster for each layer
    # iterate over the list above
    # CreateCopy > rasterize over > calc/compress
    print("classify stand layers...")
    for column_prefix, \
            dg_lim_field, \
            dg_tmp_file_b, \
            dg_tmp_file_c, \
            dg_layer_file, \
            formula \
            in field_file_pairs:
        start_time = time.time()
        # print(dg_lim_field, "->", dg_tmp_file_b, "->", dg_layer_file)
        if (column_prefix == 'dg_'):
            # DG Layer can be created by using OS and UEB (need to be present)
            processing.run("gdal:rastercalculator", {
                'INPUT_A': dg_files["os"],
                'BAND_A': 1,
                'INPUT_B': dg_files["ueb"],
                'BAND_B': None, 'INPUT_C': None, 'BAND_C': None, 'INPUT_D': None, 'BAND_D': None, 'INPUT_E': None,
                'BAND_E': None, 'INPUT_F': None, 'BAND_F': None, 'FORMULA': 'logical_or(A, B)', 'NO_DATA': None,
                'PROJWIN': None, 'RTYPE': 0, 'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9', 'EXTRA': '',
                'OUTPUT': dg_layer_file})
        else:
            # create an empty DG layer based on vhm extents for each layer
            create_empty_copy(vhm, dg_tmp_file_b)
            # burn vector value into raster
            processing.run("gdal:rasterize_over", {
                'INPUT': stands_dg,
                'INPUT_RASTER': dg_tmp_file_b,
                'FIELD': dg_lim_field,
                'ADD': False, 'EXTRA': ''})
            # classify raster
            processing.run("gdal:rastercalculator", {
                'INPUT_A': vhm, 'BAND_A': 1,
                'INPUT_B': dg_tmp_file_b, 'BAND_B': 1,
                'INPUT_C': dg_tmp_file_c, 'BAND_C': 1,
                'INPUT_D': None, 'BAND_D': -1, 'INPUT_E': None, 'BAND_E': -1, 'INPUT_F': None, 'BAND_F': -1,
                'FORMULA': formula, 'NO_DATA': None, 'RTYPE': 0,
                'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9', 'EXTRA': '', 'OUTPUT': dg_layer_file})

        # clean up temp files as soon as possible
        if del_tmp:
            if dg_tmp_file_c is not None:
                if os.path.exists(dg_tmp_file_c):
                    delete_raster(dg_tmp_file_c)
                if os.path.exists(dg_tmp_file_c + ".aux.xml"):
                    os.remove(dg_tmp_file_c + ".aux.xml")

        end_time = time.time()
        print(f'{column_prefix}layer classification execution time: {str(timedelta(seconds=(end_time - start_time)))}')

    # Calculate DG per stand and per layer
    print("zonal statistics...")
    for column_prefix, x, x, x, dg_layer_file, x in field_file_pairs:
        start_time = time.time()

        # using the "old" zonalstatistics algorithm (not zonalstatisticsfb), that appends fields to input layer
        # for more info, read https://github.com/qgis/QGIS/issues/40356
        param = {'INPUT_RASTER': dg_layer_file, 'RASTER_BAND': 1,
                 'INPUT_VECTOR': stands_dg,
                 'COLUMN_PREFIX': column_prefix, 'STATS': [2]}
        processing.run("qgis:zonalstatistics", param)

        end_time = time.time()
        print(f'{column_prefix}layer classification execution time: {str(timedelta(seconds=(end_time - start_time)))}')

    # re-read the input, as it was modified by zonal statistics
    stands_layer = QgsVectorLayer(stands_dg, "stands", "ogr")
    with edit(stands_layer):
        # Add DG fields
        provider = stands_layer.dataProvider()
        provider.addAttributes([QgsField("DG_ks", QVariant.Int),
                                QgsField("DG_us", QVariant.Int),
                                QgsField("DG_ms", QVariant.Int),
                                QgsField("DG_os", QVariant.Int),
                                QgsField("DG_ueb", QVariant.Int),
                                QgsField("DG", QVariant.Int)])
        stands_layer.updateFields()

        # Calculate DG per stand
        for f in stands_layer.getFeatures():
            # round if is a number, copy NULL values without rounding to avoid errors
            f["DG_ks"] = round(f["dg_ks_mean"] * 100) if f["dg_ks_mean"] != core.NULL else f["dg_ks_mean"]
            f["DG_us"] = round(f["dg_us_mean"] * 100) if f["dg_us_mean"] != core.NULL else f["dg_us_mean"]
            f["DG_ms"] = round(f["dg_ms_mean"] * 100) if f["dg_ms_mean"] != core.NULL else f["dg_ms_mean"]
            f["DG_os"] = round(f["dg_os_mean"] * 100) if f["dg_os_mean"] != core.NULL else f["dg_os_mean"]
            f["DG_ueb"] = round(f["dg_ueb_mean"] * 100) if f["dg_ueb_mean"] != core.NULL else f["dg_ueb_mean"]
            f["DG"] = round(f["dg_mean"] * 100) if f["dg_mean"] != core.NULL else f["dg_mean"]

            stands_layer.updateFeature(f)

    # Delete temporary fields
    if del_tmp:
        delete_fields(stands_layer,
                      ["dg_ks_max", 'dg_ks_count', "dg_ks_mean", 'dg_ks_sum',
                       "dg_us_min", "dg_us_mean", 'dg_us_count', 'dg_us_sum',
                       "dg_ms_min", "dg_ms_mean", 'dg_ms_count', 'dg_ms_sum',
                       "dg_os_min", "dg_os_mean", 'dg_os_count', 'dg_os_sum',
                       "dg_ueb_min", "dg_ueb_mean", 'dg_ueb_count', 'dg_ueb_sum',
                       "dg_min", "dg_mean", 'dg_count', 'dg_sum',
                       "dissolve",])

    print("DONE!")

    # Add "output_dg_layer_" as a prefix to keys to improve clarity when reusing the output.
    results = {f"dg_layer_{key}": value for key, value in dg_files.items()}
    results["stands_dg"] = stands_dg

    return results
