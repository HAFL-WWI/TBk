######################################################################
# Functions for forest stand map processing
# 07.12.2022
# (C) Raffael Bienz
######################################################################
import numpy as np
import os.path
from qgis.core import (QgsVectorLayer,
                        QgsFeature,
                        QgsVectorFileWriter,
                        QgsWkbTypes)
import processing


def find_neighbors(feature_dict, id):
    '''
    Takes a feature dictionary and a id of a feature. Returns ids of adjacent features.
    '''
    shp_sel = feature_dict[id]
    intersecting_ids = feature_dict.keys()
    neighbors=[]
    if len(intersecting_ids) > 1:
        for intersecting_id in intersecting_ids:
            intersecting_f = feature_dict[intersecting_id]

            if (id!=intersecting_id and not intersecting_f.geometry().disjoint(shp_sel.geometry())):
                neighbors.append(intersecting_id)
    return(neighbors)


def get_areas(feature_dict):
    '''Takes a feature dictionary and return the areas for all features.'''
    areas = {}
    for feature in feature_dict.values():
        areas[feature.id()] = feature.geometry().area()
    return(areas)


def get_es(feature_dict):
    '''Takes a feature dictionary and returns the stage of stand development.'''
    es = {}
    for feature in feature_dict.values():
        es[feature.id()]=feature['ES']
    return(es)


def save_feature_dict (feature_dict, shapefile, shp_out_path):
    '''Takes a shapefile and its (adapted) feature dictionary. Saves the feature dictionary as a geopackage.'''
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = "GPKG"
    save_options.fileEncoding = "UTF-8"

    writer = QgsVectorFileWriter.create(
        shp_out_path,
        shapefile.fields(),
        QgsWkbTypes.Polygon,
        shapefile.crs(),
        shapefile.transformContext(),
        save_options
    )

    for feature in feature_dict.values():
        writer.addFeature(feature)
        
    writer=None


def simplify_polygons(perimeter_dissolve, source_prefix, dest_prefix, simplify_threshold, shape_path):
    '''
    Takes features, prefixes, a minimum area and a path. 
    Simplifies the geometry of all features.
    Saves new features as shapefile.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']
        name_shp = source_prefix + str(id) + '.gpkg'

        # Load shapefile
        shp_temp = QgsVectorLayer(os.path.join(shape_path, name_shp))

        # Output path
        name_shp = dest_prefix + str(id) + '.gpkg'
        shp_out_path = os.path.join(shape_path, name_shp)

        processing.run("grass7:v.generalize", {'input': shp_temp,'type':[0,1,2],'method':0,'threshold':simplify_threshold,'look_ahead':7,
            'reduction':50,'slide':0.5,'angle_thresh':3,'degree_thresh':0,'closeness_thresh':0,'betweeness_thresh':0,
            'alpha':1,'beta':1,'iterations':1,'-t':False,'-l':True,'output':shp_out_path,
            'error':'TEMPORARY_OUTPUT','GRASS_REGION_PARAMETER':None,'GRASS_SNAP_TOLERANCE_PARAMETER':-1,
            'GRASS_MIN_AREA_PARAMETER':0.0001,'GRASS_OUTPUT_TYPE_PARAMETER':0,'GRASS_VECTOR_DSCO':'',
            'GRASS_VECTOR_LCO':'','GRASS_VECTOR_EXPORT_NOCAT':False})


def merge_small_polygons(perimeter_dissolve, source_prefix, dest_prefix, min_area_polygons, shape_path):
    '''
    Takes features, prefixes, a minimum area and a path. 
    Merges all features smaller than minimum area with best suited neighbor.
    Saves new features as shapefile.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']
        name_shp = source_prefix + str(id) + '.gpkg'

        # Load shapefile
        shp_temp = QgsVectorLayer(os.path.join(shape_path, name_shp))

        # Build Feature dictionary
        feature_dict = {f.id(): f for f in shp_temp.getFeatures()}
        
        # Iterate over Polygons that are too small and merge them with neighbors
        finished = False
        while finished == False:
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
                
                for i in [1,2,3,4,5,0,93,94,95,96,97,98,99]:
                    bool_diff = [x == i or x==-i for x in diff_es]
                    ids_ok = [neighbors[i] for i, x in enumerate(bool_diff) if x]
                    if len(ids_ok)>0:
                        area_ok = [areas[i] for i in ids_ok]
                        id_best = ids_ok[np.argmax(area_ok)]
                        es_best = es[id_best]
                        feature_best_neighbor = feature_dict[id_best]
                        feature_combined = feature_best_neighbor.geometry().combine(feature_sel.geometry())
                        f = QgsFeature(shp_temp.fields())
                        f.setGeometry(feature_combined)
                        f.setAttributes([0, es_best])
                        f.setId(id_best)
                        feature_dict[id_best] = f
                        del feature_dict[id_feature]
                        break
                        
            else:
                finished = True

        name_shp = dest_prefix + str(id) + '.gpkg'
        shp_out_path = os.path.join(shape_path, name_shp)
        save_feature_dict(feature_dict, shp_temp, shp_out_path)



