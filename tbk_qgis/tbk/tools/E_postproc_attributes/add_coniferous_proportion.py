# *************************************************************************** #
# Add new field NH(german abreviation (Nadelholz) for coniferous) for coniferous proportion.
#
# WARNING: identical coordinate system needed!
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
import sys
import os
import shutil
from typing import Dict
from qgis import core
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant
from qgis.utils import iface
from qgis.core import QgsProject
import processing

from tbk_qgis.tbk.general.tbk_utilities import *


def add_coniferous_proportion(working_root,
                              tmp_output_folder,
                              dg_layer,
                              stands_dg_copy,
                              coniferous_raster,
                              calc_main_layer,
                              tbk_result_dir,
                              del_tmp=True):
    print("--------------------------------------------")
    print("START coniferous proportion...")

    print("loading files...")
    if coniferous_raster == 'null' or coniferous_raster == None:
        print("No coniferous raster found.")
        return

    print("calc mean coniferous proportion...")

    zonal_statistics(coniferous_raster, stands_dg_copy, 'nh_', [2])

    stands_layer_copy = QgsVectorLayer(stands_dg_copy, "stands", "ogr")

    with edit(stands_layer_copy):
        # Add NH fields
        provider = stands_layer_copy.dataProvider()
        provider.addAttributes([QgsField("NH", QVariant.Int)])
        stands_layer_copy.updateFields()

        # Write NH attribute per stand
        for f in stands_layer_copy.getFeatures():
            f["NH"] = f["nh_mean"]
            stands_layer_copy.updateFeature(f)

    # NH OS
    if calc_main_layer:
        print("calc mean coniferous proportion for main layer...")
        # dg raster layer
        # todo: variable name refers to the upper layer(os) file but the main layer file is used since at least 2023. Not sure if wanted
        dg_layer_os = dg_layer

        # minimum degree of cover to select valid 10 m NH pixels
        cover = 40
        # output raster file
        tmp_files_names = {
            "dg_layer_os_nh": "nh_os.tif",
            "dg_layer_os_1m": "dg_layer_os_1m.tif",
            "dg_layer_os_10m_sum": "dg_layer_os_10m_sum.tif",
            "dg_layer_os_10m_mask": "dg_layer_os_10m_mask.tif",
        }

        # Dictionary containing the path to temp files
        tmp_files = {key: os.path.join(tmp_output_folder, filename) for key, filename in tmp_files_names.items()}

        # Resample os layer to 1m to align with 10m raster
        param = {'INPUT': dg_layer_os, 'SOURCE_CRS': None, 'TARGET_CRS': None, 'RESAMPLING': 1, 'NODATA': None,
                 'TARGET_RESOLUTION': 1, 'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9', 'DATA_TYPE': 0,
                 'TARGET_EXTENT': None, 'TARGET_EXTENT_CRS': None, 'MULTITHREADING': False, 'EXTRA': '',
                 'OUTPUT': tmp_files["dg_layer_os_1m"]}
        algoOutput = processing.run("gdal:warpreproject", param)

        # Aggregate os sum per 10m Sentinel-2 pixel
        meta_data = get_raster_metadata(coniferous_raster)
        extent = "{0},{1},{2},{3} [EPSG:{4}]".format(meta_data["extent"][0],
                                                     meta_data["extent"][2],
                                                     meta_data["extent"][1],
                                                     meta_data["extent"][3],
                                                     meta_data["epsg"])

        param = {'input': tmp_files["dg_layer_os_1m"], 'method': 8, 'quantile': 0.5, '-n': False, '-w': False,
                 'output': tmp_files["dg_layer_os_10m_sum"],
                 'GRASS_REGION_PARAMETER': extent, 'GRASS_REGION_CELLSIZE_PARAMETER': 10, 'GRASS_RASTER_FORMAT_OPT': '',
                 'GRASS_RASTER_FORMAT_META': ''}
        algoOutput = processing.run("grass7:r.resamp.stats", param)

        meta_data = get_raster_metadata(dg_layer_os)
        param = {'INPUT': tmp_files["dg_layer_os_10m_sum"],
                 'CRS': QgsCoordinateReferenceSystem('EPSG:{0}'.format(meta_data["epsg"]))}
        processing.run("gdal:assignprojection", param)

        # Reclassify
        condition_string = "(A > {0})*1".format(str(cover))
        param = {'INPUT_A': tmp_files["dg_layer_os_10m_sum"], 'BAND_A': 1,
                 'INPUT_B': None, 'BAND_B': -1,
                 'INPUT_C': None, 'BAND_C': -1,
                 'INPUT_D': None, 'BAND_D': -1,
                 'INPUT_E': None, 'BAND_E': -1,
                 'INPUT_F': None, 'BAND_F': -1,
                 'FORMULA': condition_string, 'NO_DATA': None, 'RTYPE': 0,
                 'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9', 'EXTRA': '',
                 'OUTPUT': tmp_files["dg_layer_os_10m_mask"]}
        processing.run("gdal:rastercalculator", param)

        # Extract pixels covered by OS
        formula = "A*B"
        param = {'INPUT_A': coniferous_raster, 'BAND_A': 1,
                 'INPUT_B': tmp_files["dg_layer_os_10m_mask"], 'BAND_B': 1,
                 'INPUT_C': None, 'BAND_C': -1,
                 'INPUT_D': None, 'BAND_D': -1,
                 'INPUT_E': None, 'BAND_E': -1,
                 'INPUT_F': None, 'BAND_F': -1,
                 'FORMULA': formula, 'NO_DATA': None, 'RTYPE': 0,
                 'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9', 'EXTRA': '',
                 'OUTPUT': tmp_files["dg_layer_os_nh"]}
        processing.run("gdal:rastercalculator", param)

        # Calculate mean NH_OS
        zonal_statistics(tmp_files["dg_layer_os_nh"], stands_dg_copy, 'nh_os_', [2])

        # Calculate sum NH_OS pixels
        zonal_statistics(tmp_files["dg_layer_os_10m_mask"], stands_dg_copy, 'nhm_', [1])

        with edit(stands_layer_copy):
            # Add NH fields
            provider = stands_layer_copy.dataProvider()
            provider.addAttributes([QgsField("NH_OS", QVariant.Int),
                                    QgsField("NH_OS_PIX", QVariant.Int)])
            stands_layer_copy.updateFields()

            # Write NH_OS attribute per stand
            for f in stands_layer_copy.getFeatures():
                # todo: It looks like NH_OS_PIX field is not necessary. we could do:
                #  if f["NH_OS_PIX"] > 0:
                #  f["NH_OS"] = f["nh_os_mean"]...
                f["NH_OS_PIX"] = f["nhm_sum"]
                if f["NH_OS_PIX"] > 0:
                    f["NH_OS"] = f["nh_os_mean"]
                else:
                    # set value to -1 if no NH_OS pixels
                    f["NH_OS"] = -1
                stands_layer_copy.updateFeature(f)

        # Delete tmp files and fields
        if del_tmp:
            delete_fields(stands_layer_copy, ['nh_count', "nh_mean", 'nh_sum',
                                              'nhm_count', 'nhm_mean', "nhm_sum",
                                              'nh_os_count', "nh_os_mean", 'nh_os_sum',
                                              'NH_OS_PIX'])

            delete_raster(tmp_files["dg_layer_os_1m"])
            delete_raster(tmp_files["dg_layer_os_10m_sum"])
            delete_raster(tmp_files["dg_layer_os_nh"])
            delete_raster(tmp_files["dg_layer_os_10m_mask"])

    print("DONE!")
    return stands_dg_copy


def zonal_statistics(input_raster: str, input_vector: str, column_prefix: str, stats: list, rasterband=1) -> Dict:
    """
    For the statistics: 0=count, 1=sum, 2=mean
    """
    return processing.run("qgis:zonalstatistics", {
        'INPUT_RASTER': input_raster,
        'RASTER_BAND': rasterband,
        'INPUT_VECTOR': input_vector,
        'COLUMN_PREFIX': column_prefix,
        'STATISTICS': stats})
