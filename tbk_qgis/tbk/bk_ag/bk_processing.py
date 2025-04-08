######################################################################
# Functions for forest stand map processing
# 07.02.2025
# (C) Raffael Bienz
######################################################################
import numpy as np
import os.path
from qgis.core import (QgsVectorLayer,
                        QgsFeature,
                        QgsVectorFileWriter,
                        QgsWkbTypes,
                        QgsProcessingFeatureSourceDefinition,
                        QgsFeatureRequest,
                        QgsProject,
                        QgsRasterLayer)
import processing

def find_neighbors(feature_dict, id):
    '''
    Takes a feature dictionary and a id of a feature as inputs. Returns ids of adjacent features.
    '''
    feature_sel = feature_dict[id]
    intersecting_ids = feature_dict.keys()
    neighbors=[]
    if len(intersecting_ids) > 1:
        for intersecting_id in intersecting_ids:
            intersecting_f = feature_dict[intersecting_id]

            if (id!=intersecting_id and not intersecting_f.geometry().disjoint(feature_sel.geometry())):
                neighbors.append(intersecting_id)
    return(neighbors)

def get_areas(feature_dict):
    '''Takes a feature dictionary as input and returns the areas for all features.'''
    areas = {}
    for feature in feature_dict.values():
        areas[feature.id()] = feature.geometry().area()
    return(areas)

def get_es(feature_dict):
    '''Takes a feature dictionary as input and returns the stage of stand development.'''
    es = {}
    for feature in feature_dict.values():
        es[feature.id()]=feature['ES']
    return(es)

def save_feature_dict (feature_dict, features, out_path):
    '''Takes a gpkg and its (adapted) feature dictionary as inputs. Saves the feature dictionary as a gpkg.'''
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.fileEncoding = "UTF-8"

    writer = QgsVectorFileWriter.create(
        out_path,
        features.fields(),
        QgsWkbTypes.Polygon,
        features.crs(),
        features.transformContext(),
        save_options
    )

    for feature in feature_dict.values():
        writer.addFeature(feature)
        
    writer=None

def simplify_polygons(perimeter_dissolve, source_prefix, dest_prefix, simplify_threshold, out_path):
    '''
    Takes perimeter features, prefixes, a simplifying threshold and a path as inputs. 
    Simplifies the geometry of all features.
    Saves new features as gpkg.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']
        
        # Load features
        name_gpkg = source_prefix + str(id) + '.gpkg'
        features_input = QgsVectorLayer(os.path.join(out_path, name_gpkg))

        # Output path
        name_gpkg = dest_prefix + str(id) + '.gpkg'
        path_output = os.path.join(out_path, name_gpkg)

        processing.run("grass7:v.generalize", {'input': features_input,'type':[0,1,2],'method':0,'threshold':simplify_threshold,'look_ahead':7,
            'reduction':50,'slide':0.5,'angle_thresh':3,'degree_thresh':0,'closeness_thresh':0,'betweeness_thresh':0,
            'alpha':1,'beta':1,'iterations':1,'-t':False,'-l':True,'output':path_output,
            'error':'TEMPORARY_OUTPUT','GRASS_REGION_PARAMETER':None,'GRASS_SNAP_TOLERANCE_PARAMETER':-1,
            'GRASS_MIN_AREA_PARAMETER':0.0001,'GRASS_OUTPUT_TYPE_PARAMETER':0,'GRASS_VECTOR_DSCO':'',
            'GRASS_VECTOR_LCO':'','GRASS_VECTOR_EXPORT_NOCAT':False})

def clip_to_perimeter(perimeter_dissolve, source_prefix, dest_prefix, out_path):
    '''
    Takes perimeter features, prefixes and a path as inputs. 
    Clips each features set to the corresponding perimeter.
    Saves new features as gpkg.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']

        # Load features
        name_gpkg = source_prefix + str(id) + '.gpkg'
        features_input = QgsVectorLayer(os.path.join(out_path, name_gpkg))

        # Output path
        name_gpkg = dest_prefix + str(id) + '.gpkg'
        path_output = os.path.join(out_path, name_gpkg)

        # Create a temporary layer for the current perimeter feature
        perimeter_layer = QgsVectorLayer('Polygon?crs=' + features_input.crs().toWkt(), 'perimeter_layer', 'memory')
        provider = perimeter_layer.dataProvider()
        provider.addFeatures([perimeter])

        # Buffer to remove small errors
        features_buf = processing.run("native:buffer", {'INPUT':features_input,'DISTANCE':1e-05,'SEGMENTS':5,'END_CAP_STYLE':0,
            'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':'TEMPORARY_OUTPUT'})
        
        processing.run("native:clip", {'INPUT':features_buf['OUTPUT'],'OVERLAY':perimeter_layer,'OUTPUT':path_output})

def clip_polygons(perimeter_dissolve, source_prefix, clip_prefix, dest_prefix, out_path):
    '''
    Takes perimeter features, prefixes and a path as inputs. 
    Clips input features to clipping features.
    Saves new features as gpkg.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']

        # Load features to be clipped
        name_gpkg = source_prefix + str(id) + '.gpkg'
        features_input = QgsVectorLayer(os.path.join(out_path, name_gpkg))

        # Load clipping features
        name_clip = clip_prefix + str(id) + '.gpkg'
        features_clip = QgsVectorLayer(os.path.join(out_path, name_clip))

        # Output path
        name_gpkg = dest_prefix + str(id) + '.gpkg'
        path_output = os.path.join(out_path, name_gpkg)
     
        processing.run("native:clip", {'INPUT':features_input, 'OVERLAY':features_clip,'OUTPUT':path_output})

def eliminate_small_polygons(perimeter_dissolve, source_prefix, dest_prefix, min_area_polygons, out_path):
    '''
    Takes perimeter features, prefixes, a minimum area and a path as inputs. 
    Merges all features smaller than minimum area with best suited neighbor.
    Saves new features as gpkg.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']

        # Load features
        name_gpkg = source_prefix + str(id) + '.gpkg'
        features_input = QgsVectorLayer(os.path.join(out_path, name_gpkg))

        # Output path
        name_gpkg = dest_prefix + str(id) + '.gpkg'
        path_output = os.path.join(out_path, name_gpkg)

        expression = "$area < " + str(min_area_polygons)
        features_input.selectByExpression(expression)

        param = {'INPUT': features_input, 'MODE': 2, 'OUTPUT': path_output}
        processing.run("qgis:eliminateselectedpolygons", param)

def merge_small_polygons(perimeter_dissolve, source_prefix, dest_prefix, min_area_polygons, out_path):
    '''
    Takes perimeter features, prefixes, a minimum area and a path as inputs. 
    Merges all features smaller than minimum area with best suited neighbor.
    Saves new features as gpkg.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']

        # Load features
        name_gpkg = source_prefix + str(id) + '.gpkg'
        features_input = QgsVectorLayer(os.path.join(out_path, name_gpkg))

        # Build Feature dictionary
        feature_dict = {f.id(): f for f in features_input.getFeatures()}
        
        # Iterate over Polygons that are too small and merge them with neighbors
        finished = len(feature_dict)*2
        while finished > 0:
            areas=get_areas(feature_dict)
            areas_too_small = [i for i in areas if areas[i]<min_area_polygons]
            es = get_es(feature_dict)
            
            if len(areas_too_small)>0:                
                id_feature=areas_too_small[0]
                feature_sel = feature_dict[id_feature]
                es_sel = feature_sel['ES']
                neighbors = find_neighbors(feature_dict, id_feature)
                neighbors_area = []
                neighbors_es = []
                for neighbor in neighbors:
                    feature_neighbor = feature_dict[neighbor]
                    feature_neighbor_es = feature_neighbor['ES']
                    if feature_neighbor_es !=0:
                        neighbors_area.append(feature_neighbor.geometry().area())
                        neighbors_es.append(feature_neighbor_es)
                    else:
                        neighbors_area.append(0.0)
                        neighbors_es.append(99.0)
                diff_es = [x - es_sel for x in neighbors_es]

                for i in [1,2,3,4,5,6,0,93,94,95,96,97,98,99]:
                    bool_diff = [x == i or x==-i for x in diff_es]
                    ids_ok = [neighbors[i] for i, x in enumerate(bool_diff) if x]
                    if len(ids_ok)>0:
                        area_ok = [areas[i] for i in ids_ok]
                        id_best = ids_ok[np.argmax(area_ok)]
                        es_best = es[id_best]
                        feature_best_neighbor = feature_dict[id_best]
                        feature_combined = feature_best_neighbor.geometry().combine(feature_sel.geometry())
                        f = QgsFeature(features_input.fields())
                        f.setGeometry(feature_combined)
                        f.setAttributes([id_best, 0, es_best])
                        f.setId(id_best)
                        feature_dict[id_best] = f
                        del feature_dict[id_feature]
                        break
                        
            else:
                finished = 0

            finished -= 1

        name_gpkg = dest_prefix + str(id) + '.gpkg'
        path_out = os.path.join(out_path, name_gpkg)
        save_feature_dict(feature_dict, features_input, path_out)

def delete_small_polygons(perimeter_dissolve, source_prefix, dest_prefix,out_path, min_area):
    '''
    Takes perimeter features, prefixes, a minimum area and a path as inputs. 
    Merges all features smaller than minimum area with best suited neighbor.
    Saves new features as gpkg.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']

        # Load features
        name_gpkg = source_prefix + str(id) + '.gpkg'
        features_input = QgsVectorLayer(os.path.join(out_path, name_gpkg))

        # Output path
        name_gpkg = dest_prefix + str(id) + '.gpkg'
        path_output = os.path.join(out_path, name_gpkg)

        # Create a new memory layer for the filtered features
        fields = features_input.fields()
        writer = QgsVectorFileWriter(
            path_output,            
            'UTF-8', fields, QgsWkbTypes.Polygon, features_input.crs(),
            driverName="GPKG"
        )

        # Iterate through the features and check their area
        for feature in features_input.getFeatures():
            geometry = feature.geometry()
            
            # Only process features that have geometry and are polygons 
            if geometry.isNull():
                continue
            
            # Check if the area is greater than the threshold
            if geometry.area() >= min_area:
                writer.addFeature(feature)
        
        # Close the writer
        del writer
 
def buffer_polygons(perimeter_dissolve, source_prefix, dest_prefix,out_path,buffer_distance):
    '''
    Takes perimeter features, prefixes, a buffer distance and a path as inputs. 
    Buffers all feature according to the buffer distance.
    Saves new features as gpkg.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']

        # Load features
        name_gpkg = source_prefix + str(id) + '.gpkg'
        features_input = QgsVectorLayer(os.path.join(out_path, name_gpkg))

        # Output path
        name_gpkg = dest_prefix + str(id) + '.gpkg'
        path_output = os.path.join(out_path, name_gpkg)

        params = {'INPUT': features_input, 'DISTANCE': buffer_distance, 'SEGMENTS': 5, 'END_CAP_STYLE': 0, 'JOIN_STYLE': 0,
                'MITER_LIMIT': 2, 'DISSOLVE': False, 'OUTPUT': path_output}
        processing.run("native:buffer", params)

def snap_to_perimeter(perimeter_dissolve, source_prefix, dest_prefix,out_path,tolerance):
    '''
    Takes perimeter features, prefixes, a snapping tolerance and a path as inputs. 
    Snaps all features according to the snapping tolerance.
    Saves new features as gpkg.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']

        # Load features
        name_gpkg = source_prefix + str(id) + '.gpkg'
        features_input = QgsVectorLayer(os.path.join(out_path, name_gpkg))

        # Output path
        name_gpkg = dest_prefix + str(id) + '.gpkg'
        path_output = os.path.join(out_path, name_gpkg)

        # Create a temporary layer for the current perimeter feature
        perimeter_layer = QgsVectorLayer('Polygon?crs=' + features_input.crs().toWkt(), 'perimeter_layer', 'memory')
        provider = perimeter_layer.dataProvider()
        provider.addFeatures([perimeter])

        # Buffer to remove small errors
        features_buf = processing.run("native:buffer", {'INPUT':features_input,'DISTANCE':1e-05,'SEGMENTS':5,'END_CAP_STYLE':0,
            'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':'TEMPORARY_OUTPUT'})
        
        processing.run("native:snapgeometries", {'INPUT':features_buf['OUTPUT'],'REFERENCE_LAYER':perimeter_layer,'TOLERANCE':tolerance,'BEHAVIOR':0,'OUTPUT':path_output})

def multipart_to_singlepart(perimeter_dissolve, source_prefix, dest_prefix, out_path):
    '''
    Takes perimeter features, prefixes and a path as inputs. 
    Converts all multipart polygons to singlepart polygons.
    Saves new features as gpkg.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']

        # Load features
        name_gpkg = source_prefix + str(id) + '.gpkg'
        features_input = QgsVectorLayer(os.path.join(out_path, name_gpkg))

        # Output path
        name_gpkg = dest_prefix + str(id) + '.gpkg'
        path_output = os.path.join(out_path, name_gpkg)

        processing.run('qgis:multiparttosingleparts', {'INPUT':features_input, 'OUTPUT':path_output})

def polygon_to_raster(perimeter_dissolve, source_prefix, reference_prefix, dest_prefix, vhm_clipped_path, out_path):
    '''
    Takes perimeter features, prefixes and paths as inputs. 
    Converts the features to raster.
    Saves new features as gpkg.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']

        # Load features
        name_gpkg = source_prefix + str(id) + '.gpkg'
        features_input = QgsVectorLayer(os.path.join(out_path, name_gpkg))

        # Load reference raster
        name_tile_source = reference_prefix + str(id) + '.tif'
        vhm_temp = QgsRasterLayer(os.path.join(vhm_clipped_path, name_tile_source))

        extent = vhm_temp.extent()  # Get the extent of the raster (xmin, ymin, xmax, ymax)

        # Output path
        name_raster = dest_prefix + str(id) + '.tif'
        raster_output_path = os.path.join(vhm_clipped_path, name_raster)
        #output_width = int((extent.xMaximum() - extent.xMinimum()) / resolution_x)
        #output_height = int((extent.yMaximum() - extent.yMinimum()) / resolution_y)
        processing.run("gdal:rasterize", {'INPUT':features_input,
                                          'FIELD':'ES','BURN':0,'USE_Z':False,'UNITS':1,'WIDTH':1,'HEIGHT':1,'EXTENT':extent,
                                          'NODATA':0,'OPTIONS':'','DATA_TYPE':0,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':raster_output_path})

    