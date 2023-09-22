######################################################################
# Clip stand shapefile to exact perimeter and fill gaps.
#
# (C) Dominique Weber,  Christoph Schaller, HAFL, BFH
######################################################################

import sys
import os


from qgis import core
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant
from qgis.utils import iface
from qgis.core import QgsProject
import processing
from qgis.core import *

from tbk_qgis.tbk.utility.tbk_utilities import *

def clip_to_perimeter(tbk_path, perimeter, del_tmp=True):
    print("--------------------------------------------")
    print("START Clip to perimeter...")

    stands_merged_path = os.path.join(tbk_path,"stands_merged.shp")
    stands_clip_path = os.path.join(tbk_path,"stands_clip_tmp.shp")

    # Clip to forest mask
    param = {'INPUT':stands_merged_path,'OVERLAY':perimeter,'OUTPUT':stands_clip_path}
    processing.run("native:clip", param)

    #Clip highest trees
    highest_point_path = os.path.join(tbk_path,"stands_highest_tree_tmp.shp")
    highest_point_clip_path = os.path.join(tbk_path,"stands_highest_tree.shp")
    param = {'INPUT':highest_point_path,'OVERLAY':perimeter,'OUTPUT':highest_point_clip_path}
    processing.run("native:clip", param)

    if del_tmp:
        delete_shapefile(highest_point_path)

def clip_vhm_to_perimeter(tbk_path, vhm_input, perimeter, vhm_output_name):
    print("--------------------------------------------")
    print("START Clip VHM to perimeter...")

    # Clip to forest mask
    vhm_clipped_path = os.path.join(tbk_path, vhm_output_name)

    param = {'INPUT':vhm_input,'MASK':perimeter,'SOURCE_CRS':None,'TARGET_CRS':None,'NODATA':None,
    'ALPHA_BAND':False,'CROP_TO_CUTLINE':True,'KEEP_RESOLUTION':False,
    'SET_RESOLUTION':False,'X_RESOLUTION':0,'Y_RESOLUTION':0,'MULTITHREADING':False,
    'OPTIONS':'','DATA_TYPE':0,
    'EXTRA':'-multi -wm 5000 -co COMPRESS=LZW -co TILED=YES -co BIGTIFF=YES  -wo \"CUTLINE_ALL_TOUCHED=TRUE\"',
    'OUTPUT':vhm_clipped_path}
    processing.run("gdal:cliprasterbymasklayer", param)

    return vhm_clipped_path

def eliminate_gaps(tbk_path, perimeter, del_tmp=True):
    '''
    Align tbk shapefile to perimeter (for example Waldmaske AV).
    Idea: If small gaps remain between a defined perimeter and the
    stands shapefile. They need to be merged with the neighboring stand to
    exactly match the perimeter and therefore remove small gap
    '''
    
    print("--------------------------------------------")
    print("START Eliminate gaps...")

    # TBk folder path
    workspace = tbk_path
    scratchWorkspace = tbk_path
        
    # Perimeter
    perimeter_shape = perimeter

    # File names
    in_shape_path = os.path.join(tbk_path,"stands_clip_tmp.shp")
    output_shape_path = os.path.join(tbk_path,"stands_clipped.shp")
    gaps_tmp_path = os.path.join(tbk_path,"gaps_tmp.shp")
    gaps_single_tmp_path = os.path.join(tbk_path,"gaps_single_tmp.shp")
    union_tmp_path = os.path.join(tbk_path,"stands_gaps_union_tmp.shp")
    union_tmp_buf_path = os.path.join(tbk_path,"stands_gaps_union_tmp_buf0.shp")

    ########################################
    # Find gaps
    print("finding gaps...")
    param = {'INPUT':perimeter_shape,'OVERLAY':in_shape_path,'OUTPUT':gaps_tmp_path}
    algoOutput = processing.run("native:difference", param)
    
    ########################################
    # Transform gaps to single part
    print("transform gaps to single part")
    param = {'INPUT':gaps_tmp_path,'OUTPUT':gaps_single_tmp_path}
    algoOutput = processing.run("native:multiparttosingleparts", param)

    ########################################
    # Union with stand layer
    print("union gaps with stands...")
    processing.ProcessingConfig.setSettingValue('FILTER_INVALID_GEOMETRIES', 1)
    param = {'INPUT': in_shape_path,'OVERLAY':gaps_single_tmp_path,'OVERLAY_FIELDS_PREFIX':'','OUTPUT':union_tmp_path}
    algoOutput = processing.run("native:union", param)
    processing.ProcessingConfig.setSettingValue('FILTER_INVALID_GEOMETRIES', 2)

    params = {'INPUT':union_tmp_path,'DISTANCE':0,'SEGMENTS':5,'END_CAP_STYLE':0,'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':union_tmp_buf_path}
    algoOutput = processing.run("native:buffer", params)

    ########################################
    # Eliminate gaps
    print("eliminate gaps...")
    expression = 'FID_orig IS NULL AND to_int(area($geometry))>0'

    union_layer = QgsVectorLayer(union_tmp_path, "union_tmp", "ogr")
    union_layer.selectByExpression(expression)

    ##Does not persist results when writing directly to file
    param = {'INPUT':union_layer,'MODE':2,'OUTPUT':'memory:'}
    algoOutput = processing.run("qgis:eliminateselectedpolygons", param)

    ctc = QgsProject.instance().transformContext()
    QgsVectorFileWriter.writeAsVectorFormatV2(algoOutput['OUTPUT'],output_shape_path,ctc,getVectorSaveOptions('ESRI Shapefile','utf-8'))

    ########################################
    # Delete gaps not possible to eliminate
    print("delete remaining gaps completely...")
    expression = 'FID_orig IS NULL OR to_int(area($geometry))=0'

    fields_to_delete = ["ID_2","GRIDCODE","FID_stands","FID_gaps_s","Id_1","ORIG_FID"]
    fields_to_keep = ["OBJECTID","area_m2","hmax_eff","hp80","FID_orig","ID","hmax","hdom","type"]

    out_layer = QgsVectorLayer(output_shape_path, "union_tmp", "ogr")
    prov = out_layer.dataProvider()
    for field in prov.fields():
        if not field.name() in fields_to_keep:
            fields_to_delete.append(field.name())

    out_layer.selectByExpression(expression)
    if len(out_layer.selectedFeatureIds())>0:
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
