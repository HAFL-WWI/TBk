######################################################################
# Functions for VHM processing
# 07.12.2022
# (C) Raffael Bienz
######################################################################
import os.path
from osgeo import gdal
import numpy as np
from osgeo import osr
from qgis.core import (QgsRasterLayer)
import processing

def delete_raster(raster):
    '''Takes a raster and deletes it.'''
    data = gdal.Open(raster, gdal.GA_ReadOnly)
    driver = data.GetDriver()
    data = None
    if os.path.exists(raster):
        driver.Delete(raster)

def deleteRasterIfExists (raster_path):
    '''Takes a path to a raster file and deletes it, if it exists.'''
    if os.path.exists(raster_path):
        delete_raster(raster_path)

def reclassify_vhm(perimeter_dissolve, vhm_prefix, vhm_recl_prefix, reclass_table, vhm_clipped_path):
    '''Takes features, prefixes, a lookup table and a path.
        Reclassifies VHMs for each feature according to lookup table.
        Saves raster at path.
    '''

    for feature in perimeter_dissolve.getFeatures():
        id = feature['id']
        name_tile = vhm_prefix + str(id) + '.tif'
        name_tile_recl = vhm_recl_prefix + str(id) + '.tif'
        tile_recl_path = os.path.join(vhm_clipped_path, name_tile_recl)
        vhm_temp = QgsRasterLayer(os.path.join(vhm_clipped_path, name_tile))
        raster_reclass = processing.run("native:reclassifybytable",
            {'INPUT_RASTER':vhm_temp, 'TABLE':reclass_table, 'RASTER_BAND':1, 'DATA_TYPE':1, 'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
        
        par = {'FIELD': 'id', 'INPUT': perimeter_dissolve, 'OPERATOR': 0, 'OUTPUT': 'TEMPORARY_OUTPUT', 'VALUE': id}
        mask = processing.run("qgis:extractbyattribute", par)

        par = {'INPUT': raster_reclass, 'MASK': mask['OUTPUT'], 'NODATA': None, 'ALPHA_BAND': True, 'CROP_TO_CUTLINE' : True, 'KEEP_RESOLUTION': False,
        'SET_RESOLUTION' : False, 'OPTIONS': '', 'DATA_TYPE': 1, 'OUTPUT': tile_recl_path}
        processing.run("gdal:cliprasterbymasklayer", par)['OUTPUT']


def cut_vhm_to_perimeter(perimeter_dissolve, vhm, vhm_prefix, vhm_clipped_path):
    '''Takes features, a VHM, prefixes and a path.
        Cuts VHM to features.
        Saves VHM at path.
    '''
    for feature in perimeter_dissolve.getFeatures():
        id = feature['id']
            
        par = {'FIELD': 'id', 'INPUT': perimeter_dissolve, 'OPERATOR': 0, 'OUTPUT': 'TEMPORARY_OUTPUT', 'VALUE': id}
        
        mask = processing.run("qgis:extractbyattribute", par)
        name_tile = vhm_prefix + str(id) + '.tif'
        par = {'INPUT': vhm, 'MASK': mask['OUTPUT'], 'NODATA': None, 'ALPHA_BAND': True, 'CROP_TO_CUTLINE' : True, 'KEEP_RESOLUTION': False,
        'SET_RESOLUTION' : False, 'OPTIONS': '', 'DATA_TYPE': 0, 'OUTPUT': os.path.join(vhm_clipped_path, name_tile)}
        
        clip = processing.run('gdal:cliprasterbymasklayer', par)


def get_values_array(array, window_radius, r, c, n_rows, n_cols):
    '''Takes an array, a radius, a row number, a column number, the total number of rows and the total number uf columns.
        Returns an array of the values within the radius (rectangular), starting at the defined row and column.
    '''
    r_min = max(0, r-window_radius)
    r_max = min(r+window_radius, n_rows)
    c_min = max(0, c-window_radius)
    c_max = min(c+window_radius, n_cols)

    array_sel = array[r_min:r_max, c_min:c_max]

    return array_sel


def focal(raster_layer, window_radius, method, weighting_sh1, output_path):
    '''Takes a raster, radius, method, weighting parameter and a path.
        Performs a focal statistics of the raster.
        Saves the raster to the path.
    '''
    # Load data as array
    ds = gdal.Open(raster_layer.dataProvider().dataSourceUri())
    vhm_arr = ds.GetRasterBand(1).ReadAsArray()

    # Clone array for new values
    vhm_arr_new = vhm_arr.copy()

    # Get dimensions of raster
    n_rows, n_cols = vhm_arr.shape

    # Iterate over all cells and calculate new values
    for r in range(n_rows):
        for c in range(n_cols):
            val_centre = vhm_arr[r,c]

            if method=='majority':
                if val_centre ==0:
                    new_value=0
                else:
                    array = get_values_array(vhm_arr, window_radius, r, c, n_rows, n_cols)
                    array_sel= array[array != 0]
                    counts = np.bincount(array_sel.flatten())
                    new_value = np.argmax(counts)

            elif method=='SH1':
                if val_centre==0 or val_centre>2:
                    new_value=val_centre
                else:
                    array_sel = get_values_array(vhm_arr, window_radius, r, c, n_rows, n_cols)
                    counts = np.bincount(array_sel.flatten())

                    if len(counts)<3:
                        prop_sh1 = 0
                    else:
                        prop_sh1 = counts[2]/sum(counts[1:3])

                    if prop_sh1>=weighting_sh1/100:
                        new_value=2
                    else:
                        new_value=1

            else:
                print('Method not defined')
                break

            vhm_arr_new[r,c] = new_value

    # Save as new raster
    geotransform = ds.GetGeoTransform()
    prj = ds.GetProjection()
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(output_path, n_cols, n_rows, 1, 1)

    dst_ds.GetRasterBand(1).WriteArray(vhm_arr_new)
    dst_ds.SetGeoTransform(geotransform)
    srs = osr.SpatialReference(wkt = prj)
    dst_ds.SetProjection( srs.ExportToWkt())
    dst_ds = None
    ds = None
    


def focal_folder (perimeter_dissolve, window_size, method, weighting_sh1, source_path, source_prefix, dest_path, dest_prefix):
    '''Performs focal statistics for all rasters at a given path.'''
    window_radius = round(window_size/2)

    for feature in perimeter_dissolve.getFeatures():
        id = feature['id']
        name_tile_source = source_prefix + str(id) + '.tif'
        vhm_temp = QgsRasterLayer(os.path.join(source_path, name_tile_source))

        name_tile_focal = dest_prefix + str(id) + '.tif'
        tile_focal_path = os.path.join(dest_path, name_tile_focal)

        focal(vhm_temp, window_radius, method, weighting_sh1, tile_focal_path)


def vhm_to_polygon(perimeter_dissolve, source_prefix, dest_prefix, vhm_clipped_path, shape_path):
    '''Converts a raster dataset to a polygon dataset and saves the polygon as a shapefile.'''
    for feature in perimeter_dissolve.getFeatures():
        id = feature['id']
        name_tile_source = source_prefix + str(id) + '.tif'
        vhm_temp = QgsRasterLayer(os.path.join(vhm_clipped_path, name_tile_source))

        name_shp = dest_prefix + str(id) + '.shp'
        shp_out_path = os.path.join(shape_path, name_shp)

        processing.run('gdal:polygonize', {'INPUT': vhm_temp, 'BAND':1, 'FIELD':"ES", 'OUTPUT':shp_out_path})