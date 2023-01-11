######################################################################
# Add new field NH for coniferous proportion.
#
# WARNING: identical coordinate system needed!
#
# (C) Dominique Weber, Christoph Schaller, HAFL, BFH
######################################################################

# Import arcpy module
import sys
import os
import shutil

from qgis import core
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant
from qgis.utils import iface
from qgis.core import QgsProject
import processing
from qgis.core import *

from tbk.utility.tbk_utilities import *


def add_coniferous_proportion(tbk_path, coniferous_raster, calc_main_layer, del_tmp=True):
    print("--------------------------------------------")
    print("START coniferous proportion...")

    workspace = tbk_path
    scratchWorkspace = tbk_path
    
    print("loading files...")
    if coniferous_raster == 'null' or coniferous_raster == None:
        return
    nh_raster = coniferous_raster
    stands_shapefile = os.path.join(tbk_path,"stands_clipped.shp")

    print("calc mean coniferous proportion...")

    param ={'INPUT_RASTER':nh_raster,'RASTER_BAND':1,'INPUT_VECTOR':stands_shapefile,'COLUMN_PREFIX':'nh_','STATS':[2]}
    processing.run("qgis:zonalstatistics", param)

    stands_layer = QgsVectorLayer(stands_shapefile, "stands", "ogr")

    with edit(stands_layer):
        # Add NH fields
        provider = stands_layer.dataProvider()
        provider.addAttributes([QgsField("NH", QVariant.Int)])
        stands_layer.updateFields()

        # Calculate NH per stand
        for f in stands_layer.getFeatures():
            f["NH"] = f["nh_mean"]
            stands_layer.updateFeature(f)  
    
    if del_tmp:
        delete_fields(stands_layer, ["nh_mean"])
    del stands_layer

    # NH OS
    if calc_main_layer:
        print("calc mean coniferous proportion for main layer...")
        # dg raster layer
        dg_layer_os = os.path.join(tbk_path, r"dg_layers\dg_layer.tif")

        # minimum degree of cover to select valid 10 m NH pixels
        cover = 40

        # output raster file
        dg_layer_os_nh = os.path.join(tbk_path, "nh_os.tif")

        # Output files tmp
        output_tmp_folder = os.path.join(tbk_path, "tmp")
        if not os.path.isdir(output_tmp_folder):
            os.makedirs(output_tmp_folder)
        dg_layer_os_1m = os.path.join(output_tmp_folder, "dg_layer_os_1m.tif")
        dg_layer_os_10m_sum = os.path.join(output_tmp_folder, "dg_layer_os_10m_sum.tif")
        dg_layer_os_10m_mask = os.path.join(output_tmp_folder, "dg_layer_os_10m_mask.tif")
        nh_mean_table = os.path.join(output_tmp_folder, "nh_mean_table")
        nh_sum_table = os.path.join(output_tmp_folder, "nh_sum_table")

        # Resample os layer to 1m
        param = {'INPUT':dg_layer_os,'SOURCE_CRS':None,'TARGET_CRS':None,'RESAMPLING':1,'NODATA':None,'TARGET_RESOLUTION':1,'OPTIONS':'','DATA_TYPE':0,'TARGET_EXTENT':None,'TARGET_EXTENT_CRS':None,'MULTITHREADING':False,'EXTRA':'','OUTPUT':dg_layer_os_1m}
        algoOutput = processing.run("gdal:warpreproject", param)
        
        # Aggregate os sum per 10m Sentinel-2 pixel
        meta_data = get_raster_metadata(nh_raster)
        extent = "{0},{1},{2},{3} [EPSG:{4}]".format(meta_data["extent"][0],meta_data["extent"][2],meta_data["extent"][1],meta_data["extent"][3],meta_data["epsg"]) 

        param = {'input':dg_layer_os_1m,'method':8,'quantile':0.5,'-n':False,'-w':False,'output':dg_layer_os_10m_sum,
                 'GRASS_REGION_PARAMETER':extent,'GRASS_REGION_CELLSIZE_PARAMETER':10,'GRASS_RASTER_FORMAT_OPT':'','GRASS_RASTER_FORMAT_META':''}
        algoOutput = processing.run("grass7:r.resamp.stats", param)

        meta_data = get_raster_metadata(dg_layer_os)
        param = {'INPUT': dg_layer_os_10m_sum,'CRS':QgsCoordinateReferenceSystem('EPSG:{0}'.format(meta_data["epsg"]))}
        processing.run("gdal:assignprojection", param)

        # Reclassify
        condition_string = "(A < {0})*1".format(str(cover))
        param = {'INPUT_A':dg_layer_os_10m_sum,'BAND_A':1,'INPUT_B':None,'BAND_B':-1,'INPUT_C':None,'BAND_C':-1,'INPUT_D':None,'BAND_D':-1,'INPUT_E':None,'BAND_E':-1,'INPUT_F':None,'BAND_F':-1,
                'FORMULA':condition_string,'NO_DATA':None,'RTYPE':0,'OPTIONS':'','EXTRA':'','OUTPUT':dg_layer_os_10m_mask}
        processing.run("gdal:rastercalculator", param)

        # Extract pixels covered by OS
        param = {'INPUT_A':nh_raster,'BAND_A':1,'INPUT_B':dg_layer_os_10m_mask,'BAND_B':1,'INPUT_C':None,'BAND_C':-1,'INPUT_D':None,'BAND_D':-1,'INPUT_E':None,'BAND_E':-1,'INPUT_F':None,'BAND_F':-1,
                'FORMULA':'A*(B>0)','NO_DATA':None,'RTYPE':0,'OPTIONS':'','EXTRA':'','OUTPUT':dg_layer_os_nh}
        processing.run("gdal:rastercalculator", param)

        # Calculate mean NH_OS
        param ={'INPUT_RASTER':dg_layer_os_nh,'RASTER_BAND':1,'INPUT_VECTOR':stands_shapefile,'COLUMN_PREFIX':'nh_','STATS':[2]}
        processing.run("qgis:zonalstatistics", param)

        # Calculate sum NH_OS pixels
        param ={'INPUT_RASTER':dg_layer_os_10m_mask,'RASTER_BAND':1,'INPUT_VECTOR':stands_shapefile,'COLUMN_PREFIX':'nhm_','STATS':[1]}
        processing.run("qgis:zonalstatistics", param)

        stands_layer = QgsVectorLayer(stands_shapefile, "stands", "ogr")

        with edit(stands_layer):
            # Add NH fields
            provider = stands_layer.dataProvider()
            provider.addAttributes([QgsField("NH_OS", QVariant.Int),
                                    QgsField("NH_OS_PIX", QVariant.Int)])
            stands_layer.updateFields()

            # Calculate NH fields per stand         
            for f in stands_layer.getFeatures():
                if f["NH_OS"] > 0:
                    f["NH_OS"] = f["nh_mean"]
                    f["NH_OS_PIX"] = f["nhm_sum"]
                else:
                    # set value to -1 if no NH_OS pixels
                    f["NH_OS"] = -1
                    f["NH_OS_PIX"] = f["nhm_sum"]
                stands_layer.updateFeature(f)  


        if del_tmp:
            delete_fields(stands_layer, ["nh_mean","nhm_sum"])

        # Delete tmp files
        if del_tmp:
            delete_raster(dg_layer_os_1m)
            delete_raster(dg_layer_os_10m_sum)
            #delete_raster(dg_layer_os_10m_mask)
            #shutil.rmtree(output_tmp_folder)

    print("DONE!")
