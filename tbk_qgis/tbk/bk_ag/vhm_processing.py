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
    '''Takes a raster as input and deletes it.'''
    data = gdal.Open(raster, gdal.GA_ReadOnly)
    driver = data.GetDriver()
    data = None
    if os.path.exists(raster):
        driver.Delete(raster)

def deleteRasterIfExists (raster_path):
    '''Takes a path to a raster file as input and deletes it, if it exists.'''
    if os.path.exists(raster_path):
        delete_raster(raster_path)

def reclassify_vhm(perimeter_dissolve, vhm_prefix, vhm_recl_prefix, reclass_table, vhm_clipped_path):
    '''Takes perimeter features, prefixes, a lookup table and a path as inputs.
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

        # Buffer to remove edge effects
        mask_buf = processing.run("native:buffer", {'INPUT':mask['OUTPUT'],'DISTANCE':5,'SEGMENTS':5,'END_CAP_STYLE':0,
            'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':'TEMPORARY_OUTPUT'})

        par = {'INPUT': raster_reclass, 'MASK': mask_buf['OUTPUT'], 'NODATA': 0, 'ALPHA_BAND': False, 'CROP_TO_CUTLINE' : True, 'KEEP_RESOLUTION': False,
        'SET_RESOLUTION' : False, 'OPTIONS': '', 'DATA_TYPE': 1, 'OUTPUT': tile_recl_path}
        processing.run("gdal:cliprasterbymasklayer", par)['OUTPUT']

def cut_vhm_to_perimeter(perimeter_dissolve, vhm, vhm_prefix, vhm_clipped_path):
    '''Takes perimeter features, a VHM, prefixes and a path as inputs.
        Cuts VHM to features.
        Saves VHM at path.
    '''
    for feature in perimeter_dissolve.getFeatures():
        id = feature['id']
            
        par = {'FIELD': 'id', 'INPUT': perimeter_dissolve, 'OPERATOR': 0, 'OUTPUT': 'TEMPORARY_OUTPUT', 'VALUE': id}
        mask = processing.run("qgis:extractbyattribute", par)

        # Buffer to remove edge effects
        mask_buf = processing.run("native:buffer", {'INPUT':mask['OUTPUT'],'DISTANCE':5,'SEGMENTS':5,'END_CAP_STYLE':0,
            'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':'TEMPORARY_OUTPUT'})

        name_tile = vhm_prefix + str(id) + '.tif'
        par = {'INPUT': vhm, 'MASK': mask_buf['OUTPUT'], 'NODATA': None, 'ALPHA_BAND': True, 'CROP_TO_CUTLINE' : True, 'KEEP_RESOLUTION': False,
        'SET_RESOLUTION' : False, 'OPTIONS': '', 'DATA_TYPE': 0, 'OUTPUT': os.path.join(vhm_clipped_path, name_tile)}
        
        processing.run('gdal:cliprasterbymasklayer', par)

def get_values_array(array, window_radius, r, c, n_rows, n_cols):
    '''Takes an array, a radius, a row number, a column number, the total number of rows and the total number of columns as inputs.
        Returns an array of the values within the radius (rectangular), starting at the defined row and column.
    '''
    r_min = max(0, r-window_radius)
    r_max = min(r+window_radius+1, n_rows)
    c_min = max(0, c-window_radius)
    c_max = min(c+window_radius+1, n_cols)
    array_sel = array[r_min:r_max, c_min:c_max]
    return array_sel

def focal(raster_layer, window_radius, method, weighting_sh1, output_path, set_no_data):
    '''Takes a raster, radius, method, weighting parameter and a path as inputs.
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

            elif method=='shrink':
                array = get_values_array(vhm_arr, window_radius, r, c, n_rows, n_cols)
                #array_sel= array[array == val_centre]
                counts = np.bincount(array.flatten())

                if counts[val_centre]>(window_radius*window_radius*1.5):
                    new_value=val_centre
                else:
                    new_value=0

            elif method=='expand':
                if val_centre ==0:
                    array = get_values_array(vhm_arr, window_radius, r, c, n_rows, n_cols)
                    array_sel= array[array != 0]
                    counts = np.bincount(array_sel.flatten())
                    if (len(counts)>0):
                        new_value = np.argmax(counts)
                    else:
                        new_value=0
                else:
                    new_value=val_centre
            

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
    if set_no_data:
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
    dst_ds.SetGeoTransform(geotransform)
    srs = osr.SpatialReference(wkt = prj)
    dst_ds.SetProjection( srs.ExportToWkt())
    dst_ds = None
    ds = None
    
def focal_folder (perimeter_dissolve, window_size, method, weighting_sh1, source_path, source_prefix, dest_path, dest_prefix, set_no_data):
    '''
    Takes perimeter features, prefixes, a window size, a method, weighting parameter, no data value and paths as inputs. 
    Performs focal statistics for all rasters at a given path.
    Saves the rasters to the output path.
    '''
    window_radius = round(window_size/2-0.1)

    for feature in perimeter_dissolve.getFeatures():
        id = feature['id']
        name_tile_source = source_prefix + str(id) + '.tif'
        vhm_temp = QgsRasterLayer(os.path.join(source_path, name_tile_source))

        name_tile_focal = dest_prefix + str(id) + '.tif'
        tile_focal_path = os.path.join(dest_path, name_tile_focal)

        focal(vhm_temp, window_radius, method, weighting_sh1, tile_focal_path, set_no_data)

def sieve_vhm(perimeter_dissolve, source_path, source_prefix, dest_path, dest_prefix, sieve_thresh):
    '''
    Takes perimeter features, prefixes, a sieving threshold and paths as inputs. 
    Combines areas under the threshold with neighbors.
    Saves the rasters to the output path.
    '''
    for feature in perimeter_dissolve.getFeatures():
        id = feature['id']
        name_tile_source = source_prefix + str(id) + '.tif'
        vhm_temp = QgsRasterLayer(os.path.join(source_path, name_tile_source))

        name_tile_out = dest_prefix + str(id) + '.tif'
        tile_out_path = os.path.join(dest_path, name_tile_out)
        processing.run("gdal:sieve", {'INPUT': vhm_temp,'THRESHOLD':sieve_thresh,'EIGHT_CONNECTEDNESS':False,'NO_MASK':False,'MASK_LAYER':None,'EXTRA':'','OUTPUT':tile_out_path})

def vhm_to_polygon(perimeter_dissolve, source_prefix, dest_prefix, vhm_clipped_path, out_path):
    '''
    Takes perimeter features, prefixes, a sieving threshold and paths as inputs. 
    Converts a raster dataset to a polygon dataset.
    Saves the features as gpkg.
    '''
    for feature in perimeter_dissolve.getFeatures():
        id = feature['id']
        name_tile_source = source_prefix + str(id) + '.tif'
        vhm_temp = QgsRasterLayer(os.path.join(vhm_clipped_path, name_tile_source))

        name_gpkg = dest_prefix + str(id) + '.gpkg'
        path_output = os.path.join(out_path, name_gpkg)

        processing.run('gdal:polygonize', {'INPUT': vhm_temp, 'BAND':1, 'FIELD':"ES", 'OUTPUT':path_output})

