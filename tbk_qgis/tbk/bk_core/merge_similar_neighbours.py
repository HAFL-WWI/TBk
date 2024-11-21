######################################################################
# Merge similar neighbouring stands
#
# (C) Dominique Weber, Christoph Schaller, HAFL, BFH
######################################################################


import os
import subprocess
import sys

from qgis import core
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import QVariant
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

    scratchWorkspace = tmp_output_folder

    # files
    shape_in_path = os.path.join(working_root,"stands_simplified.gpkg")
    shape_out_path = os.path.join(working_root,"stands_merged.gpkg")

    ######################################################################
    # TBk post-process. Prepare polygons to dissolve by specific criterias.
    # Used to combine small polygons with similar neighbors.
    ######################################################################
    print("min_area_m2: ", min_area_m2, " min_hdom_diff_rel: ", min_hdom_diff_rel)

    # load TBk shapefile
    simplified_layer = QgsVectorLayer(shape_in_path, "stand_boundaries_simplified", "ogr")

    dissolve_layer_path = os.path.join(tmp_output_folder, "stands_final_dissolve_field.gpkg")
    simplified_layer.selectAll()

    param = {'INPUT': simplified_layer,'OUTPUT': dissolve_layer_path}
    algoOutput = processing.run("native:saveselectedfeatures", param)

    del simplified_layer
     
    dissolve_layer = QgsVectorLayer(dissolve_layer_path, "stand_boundaries_simplified", "ogr")

    # load neighbors file depending on system settings
    neighbors_path = os.path.join(working_root,"neighbors.csv")

    df = pd.read_csv(neighbors_path)

    # select small polygons with possible neighbor to dissolve
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
