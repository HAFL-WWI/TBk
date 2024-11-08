######################################################################
# Post processing of the "raw" TBk classification.
# Steps: Eliminate -> simplify -> eliminate -> calculate remainder values
#
# (C) Dominique Weber, Christoph Schaller,  HAFL, BFH
######################################################################

# Import system modules

import processing

from tbk_qgis.tbk.general.tbk_utilities import *


def post_process(working_root, tmp_output_folder, min_area, simplification_tolerance=8, del_tmp=True):
    # -------- INIT -------#
    print("--------------------------------------------")
    print("START post processing...")

    # TBk folder path
    workspace = working_root
    scratchWorkspace = tmp_output_folder

    # Expression to eliminate small polygons
    expression = "area_m2 < " + str(min_area)

    # Expression to calculate area m2
    eArea = "{0}".format("to_int(area($geometry))")

    # File names
    shape_in = "stand_boundaries.gpkg"
    tmp_stands_buf = "tmp_stand_boundaries_buf0.gpkg"
    shape_out = "stands_simplified.gpkg"
    tmp_reduced = "tmp_reduced.gpkg"
    tmp_smoothed = "tmp_smoothed.gpkg"
    tmp_smoothed_error = "tmp_smoothed_error.gpkg"
    tmp_simplified = "tmp_simplified.gpkg"
    tmp_simplified_error = "tmp_simplified_error.gpkg"
    tempLayer = "tmp"

    highest_raster_in = "hmax.tif"
    highest_point_out = "stands_highest_tree_tmp.gpkg"

    ########################################
    # Vectorize highest trees
    highest_raster_path = os.path.join(working_root, highest_raster_in)
    print(highest_raster_path)

    params = {'INPUT_RASTER': highest_raster_path, 'RASTER_BAND': 1, 'FIELD_NAME': 'VALUE',
              'OUTPUT': 'TEMPORARY_OUTPUT'}
    algoOutput = processing.run("native:pixelstopoints", params)

    highest_point_path = os.path.join(tmp_output_folder, highest_point_out)
    params = {'INPUT': algoOutput["OUTPUT"], 'FIELD': 'VALUE', 'OPERATOR': 2, 'VALUE': '0',
              'OUTPUT': highest_point_path}
    algoOutput = processing.run("native:extractbyattribute", params)

    ########################################
    # Eliminate small polygons

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

    ##Does not persist results when writing directly to file
    param = {'INPUT': stand_boundaries_layer, 'MODE': 2, 'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:eliminateselectedpolygons", param)

    ctc = QgsProject.instance().transformContext()
    QgsVectorFileWriter.writeAsVectorFormatV3(algoOutput['OUTPUT'], tmp_reduced_path, ctc,
                                              getVectorSaveOptions('GPKG', 'utf-8'))
    # QgsVectorFileWriter.writeAsVectorFormatV3(algoOutput['OUTPUT'],tmp_reduced_path,"utf-8",stand_boundaries_layer.sourceCrs(),"GPKG")

    ########################################
    # Simplify

    # print("smoothing polygons...")
    # tmp_smoothed_path = os.path.join(tmp_output_folder,tmp_smoothed)
    # tmp_smoothed_error_path = os.path.join(tmp_output_folder,tmp_smoothed_error)

    # param = {'input':tmp_reduced_path,'type':[0,1,2],'cats':'','where':'','method':8,'threshold':0.1,'look_ahead':7,'reduction':50,'slide':0.5,'angle_thresh':3,'degree_thresh':0,'closeness_thresh':0,'betweeness_thresh':0,'alpha':1,'beta':1,'iterations':1,'-t':False,'-l':True,'output':tmp_smoothed_path,'error':tmp_smoothed_error_path,'GRASS_REGION_PARAMETER':None,'GRASS_SNAP_TOLERANCE_PARAMETER':-1,'GRASS_MIN_AREA_PARAMETER':0.0001,'GRASS_OUTPUT_TYPE_PARAMETER':0,'GRASS_VECTOR_DSCO':'','GRASS_VECTOR_LCO':''}
    # algoOutput = processing.run("grass7:v.generalize", param)

    # print("simplifying polygons...")
    # tmp_simplified_path = os.path.join(tmp_output_folder,tmp_simplified)
    # tmp_simplified_error_path = os.path.join(tmp_output_folder,tmp_simplified_error)

    # param = {'input':tmp_smoothed_path,'type':[0,1,2],'cats':'','where':'','method':0,'threshold':7,'look_ahead':7,'reduction':50,'slide':0.5,'angle_thresh':3,'degree_thresh':0,'closeness_thresh':0,'betweeness_thresh':0,'alpha':1,'beta':1,'iterations':1,'-t':False,'-l':True,'output':tmp_simplified_path,'error':tmp_simplified_error_path,'GRASS_REGION_PARAMETER':None,'GRASS_SNAP_TOLERANCE_PARAMETER':-1,'GRASS_MIN_AREA_PARAMETER':0.0001,'GRASS_OUTPUT_TYPE_PARAMETER':0,'GRASS_VECTOR_DSCO':'','GRASS_VECTOR_LCO':''}
    # algoOutput = processing.run("grass7:v.generalize", param)

    # tmp_simplified_layer = iface.addVectorLayer(tmp_simplified_path, "tmp_simplified", "ogr")

    print("simplifying polygons...")
    tmp_simplified_path = os.path.join(tmp_output_folder, tmp_simplified)
    tmp_simplified_error_path = os.path.join(tmp_output_folder, tmp_simplified_error)

    param = {'input': tmp_reduced_path, 'type': [0, 1, 2], 'cats': '', 'where': '', 'method': 0,
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
    # Recalculate area
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
    # Redo elimination of small polygons
    # because sometimes it's not possible in one GO
    # and simplification also alters polygon area

    # Create tmp layer
    tmp_simplified_layer = QgsVectorLayer(tmp_simplified_path, "stand_boundaries_simplified", "ogr")
    # Execute SelectLayerByAttribute to define features to be eliminated
    print("selecting small polygons...")
    tmp_simplified_layer.selectByExpression(expression)

    # Execute Eliminate
    print("eliminating small polygons...")

    ##Does not persist results when writing directly to file
    param = {'INPUT': tmp_simplified_layer, 'MODE': 2, 'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:eliminateselectedpolygons", param)

    QgsVectorFileWriter.writeAsVectorFormatV3(algoOutput['OUTPUT'], tmp_reduced_path, ctc,
                                              getVectorSaveOptions('GPKG', 'utf-8'))

    ########################################
    # Recalculate area
    print("recalculating area...")
    param = {'INPUT': algoOutput['OUTPUT'], 'FIELD_NAME': 'area_m2', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10,
             'FIELD_PRECISION': 3, 'NEW_FIELD': False, 'FORMULA': eArea, 'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:fieldcalculator", param)

    del tmp_simplified_layer
    # QgsVectorFileWriter.writeAsVectorFormatV3(algoOutput['OUTPUT'],tmp_simplified_path,ctc,getVectorSaveOptions('GPKG','utf-8'))

    ########################################
    # Calculate hmax and hdom for remainders
    print("calculating hmax and hdom for remainders...")
    # Create tmp layer
    # tmp_simplified_layer = QgsVectorLayer(tmp_simplified_path, "stand_boundaries_simplified", "ogr")
    tmp_simplified_layer = algoOutput['OUTPUT']

    # Select remainders and calculate hmax, hdom
    param = {'INPUT': tmp_simplified_layer, 'FIELD': 'type', 'OPERATOR': 0, 'VALUE': 'remainder', 'METHOD': 0}
    algoOutput = processing.run("qgis:selectbyattribute", param)

    param = {'INPUT': algoOutput['OUTPUT'], 'FIELD_NAME': 'hmax', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10,
             'FIELD_PRECISION': 3, 'NEW_FIELD': False, 'FORMULA': 'if(is_selected(),hmax_eff,hmax)',
             'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:fieldcalculator", param)

    param = {'INPUT': algoOutput['OUTPUT'], 'FIELD': 'type', 'OPERATOR': 0, 'VALUE': 'remainder', 'METHOD': 0}
    algoOutput = processing.run("qgis:selectbyattribute", param)

    param = {'INPUT': algoOutput['OUTPUT'], 'FIELD_NAME': 'hdom', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10,
             'FIELD_PRECISION': 3, 'NEW_FIELD': False, 'FORMULA': 'if(is_selected(),hp80,hdom)', 'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:fieldcalculator", param)

    # with edit(tmp_simplified_layer):
    #         for f in tmp_simplified_layer.getFeatures():
    #             if f['type'] == "remainder":
    #                 f['hmax'] == f['hmax_eff']
    #                 f['hdom'] == f['hp80']
    #                 tmp_simplified_layer.updateFeature(f)

    ########################################
    # Prepare for further analysis of neighbours
    param = {'INPUT': algoOutput['OUTPUT'], 'FIELD_NAME': 'FID_orig', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 10,
             'FIELD_PRECISION': 0, 'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:addfieldtoattributestable", param)
    ##May be the wrong field!
    param = {'INPUT': algoOutput['OUTPUT'], 'FIELD_NAME': 'FID_orig', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 10,
             'FIELD_PRECISION': 3, 'NEW_FIELD': False, 'FORMULA': 'OBJECTID', 'OUTPUT': 'memory:'}
    algoOutput = processing.run("qgis:fieldcalculator", param)

    # Delete fields
    mLayer = algoOutput['OUTPUT']
    fields = ['hmax_eff', 'hp80']
    if del_tmp:
        delete_fields(mLayer, fields)

    shape_out_path = os.path.join(working_root, shape_out)
    QgsVectorFileWriter.writeAsVectorFormatV3(mLayer, shape_out_path, ctc,
                                              getVectorSaveOptions('GPKG', 'utf-8'))


    # Delete files
    if del_tmp:
        delete_shapefile(tmp_simplified_path)
        delete_shapefile(tmp_simplified_error_path)
        delete_shapefile(tmp_reduced_path)
        delete_shapefile(tmp_stands_buf_path)

    print("DONE!")
