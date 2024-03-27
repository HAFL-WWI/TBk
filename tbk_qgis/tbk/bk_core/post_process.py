######################################################################
# Post processing of the "raw" TBk classification.
# Steps: Eliminate -> simplify -> eliminate -> calculate remainder values
#
# (C) Dominique Weber, Christoph Schaller,  HAFL, BFH
######################################################################

# Import system modules

from qgis import core
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant
from qgis.utils import iface
from qgis.core import QgsProject
import processing
import os
from qgis.core import *

from tbk_qgis.tbk.utility.tbk_utilities import *


def post_process(tbk_path, min_area, simplification_tolerance=8, del_tmp=True):
    # -------- INIT -------#
    print("--------------------------------------------")
    print("START post processing...")

    # TBk folder path
    workspace = tbk_path
    scratchWorkspace = tbk_path

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
    neighbors_out = "neighbors"

    highest_raster_in = "hmax.tif"
    highest_point_out = "stands_highest_tree_tmp.gpkg"

    ########################################
    # Vectorize highest trees
    highest_raster_path = os.path.join(workspace, highest_raster_in)
    print(highest_raster_path)

    params = {'INPUT_RASTER': highest_raster_path, 'RASTER_BAND': 1, 'FIELD_NAME': 'VALUE',
              'OUTPUT': 'TEMPORARY_OUTPUT'}
    algoOutput = processing.run("native:pixelstopoints", params)

    highest_point_path = os.path.join(workspace, highest_point_out)
    params = {'INPUT': algoOutput["OUTPUT"], 'FIELD': 'VALUE', 'OPERATOR': 2, 'VALUE': '0',
              'OUTPUT': highest_point_path}
    algoOutput = processing.run("native:extractbyattribute", params)

    ########################################
    # Eliminate small polygons

    # Create tmp layer
    stand_boundaries_path = os.path.join(workspace, shape_in)
    tmp_stands_buf_path = os.path.join(workspace, tmp_stands_buf)

    params = {'INPUT': stand_boundaries_path, 'DISTANCE': 0, 'SEGMENTS': 5, 'END_CAP_STYLE': 0, 'JOIN_STYLE': 0,
              'MITER_LIMIT': 2, 'DISSOLVE': False, 'OUTPUT': tmp_stands_buf_path}
    algoOutput = processing.run("native:buffer", params)

    stand_boundaries_layer = QgsVectorLayer(tmp_stands_buf_path, "stand_boundaries", "ogr")
    # Execute SelectLayerByAttribute to define features to be eliminated
    print("selecting small polygons...")
    stand_boundaries_layer.selectByExpression(expression)

    # Execute Eliminate
    print("eliminating small polygons...")

    tmp_reduced_path = os.path.join(workspace, tmp_reduced)

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
    # tmp_smoothed_path = os.path.join(workspace,tmp_smoothed)
    # tmp_smoothed_error_path = os.path.join(workspace,tmp_smoothed_error)

    # param = {'input':tmp_reduced_path,'type':[0,1,2],'cats':'','where':'','method':8,'threshold':0.1,'look_ahead':7,'reduction':50,'slide':0.5,'angle_thresh':3,'degree_thresh':0,'closeness_thresh':0,'betweeness_thresh':0,'alpha':1,'beta':1,'iterations':1,'-t':False,'-l':True,'output':tmp_smoothed_path,'error':tmp_smoothed_error_path,'GRASS_REGION_PARAMETER':None,'GRASS_SNAP_TOLERANCE_PARAMETER':-1,'GRASS_MIN_AREA_PARAMETER':0.0001,'GRASS_OUTPUT_TYPE_PARAMETER':0,'GRASS_VECTOR_DSCO':'','GRASS_VECTOR_LCO':''}
    # algoOutput = processing.run("grass7:v.generalize", param)

    # print("simplifying polygons...")
    # tmp_simplified_path = os.path.join(workspace,tmp_simplified)
    # tmp_simplified_error_path = os.path.join(workspace,tmp_simplified_error)

    # param = {'input':tmp_smoothed_path,'type':[0,1,2],'cats':'','where':'','method':0,'threshold':7,'look_ahead':7,'reduction':50,'slide':0.5,'angle_thresh':3,'degree_thresh':0,'closeness_thresh':0,'betweeness_thresh':0,'alpha':1,'beta':1,'iterations':1,'-t':False,'-l':True,'output':tmp_simplified_path,'error':tmp_simplified_error_path,'GRASS_REGION_PARAMETER':None,'GRASS_SNAP_TOLERANCE_PARAMETER':-1,'GRASS_MIN_AREA_PARAMETER':0.0001,'GRASS_OUTPUT_TYPE_PARAMETER':0,'GRASS_VECTOR_DSCO':'','GRASS_VECTOR_LCO':''}
    # algoOutput = processing.run("grass7:v.generalize", param)

    # tmp_simplified_layer = iface.addVectorLayer(tmp_simplified_path, "tmp_simplified", "ogr")

    print("simplifying polygons...")
    tmp_simplified_path = os.path.join(workspace, tmp_simplified)
    tmp_simplified_error_path = os.path.join(workspace, tmp_simplified_error)

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
    # Prepare for further analysis of neighbors
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

    shape_out_path = os.path.join(workspace, shape_out)
    QgsVectorFileWriter.writeAsVectorFormatV3(mLayer, shape_out_path, ctc,
                                              getVectorSaveOptions('GPKG', 'utf-8'))

    # print("write neighbors TXT...")
    # # arcpy.PolygonNeighbors_analysis(shape_out, "neighbors.txt", in_fields="FID;ID;hdom;type;area_m2", area_overlap="NO_AREA_OVERLAP", both_sides="BOTH_SIDES", cluster_tolerance="-1 Unknown", out_linear_units="METERS", out_area_units="SQUARE_METERS")

    # param = {'INPUT':shape_out_path,'JOIN':shape_out_path,'PREDICATE':[0],'JOIN_FIELDS':['ID','hmax','hdom','type','area_m2','FID_orig'],'METHOD':0,'DISCARD_NONMATCHING':False,'PREFIX':'nbr_','OUTPUT':'memory:'}
    # algoOutput = processing.run("qgis:joinattributesbylocation", param)
    # mLayer = algoOutput['OUTPUT']
    # mLayer.selectByExpression("FID_orig = nbr_FID_orig")
    # ids = mLayer.selectedFeatureIds()
    # mLayer.dataProvider().deleteFeatures(ids)

    # fields = ['ID','hmax','hdom','type','area_m2','FID_orig']
    # for name in fields:
    #     findex = mLayer.dataProvider().fieldNameIndex(name)
    #     if findex != -1:
    #         mLayer.dataProvider().renameAttributes({findex: "src_"+name})
    #         mLayer.updateFields()

    # neighbors_path = os.path.join(workspace,neighbors_out) 
    # QgsVectorFileWriter.writeAsVectorFormatV3(mLayer,neighbors_path,ctc,getVectorSaveOptions('CSV','utf-8'))

    ########################################
    # Approximate the arcpy Neighbors tool
    # Code basing on https://www.qgistutorials.com/en/docs/find_neighbor_polygons.html

    print("write neighbors TXT...")
    #    arcpy.PolygonNeighbors_analysis(shape_out, "neighbors.txt", in_fields="FID;ID;hdom;type;area_m2", area_overlap="NO_AREA_OVERLAP", both_sides="BOTH_SIDES", cluster_tolerance="-1 Unknown", out_linear_units="METERS", out_area_units="SQUARE_METERS")

    neighbors_path = os.path.join(workspace, neighbors_out)
    # Create memory layer
    neighborLayer = QgsVectorLayer('None', 'Neighbors', 'memory')

    simplified_layer = QgsVectorLayer(shape_out_path, "stand_boundaries_simplified", "ogr")
    # QgsProject.instance().addMapLayer(simplified_layer)

    # Create a dictionary of all features
    feature_dict = {f.id(): f for f in simplified_layer.getFeatures()}

    # Build a spatial index
    index = QgsSpatialIndex()
    for f in feature_dict.values():
        index.addFeature(f)

    neighbors_tmp = []

    # Loop through all features and find features that touch each feature
    for f in feature_dict.values():
        geom = f.geometry()

        oid = -1
        src_FID = f["OBJECTID"]
        src_ID = f["OBJECTID"]
        src_hdom = f["hdom"]
        src_type = f["type"]
        src_area_m2 = f["area_m2"]
        node_count = -1

        # Find all features that intersect the bounding box of the current feature.
        # We use spatial index to find the features intersecting the bounding box
        # of the current feature. This will narrow down the features that we need
        # to check neighboring features.
        intersecting_ids = index.intersects(geom.boundingBox())

        for intersecting_id in intersecting_ids:
            # Look up the feature from the dictionary
            intersecting_f = feature_dict[intersecting_id]

            # For our purpose we consider a feature as 'neighbor' if it touches or
            # intersects a feature. We use the 'disjoint' predicate to satisfy
            # these conditions. So if a feature is not disjoint, it is a neighbor.
            if (f != intersecting_f and
                    not intersecting_f.geometry().disjoint(geom)):
                nbr_FID = intersecting_f["OBJECTID"]
                nbr_ID = intersecting_f["OBJECTID"]
                nbr_hdom = intersecting_f["hdom"]
                nbr_type = intersecting_f["type"]
                nbr_area_m2 = intersecting_f["area_m2"]
                lngth = -1
                if (intersecting_f.geometry().touches(geom) or intersecting_f.geometry().intersects(geom)):
                    isct = intersecting_f.geometry().intersection(geom)
                    lngth = isct.length()
                # Add a feature with attributes (and without geometry) to populate the 3 fields

                # print([objectid,src_FID, nbr_FID, src_ID, nbr_ID, src_hdom, nbr_hdom, src_type, nbr_type, src_area_m2, nbr_area_m2, lngth, node_count])
                neighbors_tmp.append(
                    [oid, src_FID, nbr_FID, src_ID, nbr_ID, src_hdom, nbr_hdom, src_type, nbr_type, src_area_m2,
                     nbr_area_m2, lngth, node_count])

    # Begin editing memory layer and create 3 fields
    neighborLayer.startEditing()
    provider = neighborLayer.dataProvider()
    provider.addAttributes([QgsField("OID", QVariant.Int),
                            QgsField("src_FID", QVariant.Int),
                            QgsField("nbr_FID", QVariant.Int),
                            QgsField("src_ID", QVariant.Int),
                            QgsField("nbr_ID", QVariant.Int),
                            QgsField("src_hdom", QVariant.Int),
                            QgsField("nbr_hdom", QVariant.Int),
                            QgsField("src_type", QVariant.String),
                            QgsField("nbr_type", QVariant.String),
                            QgsField("src_area_m2", QVariant.Int),
                            QgsField("nbr_area_m2", QVariant.Int),
                            QgsField("LENGTH", QVariant.Double),
                            QgsField("NODE_COUNT", QVariant.Int)])
    neighborLayer.updateFields()

    for n in neighbors_tmp:
        attr = neighborLayer.dataProvider()
        feat = QgsFeature()
        # print([objectid,src_FID, nbr_FID, src_ID, nbr_ID, src_hdom, nbr_hdom, src_type, nbr_type, src_area_m2, nbr_area_m2, lngth, node_count])
        feat.setAttributes(n)
        attr.addFeatures([feat])
        # print(feat)

        neighborLayer.commitChanges()

    QgsVectorFileWriter.writeAsVectorFormatV3(neighborLayer, neighbors_path, ctc, getVectorSaveOptions('CSV', 'utf-8'))
    # QgsProject.instance().removeMapLayer(neighborLayer.id())
    # QgsProject.instance().removeMapLayer(simplified_layer.id())

    print('Processing neighbors complete.')

    # Delete files
    if del_tmp:
        delete_shapefile(tmp_simplified_path)
        delete_shapefile(tmp_simplified_error_path)
        delete_shapefile(tmp_reduced_path)
        delete_shapefile(tmp_stands_buf_path)

    print("DONE!")
