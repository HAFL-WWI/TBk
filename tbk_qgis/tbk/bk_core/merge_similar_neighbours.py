######################################################################
# Merge similar neighbouring stands
#
# (C) Dominique Weber, Christoph Schaller, HAFL, BFH
######################################################################


import os
import subprocess
import sys

from qgis import core
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant
from qgis.utils import iface
from qgis.core import QgsProject
import processing
from qgis.core import *

from tbk_qgis.tbk.utility.tbk_utilities import *

import numpy as np
import pandas as pd

def merge_similar_neighbours(working_root, tmp_output_folder, min_area_m2, min_hdom_diff_rel, del_tmp=True):
    print("--------------------------------------------")
    print("START MERGE similar neighbours...")

    # files
    shape_in_path = os.path.join(working_root,"stands_simplified.gpkg")
    shape_out_path = os.path.join(working_root,"stands_merged.gpkg")

    ######################################################################
    # TBk post-process. Prepare polygons to dissolve by specific criterias.
    # Used to combine small polygons with similar neighbours.
    ######################################################################
    print("min_area_m2: ", min_area_m2, " min_hdom_diff_rel: ", min_hdom_diff_rel)

    # load TBk shapefile
    simplified_layer = QgsVectorLayer(shape_in_path, "stand_boundaries_simplified", "ogr")
    # QgsProject.instance().addMapLayer(simplified_layer)

    ########################################
    # Approximate the arcpy Neighbours tool
    # Code basing on https://www.qgistutorials.com/en/docs/find_neighbour_polygons.html

    print("make internally used neighbours table...")

    # Create memory layer
    neighbourLayer = QgsVectorLayer('None', 'Neighbours', 'memory')

    # Create a dictionary of all features
    feature_dict = {f.id(): f for f in simplified_layer.getFeatures()}

    # Build a spatial index
    index = QgsSpatialIndex()
    for f in feature_dict.values():
        index.addFeature(f)

    neighbours_tmp = []

    # Loop through all features and find features that touch each feature
    for f in feature_dict.values():
        geom = f.geometry()

        oid = -1
        src_FID = f["OBJECTID"]
        src_hdom = f["hdom"]
        src_type = f["type"]
        src_area_m2 = f["area_m2"]
        node_count = -1

        # Find all features that intersect the bounding box of the current feature.
        # We use spatial index to find the features intersecting the bounding box
        # of the current feature. This will narrow down the features that we need
        # to check neighbouring features.
        intersecting_ids = index.intersects(geom.boundingBox())

        for intersecting_id in intersecting_ids:
            # Look up the feature from the dictionary
            intersecting_f = feature_dict[intersecting_id]

            # For our purpose we consider a feature as 'neighbour' if it touches or
            # intersects a feature. We use the 'disjoint' predicate to satisfy
            # these conditions. So if a feature is not disjoint, it is a neighbour.
            if (f != intersecting_f and
                    not intersecting_f.geometry().disjoint(geom)):
                nbr_FID = intersecting_f["OBJECTID"]
                nbr_hdom = intersecting_f["hdom"]
                nbr_type = intersecting_f["type"]
                nbr_area_m2 = intersecting_f["area_m2"]
                lngth = -1
                if (intersecting_f.geometry().touches(geom) or intersecting_f.geometry().intersects(geom)):
                    isct = intersecting_f.geometry().intersection(geom)
                    lngth = isct.length()
                # Add a feature with attributes (and without geometry) to populate the 3 fields

                # print([objectid,src_FID, nbr_FID, src_hdom, nbr_hdom, src_type, nbr_type, src_area_m2, nbr_area_m2, lngth, node_count])
                neighbours_tmp.append(
                    [oid, src_FID, nbr_FID, src_hdom, nbr_hdom, src_type, nbr_type, src_area_m2,
                     nbr_area_m2, lngth, node_count])

    # Begin editing memory layer and create 3 fields
    neighbourLayer.startEditing()
    provider = neighbourLayer.dataProvider()
    provider.addAttributes([QgsField("OID", QVariant.Int),
                            QgsField("src_FID", QVariant.Int),
                            QgsField("nbr_FID", QVariant.Int),
                            QgsField("src_hdom", QVariant.Int),
                            QgsField("nbr_hdom", QVariant.Int),
                            QgsField("src_type", QVariant.String),
                            QgsField("nbr_type", QVariant.String),
                            QgsField("src_area_m2", QVariant.Int),
                            QgsField("nbr_area_m2", QVariant.Int),
                            QgsField("LENGTH", QVariant.Double),
                            QgsField("NODE_COUNT", QVariant.Int)])
    neighbourLayer.updateFields()

    for n in neighbours_tmp:
        attr = neighbourLayer.dataProvider()
        feat = QgsFeature()
        # print([objectid,src_FID, nbr_FID, src_hdom, nbr_hdom, src_type, nbr_type, src_area_m2, nbr_area_m2, lngth, node_count])
        feat.setAttributes(n)
        attr.addFeatures([feat])
        # print(feat)

        neighbourLayer.commitChanges()

    # list all column names of table neighbourLayer
    cols = [f.name() for f in neighbourLayer.fields()]
    # print(cols)
    # a generator to yield one row at a time
    datagen = ([f[col] for col in cols] for f in neighbourLayer.getFeatures())
    # make pandas data.frame
    df = pd.DataFrame.from_records(data=datagen, columns=cols)
    # print(df.head())
    # save table neighbourLayer as .csv
    # df.to_csv(os.path.join(working_root, "neighbour.csv"), index=False)

    print('Processing neighbours complete.')

    dissolve_layer_path = os.path.join(tmp_output_folder, "stands_final_dissolve_field.gpkg")
    simplified_layer.selectAll()

    param = {'INPUT': simplified_layer,'OUTPUT': dissolve_layer_path}
    algoOutput = processing.run("native:saveselectedfeatures", param)

    del simplified_layer
     
    dissolve_layer = QgsVectorLayer(dissolve_layer_path, "stand_boundaries_simplified", "ogr")

    # select small polygons with possible neighbour to dissolve
    df["hdom_diff_rel"] = (df.src_hdom - df.nbr_hdom).abs()/df.src_hdom
    i_dissolve = ((df.src_area_m2 < min_area_m2) &
                  (df.hdom_diff_rel < min_hdom_diff_rel) &
                  (df.LENGTH > 0) &
                  (df.nbr_type == "classified"))
    df_sub = df[i_dissolve]

    # remove polygons with multiple dissolve options. Too complicate. Could for example lead to similar and adjcent large polygons -> confusing.
    df_sub_counts = df_sub.groupby(["src_FID"])["OID"].count().reset_index()
    df_sub = df_sub[df_sub["src_FID"].isin(df_sub_counts[df_sub_counts["OID"]==1]["src_FID"])]

    if (len(df_sub)==len(df_sub.src_FID.unique())):
        print("Merging objects not unique!")


    dissolve_FID = []
    # add dissolve field based on FID of the target polygon
    with edit(dissolve_layer):
        provider = dissolve_layer.dataProvider()
        provider.addAttributes([QgsField("dissolve", QVariant.Int)])
        dissolve_layer.updateFields()
        
        for f in dissolve_layer.getFeatures():
            f["dissolve"] = f["FID_orig"]
            if f["FID_orig"] in df_sub.src_FID.values:
                dissolve_FID.append(f["FID_orig"])
            dissolve_layer.updateFeature(f)  
        
        for index, row in df_sub.iterrows():
            dissolve_layer.selectByExpression("FID_orig = {0}".format(row.src_FID))
            for f in dissolve_layer.getSelectedFeatures():
                f["dissolve"] = row.nbr_FID
                dissolve_layer.updateFeature(f)  

    # cast dissolve_FID to int, in some cases it is generated as list of 'float'
    dissolve_FID = [int(x) for x in dissolve_FID]
    # get subset shapefile of polygons to dissolve
    dissolve_layer.removeSelection()
    dissolve_layer.selectByIds(dissolve_FID)

    # print info message
    print(len(dissolve_FID), "polygons to dissolve!")

    # metainfo: shapefile with polygons to dissolve
    dissolve_polygon_path = os.path.join(working_root,"polygons_to_dissolve.gpkg")
    param = {'INPUT': dissolve_layer,'OUTPUT': dissolve_polygon_path}
    algoOutput = processing.run("native:saveselectedfeatures", param)

    # dissolve and join
    param = {'INPUT': dissolve_layer_path,'FIELD':['dissolve'],'OUTPUT':'memory:'}
    algoOutput = processing.run("native:dissolve", param)

    #delete old fields (may be wrong)    
    fields = ['ID','hmax','hdom','type','dissolve']
    mLayer = algoOutput["OUTPUT"]
    delete_fields(mLayer, fields)

    with edit(mLayer):
        expression = QgsExpression('to_int(area($geometry))')
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(mLayer))
        for f in mLayer.getFeatures():
            context.setFeature(f)
            f['area_m2'] = expression.evaluate(context)
            mLayer.updateFeature(f)


    param = {'INPUT': mLayer,'FIELD':'FID_orig','INPUT_2':shape_in_path,'FIELD_2':'FID_orig','FIELDS_TO_COPY':['ID','hmax','hdom','type'],'METHOD':1,'DISCARD_NONMATCHING':False,'PREFIX':'','OUTPUT': shape_out_path}
    algoOutput = processing.run("native:joinattributestable", param)
    
    # Delete tmp files
    if del_tmp:
        delete_shapefile(dissolve_layer_path)
