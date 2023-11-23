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
from qgis.core import *

from tbk_qgis.tbk.utility.tbk_utilities import *

from osgeo import gdal


def calculate_dg(tbk_path, vhm, del_tmp=True):
    print("--------------------------------------------")
    print("START DG calculation...")

    # TBk folder path
    workspace = tbk_path
    scratchWorkspace = tbk_path

    # Use half of the cores on the machine.
    #arcpy.env.parallelProcessingFactor = "50%"

    # TBk shapefile
    stands_shapefile = os.path.join(tbk_path,"stands_clipped.shp")

    # Create dg layer output directory
    dg_layers_dir = os.path.join(tbk_path, "dg_layers")
    if not os.path.exists(dg_layers_dir):
        os.makedirs(dg_layers_dir)

    # DG layers
    dg_ks_classified = os.path.join(dg_layers_dir, "dg_layer_ks.tif")
    dg_us_classified = os.path.join(dg_layers_dir, "dg_layer_us.tif")
    dg_ms_classified = os.path.join(dg_layers_dir, "dg_layer_ms.tif")
    dg_os_classified = os.path.join(dg_layers_dir, "dg_layer_os.tif")
    dg_ueb_classified = os.path.join(dg_layers_dir, "dg_layer_ueb.tif")
    dg_classified = os.path.join(dg_layers_dir, "dg_layer.tif")

    # tmp files
    tmp_lim_ks = os.path.join(dg_layers_dir, "dg_ks_max.tif")
    tmp_lim_us = os.path.join(dg_layers_dir, "dg_us_min.tif")
    tmp_lim_ms = os.path.join(dg_layers_dir, "dg_ms_min.tif")
    tmp_lim_os = os.path.join(dg_layers_dir, "dg_lim_os.tif")
    tmp_lim_ueb = os.path.join(dg_layers_dir, "dg_lim_ueb.tif")
    tmp_lim_dg = os.path.join(dg_layers_dir, "dg_lim_dg.tif")
    
    # Layer threshold values (based on NFI definition, www.lfi.ch)
    max_height_ks = 0.4
    min_height_us = 0.4
    min_height_hdom_factor_ms = 1.0 / 3.0
    min_height_hdom_factor_os = 2.0 / 3.0
    min_height_hmax_factor_ueb = 1.0

    ########################################################################

    stands_layer = QgsVectorLayer(stands_shapefile, "stands", "ogr")

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


    # Create temp rasters for DG limits
    print("feature to raster...")

    meta_data = get_raster_metadata(vhm)
    extent = "{0},{1},{2},{3} [EPSG:{4}]".format(meta_data["extent"][0],meta_data["extent"][2],meta_data["extent"][1],meta_data["extent"][3],meta_data["epsg"]) 

    #param = {'INPUT':stands_shapefile,'FIELD':'dg_ks_max','BURN':0,'UNITS':1,'WIDTH':meta_data["xResolution"],'HEIGHT':meta_data["yResolution"],'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':tmp_lim_ks}
    #algoOutput = processing.run("gdal:rasterize", param)
    #
    #param = {'INPUT':stands_shapefile,'FIELD':'dg_us_min','BURN':0,'UNITS':1,'WIDTH':meta_data["xResolution"],'HEIGHT':meta_data["yResolution"],'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':tmp_lim_us}
    #algoOutput = processing.run("gdal:rasterize", param)
    #
    #param = {'INPUT':stands_shapefile,'FIELD':'dg_ms_min','BURN':0,'UNITS':1,'WIDTH':meta_data["xResolution"],'HEIGHT':meta_data["yResolution"],'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':tmp_lim_ms}
    #algoOutput = processing.run("gdal:rasterize", param)
    #
    #param = {'INPUT':stands_shapefile,'FIELD':'dg_os_min','BURN':0,'UNITS':1,'WIDTH':meta_data["xResolution"],'HEIGHT':meta_data["yResolution"],'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':tmp_lim_os}
    #algoOutput = processing.run("gdal:rasterize", param)
    #
    #param = {'INPUT':stands_shapefile,'FIELD':'dg_ueb_min','BURN':0,'UNITS':1,'WIDTH':meta_data["xResolution"],'HEIGHT':meta_data["yResolution"],'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':tmp_lim_ueb}
    #algoOutput = processing.run("gdal:rasterize", param)
    #
    #param = {'INPUT':stands_shapefile,'FIELD':'dg_min','BURN':0,'UNITS':1,'WIDTH':meta_data["xResolution"],'HEIGHT':meta_data["yResolution"],'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':tmp_lim_dg}
    #algoOutput = processing.run("gdal:rasterize", param)

    param = {'INPUT':stands_shapefile,'FIELD':'dg_ks_max','BURN':0,'UNITS':1,'WIDTH':10,'HEIGHT':10,'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'}
    algoOutput = processing.run("gdal:rasterize", param)
    param = {'INPUT':algoOutput["OUTPUT"],'SOURCE_CRS':None,'TARGET_CRS':None,'RESAMPLING':0,'NODATA':None,'TARGET_RESOLUTION':meta_data["xResolution"],'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':0,'TARGET_EXTENT':extent,'TARGET_EXTENT_CRS':None,'MULTITHREADING':False,'EXTRA':'','OUTPUT':tmp_lim_ks}
    processing.run("gdal:warpreproject", param)

    param = {'INPUT':stands_shapefile,'FIELD':'dg_us_min','BURN':0,'UNITS':1,'WIDTH':10,'HEIGHT':10,'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'}
    algoOutput = processing.run("gdal:rasterize", param)
    param = {'INPUT':algoOutput["OUTPUT"],'SOURCE_CRS':None,'TARGET_CRS':None,'RESAMPLING':0,'NODATA':None,'TARGET_RESOLUTION':meta_data["xResolution"],'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':0,'TARGET_EXTENT':extent,'TARGET_EXTENT_CRS':None,'MULTITHREADING':False,'EXTRA':'','OUTPUT':tmp_lim_us}
    processing.run("gdal:warpreproject", param)

    param = {'INPUT':stands_shapefile,'FIELD':'dg_ms_min','BURN':0,'UNITS':1,'WIDTH':10,'HEIGHT':10,'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'}
    algoOutput = processing.run("gdal:rasterize", param)
    param = {'INPUT':algoOutput["OUTPUT"],'SOURCE_CRS':None,'TARGET_CRS':None,'RESAMPLING':0,'NODATA':None,'TARGET_RESOLUTION':meta_data["xResolution"],'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':0,'TARGET_EXTENT':extent,'TARGET_EXTENT_CRS':None,'MULTITHREADING':False,'EXTRA':'','OUTPUT':tmp_lim_ms}
    processing.run("gdal:warpreproject", param)

    param = {'INPUT':stands_shapefile,'FIELD':'dg_os_min','BURN':0,'UNITS':1,'WIDTH':10,'HEIGHT':10,'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'}
    algoOutput = processing.run("gdal:rasterize", param)
    param = {'INPUT':algoOutput["OUTPUT"],'SOURCE_CRS':None,'TARGET_CRS':None,'RESAMPLING':0,'NODATA':None,'TARGET_RESOLUTION':meta_data["xResolution"],'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':0,'TARGET_EXTENT':extent,'TARGET_EXTENT_CRS':None,'MULTITHREADING':False,'EXTRA':'','OUTPUT':tmp_lim_os}
    processing.run("gdal:warpreproject", param)

    param = {'INPUT':stands_shapefile,'FIELD':'dg_ueb_min','BURN':0,'UNITS':1,'WIDTH':10,'HEIGHT':10,'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'}
    algoOutput = processing.run("gdal:rasterize", param)
    param = {'INPUT':algoOutput["OUTPUT"],'SOURCE_CRS':None,'TARGET_CRS':None,'RESAMPLING':0,'NODATA':None,'TARGET_RESOLUTION':meta_data["xResolution"],'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':0,'TARGET_EXTENT':extent,'TARGET_EXTENT_CRS':None,'MULTITHREADING':False,'EXTRA':'','OUTPUT':tmp_lim_ueb}
    processing.run("gdal:warpreproject", param)

    param = {'INPUT':stands_shapefile,'FIELD':'dg_min','BURN':0,'UNITS':1,'WIDTH':10,'HEIGHT':10,'EXTENT':extent,'NODATA':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':5,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':'TEMPORARY_OUTPUT'}
    algoOutput = processing.run("gdal:rasterize", param)
    param = {'INPUT':algoOutput["OUTPUT"],'SOURCE_CRS':None,'TARGET_CRS':None,'RESAMPLING':0,'NODATA':None,'TARGET_RESOLUTION':meta_data["xResolution"],'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','DATA_TYPE':0,'TARGET_EXTENT':extent,'TARGET_EXTENT_CRS':None,'MULTITHREADING':False,'EXTRA':'','OUTPUT':tmp_lim_dg}
    processing.run("gdal:warpreproject", param)


    # #GDAL/Burn rasterize
    # src_data = gdal.Open(vhm)
    # driver = src_data.GetDriver()
    # tmp_gdal_lim_ks = os.path.join(dg_layers_dir, "dg_ks_max_gdal.tif")
    # tmp_gdal_lim_us = os.path.join(dg_layers_dir, "dg_us_min_gdal.tif")
    # tmp_gdal_lim_ms = os.path.join(dg_layers_dir, "dg_ms_min_gdal.tif")
    # tmp_gdal_lim_os = os.path.join(dg_layers_dir, "dg_lim_os_gdal.tif")
    # tmp_gdal_lim_ueb = os.path.join(dg_layers_dir, "dg_lim_ueb_gdal.tif")
    # tmp_gdal_lim_dg = os.path.join(dg_layers_dir, "dg_lim_dg_gdal.tif")
    # dst_data = driver.CreateCopy(tmp_gdal_lim_ks, src_data, strict=0)
    # dst_data = None
    # dst_data = driver.CreateCopy(tmp_gdal_lim_us, src_data, strict=0)
    # dst_data = None
    # dst_data = driver.CreateCopy(tmp_gdal_lim_ms, src_data, strict=0)
    # dst_data = None
    # dst_data = driver.CreateCopy(tmp_gdal_lim_os, src_data, strict=0)
    # dst_data = None
    # dst_data = driver.CreateCopy(tmp_gdal_lim_ueb, src_data, strict=0)
    # dst_data = None
    # dst_data = driver.CreateCopy(tmp_gdal_lim_dg, src_data, strict=0)
    # dst_data = None
    # src_ds = None
    # param = {'INPUT':stands_shapefile,'INPUT_RASTER':tmp_gdal_lim_ks,'FIELD':'dg_ks_max','ADD':False,'EXTRA':''}
    # algoOutput = processing.run("gdal:rasterize_over", param)
    # param = {'INPUT':stands_shapefile,'INPUT_RASTER':tmp_gdal_lim_us,'FIELD':'dg_us_min','ADD':False,'EXTRA':''}
    # algoOutput = processing.run("gdal:rasterize_over", param)
    # param = {'INPUT':stands_shapefile,'INPUT_RASTER':tmp_gdal_lim_ms,'FIELD':'dg_ms_min','ADD':False,'EXTRA':''}
    # algoOutput = processing.run("gdal:rasterize_over", param)
    # param = {'INPUT':stands_shapefile,'INPUT_RASTER':tmp_gdal_lim_os,'FIELD':'dg_os_min','ADD':False,'EXTRA':''}
    # algoOutput = processing.run("gdal:rasterize_over", param)
    # param = {'INPUT':stands_shapefile,'INPUT_RASTER':tmp_gdal_lim_ueb,'FIELD':'dg_ueb_min','ADD':False,'EXTRA':''}
    # algoOutput = processing.run("gdal:rasterize_over", param)
    # param = {'INPUT':stands_shapefile,'INPUT_RASTER':tmp_gdal_lim_dg,'FIELD':'dg_min','ADD':False,'EXTRA':''}
    # algoOutput = processing.run("gdal:rasterize_over", param)





    # Produce "1" / "0" raster for each layer
    print("classify stand layers...")

    param = {'INPUT_A':vhm,'BAND_A':1,'INPUT_B':tmp_lim_ks,'BAND_B':1,'INPUT_C':None,'BAND_C':-1,'INPUT_D':None,'BAND_D':-1,'INPUT_E':None,'BAND_E':-1,'INPUT_F':None,'BAND_F':-1,
             'FORMULA':'((A<B) & True)*1','NO_DATA':None,'RTYPE':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','EXTRA':'','OUTPUT':dg_ks_classified}
    algoOutput = processing.run("gdal:rastercalculator", param)

    param = {'INPUT_A':vhm,'BAND_A':1,'INPUT_B':tmp_lim_us,'BAND_B':1,'INPUT_C':tmp_lim_ms,'BAND_C':1,'INPUT_D':None,'BAND_D':-1,'INPUT_E':None,'BAND_E':-1,'INPUT_F':None,'BAND_F':-1,
            'FORMULA':'((A>=B) & (A<=C))*1','NO_DATA':None,'RTYPE':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','EXTRA':'','OUTPUT':dg_us_classified}
    algoOutput = processing.run("gdal:rastercalculator", param)

    param = {'INPUT_A':vhm,'BAND_A':1,'INPUT_B':tmp_lim_ms,'BAND_B':1,'INPUT_C':tmp_lim_os,'BAND_C':1,'INPUT_D':None,'BAND_D':-1,'INPUT_E':None,'BAND_E':-1,'INPUT_F':None,'BAND_F':-1,
            'FORMULA':'((A>B) & (A<=C))*1','NO_DATA':None,'RTYPE':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','EXTRA':'','OUTPUT':dg_ms_classified}
    algoOutput = processing.run("gdal:rastercalculator", param)

    param = {'INPUT_A':vhm,'BAND_A':1,'INPUT_B':tmp_lim_os,'BAND_B':1,'INPUT_C':tmp_lim_ueb,'BAND_C':1,'INPUT_D':None,'BAND_D':-1,'INPUT_E':None,'BAND_E':-1,'INPUT_F':None,'BAND_F':-1,
            'FORMULA':'((A>B) & (A<=C))*1','NO_DATA':None,'RTYPE':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','EXTRA':'','OUTPUT':dg_os_classified}
    algoOutput = processing.run("gdal:rastercalculator", param)

    param = {'INPUT_A':vhm,'BAND_A':1,'INPUT_B':tmp_lim_ueb,'BAND_B':1,'INPUT_C':None,'BAND_C':-1,'INPUT_D':None,'BAND_D':-1,'INPUT_E':None,'BAND_E':-1,'INPUT_F':None,'BAND_F':-1,
             'FORMULA':'((A>B) & True)*1','NO_DATA':None,'RTYPE':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','EXTRA':'','OUTPUT':dg_ueb_classified}
    algoOutput = processing.run("gdal:rastercalculator", param)

    param = {'INPUT_A':vhm,'BAND_A':1,'INPUT_B':tmp_lim_dg,'BAND_B':1,'INPUT_C':None,'BAND_C':-1,'INPUT_D':None,'BAND_D':-1,'INPUT_E':None,'BAND_E':-1,'INPUT_F':None,'BAND_F':-1,
             'FORMULA':'((A>B) & True)*1','NO_DATA':None,'RTYPE':0,'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9','EXTRA':'','OUTPUT':dg_classified}
    algoOutput = processing.run("gdal:rastercalculator", param)

    # Calculate DG per stand and per layer
    print("zonal statistics...")

    param ={'INPUT_RASTER':dg_ks_classified,'RASTER_BAND':1,'INPUT_VECTOR':stands_shapefile,'COLUMN_PREFIX':'dg_ks_','STATS':[2]}
    processing.run("qgis:zonalstatistics", param)

    param ={'INPUT_RASTER':dg_us_classified,'RASTER_BAND':1,'INPUT_VECTOR':stands_shapefile,'COLUMN_PREFIX':'dg_us_','STATS':[2]}
    processing.run("qgis:zonalstatistics", param)

    param ={'INPUT_RASTER':dg_ms_classified,'RASTER_BAND':1,'INPUT_VECTOR':stands_shapefile,'COLUMN_PREFIX':'dg_ms_','STATS':[2]}
    processing.run("qgis:zonalstatistics", param)

    param ={'INPUT_RASTER':dg_os_classified,'RASTER_BAND':1,'INPUT_VECTOR':stands_shapefile,'COLUMN_PREFIX':'dg_os_','STATS':[2]}
    processing.run("qgis:zonalstatistics", param)

    param ={'INPUT_RASTER':dg_ueb_classified,'RASTER_BAND':1,'INPUT_VECTOR':stands_shapefile,'COLUMN_PREFIX':'dg_ueb_','STATS':[2]}
    processing.run("qgis:zonalstatistics", param)

    param ={'INPUT_RASTER':dg_classified,'RASTER_BAND':1,'INPUT_VECTOR':stands_shapefile,'COLUMN_PREFIX':'dg_','STATS':[2]}
    processing.run("qgis:zonalstatistics", param)


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
            f["DG_ks"] = round(f["dg_ks_mean"]*100) if f["dg_ks_mean"] != core.NULL else f["dg_ks_mean"]
            f["DG_us"] = round(f["dg_us_mean"]*100) if f["dg_us_mean"] != core.NULL else f["dg_us_mean"]
            f["DG_ms"] = round(f["dg_ms_mean"]*100) if f["dg_ms_mean"] != core.NULL else f["dg_ms_mean"]
            f["DG_os"] = round(f["dg_os_mean"]*100) if f["dg_os_mean"] != core.NULL else f["dg_os_mean"]
            f["DG_ueb"] = round(f["dg_ueb_mea"]*100) if f["dg_ueb_mea"] != core.NULL else f["dg_ueb_mea"]
            f["DG"] = round(f["dg_mean"]*100) if f["dg_mean"] != core.NULL else f["dg_mean"]

            stands_layer.updateFeature(f)  

    # clean up
    if del_tmp:
        delete_raster(tmp_lim_ks)
        delete_raster(tmp_lim_us)
        delete_raster(tmp_lim_ms)
        delete_raster(tmp_lim_os)
        delete_raster(tmp_lim_ueb)
        delete_raster(tmp_lim_dg)

    # Delete fields
    if del_tmp:
        delete_fields(stands_layer,["dg_ks_max","dg_us_min","dg_ms_min","dg_os_min","dg_ueb_min","dg_min","dissolve","dg_ks_mean","dg_us_mean","dg_ms_mean","dg_os_mean","dg_ueb_mea","dg_mean"])
    
    print("DONE!")


