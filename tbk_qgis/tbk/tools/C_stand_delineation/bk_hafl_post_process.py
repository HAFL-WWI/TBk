# *************************************************************************** #
# Post processing of the "raw" TBk classification.
# Steps: Eliminate -> simplify -> eliminate -> calculate remainder values
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



# Import system modules

import processing

from tbk_qgis.tbk.general.tbk_utilities import *


def post_process(working_root, shape_in, h_max_input, shape_out, tmp_output_folder, min_area, simplification_tolerance=8, del_tmp=True):
    # -------- INIT -------#
    print("--------------------------------------------")
    print("START post processing...")

    # TBk folder path
    workspace = working_root

    # Expression to eliminate small polygons
    expression = "area_m2 < " + str(min_area)

    # Expression to calculate area m2
    eArea = "{0}".format("to_int(area($geometry))")

    # File names
    tmp_stands_buf = "tmp_stand_boundaries_buf0.gpkg"
    tmp_reduced = "tmp_reduced.gpkg"
    tmp_simplified = "tmp_simplified.gpkg"
    tmp_simplified_error = "tmp_simplified_error.gpkg"

    highest_point_out = "stands_highest_tree_tmp.gpkg"

    ########################################
    # --- Vectorize highest trees

    params = {'INPUT_RASTER': h_max_input, 'RASTER_BAND': 1, 'FIELD_NAME': 'VALUE',
              'OUTPUT': 'TEMPORARY_OUTPUT'}
    algoOutput = processing.run("native:pixelstopoints", params)

    highest_point_path = os.path.join(tmp_output_folder, highest_point_out)
    params = {'INPUT': algoOutput["OUTPUT"], 'FIELD': 'VALUE', 'OPERATOR': 2, 'VALUE': '0',
              'OUTPUT': highest_point_path}
    algoOutput = processing.run("native:extractbyattribute", params)

    ########################################
    # --- Eliminate small polygons

    # Create tmp layer
    stand_boundaries_path = os.path.join(working_root, shape_in)
    tmp_stands_buf_path = os.path.join(tmp_output_folder, tmp_stands_buf)

    params = {'INPUT': stand_boundaries_path, 'DISTANCE': 0, 'SEGMENTS': 5, 'END_CAP_STYLE': 0, 'JOIN_STYLE': 0,
              'MITER_LIMIT': 2, 'DISSOLVE': False, 'OUTPUT': tmp_stands_buf_path}
    algoOutput = processing.run("native:buffer", params)

    stand_boundaries_layer = QgsVectorLayer(tmp_stands_buf_path, "stand_boundaries", "ogr")
    # Execute SelectLayerByAttribute to define features to be eliminated
    print("selecting small polygons...")
    stand_boundaries_layer.selectByExpression(expression)

    # Execute Eliminate
    print("eliminating small polygons...")

    tmp_reduced_path = os.path.join(tmp_output_folder, tmp_reduced)

    # Does not persist results when writing directly to file
    param = {'INPUT': stand_boundaries_layer, 'MODE': 2, 'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:eliminateselectedpolygons", param)

    ctc = QgsProject.instance().transformContext()
    QgsVectorFileWriter.writeAsVectorFormatV3(algoOutput['OUTPUT'], tmp_reduced_path, ctc,
                                              getVectorSaveOptions('GPKG', 'utf-8'))
    # QgsVectorFileWriter.writeAsVectorFormatV3(algoOutput['OUTPUT'],tmp_reduced_path,"utf-8",stand_boundaries_layer.sourceCrs(),"GPKG")

    ########################################
    # --- Simplify
    print("simplifying polygons...")
    tmp_simplified_path = os.path.join(tmp_output_folder, tmp_simplified)
    tmp_simplified_error_path = os.path.join(tmp_output_folder, tmp_simplified_error)

    param = {'input': tmp_reduced_path, 'type': [0, 1, 2], 'cats': '', 'where': '', 'method': 0,
             'threshold': simplification_tolerance, 'look_ahead': 7, 'reduction': 50, 'slide': 0.5, 'angle_thresh': 3,
             'degree_thresh': 0, 'closeness_thresh': 0, 'betweeness_thresh': 0, 'alpha': 1, 'beta': 1, 'iterations': 1,
             '-t': False, '-l': True, 'output': 'TEMPORARY_OUTPUT', 'error': tmp_simplified_error_path,
             'GRASS_REGION_PARAMETER': None, 'GRASS_SNAP_TOLERANCE_PARAMETER': -1, 'GRASS_MIN_AREA_PARAMETER': 0.0001,
             'GRASS_OUTPUT_TYPE_PARAMETER': 0, 'GRASS_VECTOR_DSCO': '', 'GRASS_VECTOR_LCO': ''}
    algoOutput = processing.run("grass7:v.generalize", param)

    # a second simplify pass, since the first pass leaves some stands unchanged
    param = {'input': algoOutput['output'], 'type': [0, 1, 2], 'cats': '', 'where': '', 'method': 0,
             'threshold': simplification_tolerance, 'look_ahead': 7, 'reduction': 50, 'slide': 0.5, 'angle_thresh': 3,
             'degree_thresh': 0, 'closeness_thresh': 0, 'betweeness_thresh': 0, 'alpha': 1, 'beta': 1, 'iterations': 1,
             '-t': False, '-l': True, 'output': tmp_simplified_path, 'error': tmp_simplified_error_path,
             'GRASS_REGION_PARAMETER': None, 'GRASS_SNAP_TOLERANCE_PARAMETER': -1, 'GRASS_MIN_AREA_PARAMETER': 0.0001,
             'GRASS_OUTPUT_TYPE_PARAMETER': 0, 'GRASS_VECTOR_DSCO': '', 'GRASS_VECTOR_LCO': ''}
    algoOutput = processing.run("grass7:v.generalize", param)

    tmp_simplified_layer = QgsVectorLayer(tmp_simplified_path, "stand_boundaries_reduced", "ogr")

    # Delete unimportant fields
    # apparently these are some dummy fields created by grass
    fields = ['cat', 'cat_', 'foo']
    delete_fields(tmp_simplified_layer, fields)

    ########################################
    # --- Recalculate area
    print("recalculating area...")
    param = {'INPUT': tmp_simplified_path, 'OUTPUT': 'memory:'}
    algoOutput = processing.run("native:fixgeometries", param)

    param = {'INPUT': algoOutput['OUTPUT'], 'FIELD_NAME': 'area_m2', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10,
             'FIELD_PRECISION': 3, 'NEW_FIELD': False, 'FORMULA': eArea, 'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:fieldcalculator", param)

    del tmp_simplified_layer

    QgsVectorFileWriter.writeAsVectorFormatV3(algoOutput['OUTPUT'], tmp_simplified_path, ctc,
                                              getVectorSaveOptions('GPKG', 'utf-8'))

    ########################################
    # --- Redo elimination of small polygons

    # sometimes the first pass doesn't eliminate everything
    # and simplification also alters polygon area

    # Create tmp layer
    tmp_simplified_layer = QgsVectorLayer(tmp_simplified_path, "stand_boundaries_simplified", "ogr")
    # Execute SelectLayerByAttribute to define features to be eliminated
    print("selecting small polygons...")
    tmp_simplified_layer.selectByExpression(expression)

    # Execute Eliminate
    print("eliminating small polygons...")

    # Does not persist results when writing directly to file
    param = {'INPUT': tmp_simplified_layer, 'MODE': 2, 'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:eliminateselectedpolygons", param)

    QgsVectorFileWriter.writeAsVectorFormatV3(algoOutput['OUTPUT'], tmp_reduced_path, ctc,
                                              getVectorSaveOptions('GPKG', 'utf-8'))

    ########################################
    # --- Recalculate area
    print("recalculating area...")
    param = {'INPUT': algoOutput['OUTPUT'], 'FIELD_NAME': 'area_m2', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10,
             'FIELD_PRECISION': 3, 'NEW_FIELD': False, 'FORMULA': eArea, 'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:fieldcalculator", param)

    del tmp_simplified_layer
    # QgsVectorFileWriter.writeAsVectorFormatV3(algoOutput['OUTPUT'],tmp_simplified_path,ctc,getVectorSaveOptions('GPKG','utf-8'))

    ########################################
    # --- Update hmax and hdom for remainders
    print("filling in hmax and hdom for remainders...")
    # Create tmp layer
    # tmp_simplified_layer = QgsVectorLayer(tmp_simplified_path, "stand_boundaries_simplified", "ogr")
    tmp_simplified_layer = algoOutput['OUTPUT']

    # Select remainders and calculate hmax, hdom
    param = {'INPUT': tmp_simplified_layer, 'FIELD': 'type', 'OPERATOR': 0, 'VALUE': 'remainder', 'METHOD': 0}
    algoOutput = processing.run("qgis:selectbyattribute", param)

    # update hmax attribute (with value of hmax_eff) for selected stands
    param = {'INPUT': algoOutput['OUTPUT'], 'FIELD_NAME': 'hmax', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10,
             'FIELD_PRECISION': 3, 'NEW_FIELD': False, 'FORMULA': 'if(is_selected(),hmax_eff,hmax)',
             'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:fieldcalculator", param)

    # Select remainders and calculate hmax, hdom
    param = {'INPUT': algoOutput['OUTPUT'], 'FIELD': 'type', 'OPERATOR': 0, 'VALUE': 'remainder', 'METHOD': 0}
    algoOutput = processing.run("qgis:selectbyattribute", param)

    # update hmax attribute (with value of hp_80) for selected stands
    param = {'INPUT': algoOutput['OUTPUT'], 'FIELD_NAME': 'hdom', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10,
             'FIELD_PRECISION': 3, 'NEW_FIELD': False, 'FORMULA': 'if(is_selected(),hp80,hdom)', 'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:fieldcalculator", param)

    # Delete fields
    fields = ['hmax_eff', 'hp80']
    if del_tmp:
        delete_fields(algoOutput['OUTPUT'], fields)

    ########################################
    # # create Field "FID_orig"
    # # Prepare for further analysis of neighbours
    # param = {'INPUT': algoOutput['OUTPUT'], 'FIELD_NAME': 'FID_orig', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 10,
    #          'FIELD_PRECISION': 0, 'OUTPUT': 'memory:'}
    # algoOutput = processing.run("qgis:addfieldtoattributestable", param)
    # ##May be the wrong field!
    # param = {'INPUT': algoOutput['OUTPUT'], 'FIELD_NAME': 'FID_orig', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10,
    #          'FIELD_PRECISION': 3, 'NEW_FIELD': False, 'FORMULA': 'OBJECTID', 'OUTPUT': 'memory:'}
    # algoOutput = processing.run("qgis:fieldcalculator", param)

    ########################################

    # finally persist output
    shape_out_path = os.path.join(working_root, shape_out)
    result = QgsVectorFileWriter.writeAsVectorFormatV3(algoOutput['OUTPUT'], shape_out_path, ctc,
                                              getVectorSaveOptions('GPKG', 'utf-8'))
    new_layer_path = result[2]

    # Delete files
    if del_tmp:
        delete_shapefile(tmp_simplified_path)
        delete_shapefile(tmp_simplified_error_path)
        delete_shapefile(tmp_reduced_path)
        delete_shapefile(tmp_stands_buf_path)

    print("DONE!")

    # Return final result
    return new_layer_path
