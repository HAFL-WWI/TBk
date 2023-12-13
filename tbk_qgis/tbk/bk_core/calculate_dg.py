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
from datetime import timedelta
import time
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
    max_height_ks = 1.0
    min_height_us = 1.0
    min_height_hdom_factor_ms = 1.0 / 3.0
    min_height_hdom_factor_os = 2.0 / 3.0
    min_height_hmax_factor_ueb = 1.0

    ########################################################################

    stands_layer = QgsVectorLayer(stands_shapefile, "stands", "ogr")

    #
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

    field_file_pairs = [
        ['dg_ks_', 'dg_ks_max' , tmp_lim_ks, dg_ks_classified],
        ['dg_us_','dg_us_min' , tmp_lim_us, dg_us_classified],
        ['dg_ms_','dg_ms_min', tmp_lim_ms, dg_ms_classified],
        ['dg_os_','dg_os_min', tmp_lim_os, dg_os_classified],
        ['dg_ueb_','dg_ueb_min', tmp_lim_ueb, dg_ueb_classified],
        ['dg_','dg_min', tmp_lim_dg, dg_classified]
    ]

    # Produce final "1" / "0" raster for each layer
    print("classify stand layers...")
    # A: CreateCopy > rasterize over > calc/compress
    for column_prefix, dg_lim_field, dg_tmp_file, dg_layer_file in field_file_pairs:
        start_time = time.time()
        # print(dg_lim_field, "->", dg_tmp_file, "->", dg_layer_file)
        # create an empty DG layer based on vhm extents for each layer
        create_empty_copy(vhm, dg_tmp_file)
        # burn vector value into raster
        processing.run("gdal:rasterize_over", {
            'INPUT': stands_shapefile,
            'INPUT_RASTER': dg_tmp_file,
            'FIELD': dg_lim_field,
            'ADD': False, 'EXTRA': ''})
        # classify raster
        processing.run("gdal:rastercalculator", {
            'INPUT_A': vhm, 'BAND_A': 1, 'INPUT_B': dg_tmp_file, 'BAND_B': 1, 'INPUT_C': None, 'BAND_C': -1,
            'INPUT_D': None, 'BAND_D': -1, 'INPUT_E': None, 'BAND_E': -1, 'INPUT_F': None, 'BAND_F': -1,
            'FORMULA': '((A<B) & True)*1', 'NO_DATA': None, 'RTYPE': 0,
            'OPTIONS': 'COMPRESS=ZSTD|PREDICTOR=2|ZLEVEL=1', 'EXTRA': '', 'OUTPUT': dg_layer_file})
        # clean up temp files
        if del_tmp:
            delete_raster(dg_tmp_file)
            if os.path.exists(dg_tmp_file + ".aux.xml"):
                os.remove(dg_tmp_file + ".aux.xml")

        end_time = time.time()
        print(f'{column_prefix}layer classification execution time: {str(timedelta(seconds=(end_time - start_time)))}')

    # Calculate DG per stand and per layer
    print("zonal statistics...")

    for column_prefix, dg_lim_field, dg_tmp_file, dg_layer_file in field_file_pairs:
        start_time = time.time()
        param = {'INPUT_RASTER': dg_layer_file, 'RASTER_BAND': 1,
                 'INPUT_VECTOR': stands_shapefile,
                 'COLUMN_PREFIX': column_prefix, 'STATS': [2]}
        processing.run("qgis:zonalstatistics", param)
        end_time = time.time()
        print(f'{column_prefix}layer classification execution time: {str(timedelta(seconds=(end_time - start_time)))}')

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

    # Delete temporary fields
    if del_tmp:
        delete_fields(stands_layer,
                      ["dg_ks_max", "dg_us_min", "dg_ms_min", "dg_os_min", "dg_ueb_min", "dg_min", "dissolve",
                       "dg_ks_mean", "dg_us_mean", "dg_ms_mean", "dg_os_mean", "dg_ueb_mea", "dg_mean",
                       'dg_ks_coun', 'dg_ks_sum', 'dg_us_coun', 'dg_us_sum', 'dg_ms_coun', 'dg_ms_sum', 'dg_os_coun',
                       'dg_os_sum', 'dg_ueb_cou', 'dg_ueb_sum', 'dg_count', 'dg_sum',
                       ])
    
    print("DONE!")


