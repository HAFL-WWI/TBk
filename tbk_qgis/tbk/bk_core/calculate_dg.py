######################################################################
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
# --> Siehe auch z.B. LFI Definition: https://www.lfi.ch/publikationen/publ/LFI4_Anleitung_2017.pdf
#
# (C) Dominique Weber, Christoph Schaller,  HAFL, BFH
######################################################################

# Import arcpy module
import sys
import os

from qgis import core
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant
from qgis.utils import iface
from qgis.core import QgsProject
import processing
from datetime import timedelta
import time
from qgis.core import *

from tbk_qgis.tbk.utility.tbk_utilities import *

from osgeo import gdal


def calculate_dg(working_root, tmp_output_folder, tbk_result_dir, vhm, del_tmp=True):
    print("--------------------------------------------")
    print("START DG calculation...")



    # TBk folder path
    workspace = working_root
    scratchWorkspace = tmp_output_folder

    # Use half of the cores on the machine.
    # arcpy.env.parallelProcessingFactor = "50%"

    # TBk shapefile
    stands_shapefile = os.path.join(working_root, "stands_clipped.gpkg")

    # Create dg layer output directory
    dg_layers_dir = os.path.join(tbk_result_dir, "dg_layers")
    if not os.path.exists(dg_layers_dir):
        os.makedirs(dg_layers_dir)

    # Create tmp output directory if none is provided
    if tmp_output_folder is None:
        tmp_output_folder = os.path.join(dg_layers_dir, "tmp")
        if not os.path.exists(tmp_output_folder):
            os.makedirs(tmp_output_folder)

    # DG layers
    dg_ks_classified = os.path.join(dg_layers_dir, "dg_layer_ks.tif")
    dg_us_classified = os.path.join(dg_layers_dir, "dg_layer_us.tif")
    dg_ms_classified = os.path.join(dg_layers_dir, "dg_layer_ms.tif")
    dg_os_classified = os.path.join(dg_layers_dir, "dg_layer_os.tif")
    dg_ueb_classified = os.path.join(dg_layers_dir, "dg_layer_ueb.tif")
    dg_classified = os.path.join(dg_layers_dir, "dg_layer.tif")

    # tmp files
    tmp_lim_ks = os.path.join(tmp_output_folder, "dg_ks_max.tif")
    tmp_lim_us = os.path.join(tmp_output_folder, "dg_us_min.tif")
    tmp_lim_ms = os.path.join(tmp_output_folder, "dg_ms_min.tif")
    tmp_lim_os = os.path.join(tmp_output_folder, "dg_lim_os.tif")
    tmp_lim_ueb = os.path.join(tmp_output_folder, "dg_lim_ueb.tif")
    tmp_lim_dg = os.path.join(tmp_output_folder, "dg_lim_dg.tif")

    # Layer threshold values (based on NFI definition, www.lfi.ch)
    max_height_ks = 1.0
    min_height_us = 1.0
    min_height_hdom_factor_ms = 1.0 / 3.0
    min_height_hdom_factor_os = 2.0 / 3.0
    min_height_hmax_factor_ueb = 1.0

    ########################################################################

    stands_layer = QgsVectorLayer(stands_shapefile, "stands", "ogr")

    #
    with edit(stands_layer):
        # Add DG limits fields
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


    field_file_pairs = [
        ['dg_ueb_', 'dg_ueb_min', tmp_lim_ueb, None, dg_ueb_classified, '((A>B) & True)*1'],
        ['dg_os_', 'dg_os_min', tmp_lim_os, tmp_lim_ueb, dg_os_classified, '((A>B) & (A<=C))*1'],
        ['dg_ms_', 'dg_ms_min', tmp_lim_ms, tmp_lim_os, dg_ms_classified, '((A>B) & (A<=C))*1'],
        ['dg_us_', 'dg_us_min', tmp_lim_us, tmp_lim_ms, dg_us_classified, '((A>=B) & (A<=C))*1'],
        ['dg_ks_', 'dg_ks_max', tmp_lim_ks, tmp_lim_us, dg_ks_classified, '((A<B) & True)*1'],
        ['dg_', 'dg_min', tmp_lim_dg, tmp_lim_ks, dg_classified, '((A>B) & True)*1']
    ]

    # Produce final "1" / "0" raster for each layer
    print("classify stand layers...")
    # CreateCopy > rasterize over > calc/compress
    for column_prefix, \
            dg_lim_field, \
            dg_tmp_file_B, \
            dg_tmp_file_C, \
            dg_layer_file, \
            formula \
            in field_file_pairs:
        start_time = time.time()
        # print(dg_lim_field, "->", dg_tmp_file_B, "->", dg_layer_file)
        if (column_prefix == 'dg_'):
            # DG Layer can be created by using OS and UEB
            processing.run("gdal:rastercalculator", {
                'INPUT_A': dg_os_classified,
                'BAND_A': 1,
                'INPUT_B': dg_ueb_classified,
                'BAND_B': None, 'INPUT_C': None, 'BAND_C': None, 'INPUT_D': None, 'BAND_D': None, 'INPUT_E': None,
                'BAND_E': None, 'INPUT_F': None, 'BAND_F': None, 'FORMULA': 'logical_or(A, B)', 'NO_DATA': None,
                'PROJWIN': None, 'RTYPE': 0, 'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9', 'EXTRA': '',
                'OUTPUT': dg_layer_file})
        else:
            # create an empty DG layer based on vhm extents for each layer
            create_empty_copy(vhm, dg_tmp_file_B)
            # burn vector value into raster
            processing.run("gdal:rasterize_over", {
                'INPUT': stands_shapefile,
                'INPUT_RASTER': dg_tmp_file_B,
                'FIELD': dg_lim_field,
                'ADD': False, 'EXTRA': ''})
            # classify raster
            processing.run("gdal:rastercalculator", {
                'INPUT_A': vhm, 'BAND_A': 1,
                'INPUT_B': dg_tmp_file_B, 'BAND_B': 1,
                'INPUT_C': dg_tmp_file_C, 'BAND_C': 1,
                'INPUT_D': None, 'BAND_D': -1, 'INPUT_E': None, 'BAND_E': -1, 'INPUT_F': None, 'BAND_F': -1,
                'FORMULA': formula, 'NO_DATA': None, 'RTYPE': 0,
                'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9', 'EXTRA': '', 'OUTPUT': dg_layer_file})

        # clean up temp files as soon as possible
        if del_tmp:
            if dg_tmp_file_C is not None:
                if os.path.exists(dg_tmp_file_C):
                    delete_raster(dg_tmp_file_C)
                if os.path.exists(dg_tmp_file_C + ".aux.xml"):
                    os.remove(dg_tmp_file_C + ".aux.xml")

        end_time = time.time()
        print(f'{column_prefix}layer classification execution time: {str(timedelta(seconds=(end_time - start_time)))}')

    # Calculate DG per stand and per layer
    print("zonal statistics...")

    for column_prefix, x, x, x, dg_layer_file, x in field_file_pairs:
        start_time = time.time()
        param = {'INPUT_RASTER': dg_layer_file, 'RASTER_BAND': 1,
                 'INPUT_VECTOR': stands_shapefile,
                 'COLUMN_PREFIX': column_prefix, 'STATS': [2]}
        processing.run("qgis:zonalstatistics", param)
        end_time = time.time()
        print(f'{column_prefix}layer classification execution time: {str(timedelta(seconds=(end_time - start_time)))}')

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
                      ["dg_ks_max", "dg_us_min", "dg_ms_min", "dg_os_min", "dg_ueb_min", "dg_min", "dissolve",
                       "dg_ks_mean", "dg_us_mean", "dg_ms_mean", "dg_os_mean", "dg_ueb_mea", "dg_mean",
                       'dg_ks_coun', 'dg_ks_sum', 'dg_us_coun', 'dg_us_sum', 'dg_ms_coun', 'dg_ms_sum', 'dg_os_coun',
                       'dg_os_sum', 'dg_ueb_cou', 'dg_ueb_sum', 'dg_count', 'dg_sum',
                       ])

    print("DONE!")
