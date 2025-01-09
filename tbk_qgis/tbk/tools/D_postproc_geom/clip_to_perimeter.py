# *************************************************************************** #
# Postprocessing: Clip stand shapefile to exact perimeter and fill gaps.
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

from tbk_qgis.tbk.general.tbk_utilities import *


def clip_to_perimeter(working_root, stands_to_clip_path, stands_clipped_path, tmp_output_folder, perimeter,
                      del_tmp=True):
    print("--------------------------------------------")
    print("START Clip to perimeter...")

    # stands_merged_path = os.path.join(working_root,"stands_merged.gpkg")
    # stands_clip_path = os.path.join(tmp_output_folder,"stands_clip_tmp.gpkg")

    # Clip to forest mask
    param = {'INPUT': stands_to_clip_path, 'OVERLAY': perimeter, 'OUTPUT': 'TEMPORARY_OUTPUT'}
    algOutput = processing.run("native:clip", param)

    # Convert multipart to singlepart
    algOutput = processing.run("native:multiparttosingleparts",
                               {'INPUT': algOutput['OUTPUT'], 'OUTPUT': stands_clipped_path})

    # Clip highest trees
    highest_point_path = os.path.join(tmp_output_folder, "stands_highest_tree_tmp.gpkg")
    highest_point_clip_path = os.path.join(working_root, "stands_highest_tree.gpkg")
    param = {'INPUT': highest_point_path, 'OVERLAY': perimeter, 'OUTPUT': highest_point_clip_path}
    algoOutput = processing.run("native:clip", param)

    if del_tmp:
        delete_shapefile(highest_point_path)
        delete_geopackage(highest_point_path)

    return stands_clipped_path


def clip_vhm_to_perimeter(working_root, tmp_output_folder, vhm_input, perimeter, vhm_output_name):
    print("--------------------------------------------")
    print("START Clip VHM to perimeter...")

    # Clip to forest mask
    vhm_clipped_path = os.path.join(working_root, vhm_output_name)

    param = {'INPUT': vhm_input, 'MASK': perimeter, 'SOURCE_CRS': None, 'TARGET_CRS': None, 'NODATA': None,
             'ALPHA_BAND': False, 'CROP_TO_CUTLINE': True, 'KEEP_RESOLUTION': False,
             'SET_RESOLUTION': False, 'X_RESOLUTION': 0, 'Y_RESOLUTION': 0, 'MULTITHREADING': False,
             'OPTIONS': '', 'DATA_TYPE': 0,
             'EXTRA': '-multi -wm 5000 -co COMPRESS=LZW -co TILED=YES -co BIGTIFF=YES  -wo \"CUTLINE_ALL_TOUCHED=TRUE\"',
             'OUTPUT': vhm_clipped_path}
    processing.run("gdal:cliprasterbymasklayer", param)

    return vhm_clipped_path


def eliminate_gaps(working_root, in_shape_path, output_shape_path, tmp_output_folder, perimeter, del_tmp=True):
    '''
    Align tbk shapefile to perimeter (for example Waldmaske AV).
    Idea: If small gaps remain between a defined perimeter and the
    stands shapefile. They need to be merged with the neighboring stand to
    exactly match the perimeter and therefore remove small gap
    '''

    print("--------------------------------------------")
    print("START Eliminate gaps...")

    # TBk folder path
    workspace = working_root
    scratchWorkspace = working_root

    # Perimeter
    perimeter_shape = perimeter

    # File names
    # in_shape_path = os.path.join(tmp_output_folder,"stands_clip_tmp.gpkg")
    # output_shape_path = os.path.join(working_root,"stands_clipped.gpkg")
    gaps_tmp_path = os.path.join(tmp_output_folder, "gaps_tmp.gpkg")
    gaps_single_tmp_path = os.path.join(tmp_output_folder, "gaps_single_tmp.gpkg")
    union_tmp_path = os.path.join(tmp_output_folder, "stands_gaps_union_tmp.gpkg")
    union_tmp_buf_path = os.path.join(tmp_output_folder, "stands_gaps_union_tmp_buf0.gpkg")

    ########################################
    # Find gaps
    print("finding gaps...")
    param = {'INPUT': perimeter_shape, 'OVERLAY': in_shape_path, 'OUTPUT': gaps_tmp_path}
    algoOutput = processing.run("native:difference", param)

    ########################################
    # Transform gaps to single part
    print("transform gaps to single part")
    param = {'INPUT': gaps_tmp_path, 'OUTPUT': gaps_single_tmp_path}
    algoOutput = processing.run("native:multiparttosingleparts", param)

    ########################################
    # Union with stand layer
    # todo remove Union and replace with a different workflow
    print("union gaps with stands...")
    processing.ProcessingConfig.setSettingValue('FILTER_INVALID_GEOMETRIES', 1)
    param = {'INPUT': in_shape_path, 'OVERLAY': gaps_single_tmp_path, 'OVERLAY_FIELDS_PREFIX': '',
             'OUTPUT': union_tmp_path}
    algoOutput = processing.run("native:union", param)
    processing.ProcessingConfig.setSettingValue('FILTER_INVALID_GEOMETRIES', 2)

    params = {'INPUT': union_tmp_path, 'DISTANCE': 0, 'SEGMENTS': 5, 'END_CAP_STYLE': 0, 'JOIN_STYLE': 0,
              'MITER_LIMIT': 2, 'DISSOLVE': False, 'OUTPUT': union_tmp_buf_path}
    algoOutput = processing.run("native:buffer", params)

    ########################################
    # Eliminate gaps
    print("eliminate gaps...")
    expression = 'ID IS NULL AND to_int(area($geometry))>0'

    union_layer = QgsVectorLayer(union_tmp_path, "union_tmp", "ogr")
    union_layer.selectByExpression(expression)

    # TODO Does not persist results when writing directly to file
    param = {'INPUT': union_layer, 'MODE': 2, 'OUTPUT': 'TEMPORARY_OUTPUT'}
    algoOutput = processing.run("qgis:eliminateselectedpolygons", param)

    ctc = QgsProject.instance().transformContext()
    QgsVectorFileWriter.writeAsVectorFormatV3(algoOutput['OUTPUT'], output_shape_path, ctc,
                                              getVectorSaveOptions('GPKG', 'utf-8'))

    ########################################
    # Delete gaps not possible to eliminate
    print("delete remaining gaps completely...")
    expression = 'ID IS NULL OR to_int(area($geometry))=0'

    # Delete Fields and keep only major ones
    fields_to_delete = ["ID_2", "GRIDCODE", "FID_stands", "FID_gaps_s", "Id_1", "ORIG_FID"]
    fields_to_keep = ["OBJECTID", "area_m2", "hmax_eff", "hp80", "FID_orig", "ID", "hmax", "hdom", "type"]

    out_layer = QgsVectorLayer(output_shape_path, "union_tmp", "ogr")
    prov = out_layer.dataProvider()
    for field in prov.fields():
        if not field.name() in fields_to_keep:
            fields_to_delete.append(field.name())

    out_layer.selectByExpression(expression)
    if len(out_layer.selectedFeatureIds()) > 0:
        with edit(out_layer):
            out_layer.deleteSelectedFeatures()

    # Delete fields
    delete_fields(out_layer, fields_to_delete)

    print("DONE!")

    # Delete layers
    if del_tmp:
        delete_shapefile(union_tmp_buf_path)
        delete_shapefile(gaps_single_tmp_path)
        delete_shapefile(gaps_tmp_path)
        delete_shapefile(union_tmp_path)
        delete_shapefile(in_shape_path)

    return output_shape_path