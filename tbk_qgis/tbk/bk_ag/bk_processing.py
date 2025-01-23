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
                        QgsWkbTypes,
                        QgsProcessingFeatureSourceDefinition,
                        QgsFeatureRequest,
                        QgsProject,
                        QgsRasterLayer)
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
    '''Takes a shapefile and its (adapted) feature dictionary. Saves the feature dictionary as a shapefile.'''
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    #save_options.driverName = "ESRI Shapefile"
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
        name_shp = source_prefix + str(id) + '.shp'

        # Load shapefile
        shp_temp = QgsVectorLayer(os.path.join(shape_path, name_shp))

        # Output path
        name_shp = dest_prefix + str(id) + '.shp'
        shp_out_path = os.path.join(shape_path, name_shp)

        processing.run("grass7:v.generalize", {'input': shp_temp,'type':[0,1,2],'method':0,'threshold':simplify_threshold,'look_ahead':7,
            'reduction':50,'slide':0.5,'angle_thresh':3,'degree_thresh':0,'closeness_thresh':0,'betweeness_thresh':0,
            'alpha':1,'beta':1,'iterations':1,'-t':False,'-l':True,'output':shp_out_path,
            'error':'TEMPORARY_OUTPUT','GRASS_REGION_PARAMETER':None,'GRASS_SNAP_TOLERANCE_PARAMETER':-1,
            'GRASS_MIN_AREA_PARAMETER':0.0001,'GRASS_OUTPUT_TYPE_PARAMETER':0,'GRASS_VECTOR_DSCO':'',
            'GRASS_VECTOR_LCO':'','GRASS_VECTOR_EXPORT_NOCAT':False})


def clip_polygons(perimeter_dissolve, source_prefix, dest_prefix, shape_path):
    '''
    Takes features, prefixes, a minimum area and a path. 
    Simplifies the geometry of all features.
    Saves new features as shapefile.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']
        name_shp = source_prefix + str(id) + '.shp'

        # Load shapefile
        shp_temp = QgsVectorLayer(os.path.join(shape_path, name_shp))

        # Output path
        name_shp = dest_prefix + str(id) + '.shp'
        shp_out_path = os.path.join(shape_path, name_shp)

        # Create a temporary layer for the current perimeter feature
        perimeter_layer = QgsVectorLayer('Polygon?crs=' + shp_temp.crs().toWkt(), 'perimeter_layer', 'memory')
        provider = perimeter_layer.dataProvider()
        provider.addFeatures([perimeter])

        # Buffer to remove small errors
        shp_buf = processing.run("native:buffer", {'INPUT':shp_temp,'DISTANCE':1e-05,'SEGMENTS':5,'END_CAP_STYLE':0,
            'JOIN_STYLE':0,'MITER_LIMIT':2,'DISSOLVE':False,'OUTPUT':'TEMPORARY_OUTPUT'})
        
        processing.run("native:clip", {'INPUT':shp_buf['OUTPUT'],'OVERLAY':perimeter_layer,'OUTPUT':shp_out_path})



def merge_small_polygons(perimeter_dissolve, source_prefix, dest_prefix, min_area_polygons, shape_path):
    '''
    Takes features, prefixes, a minimum area and a path. 
    Merges all features smaller than minimum area with best suited neighbor.
    Saves new features as shapefile.
    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']
        name_shp = source_prefix + str(id) + '.shp'

        # Load shapefile
        shp_temp = QgsVectorLayer(os.path.join(shape_path, name_shp))

        # Build Feature dictionary
        feature_dict = {f.id(): f for f in shp_temp.getFeatures()}
        
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
                        f = QgsFeature(shp_temp.fields())
                        f.setGeometry(feature_combined)
                        f.setAttributes([0, es_best])
                        f.setId(id_best)
                        feature_dict[id_best] = f
                        del feature_dict[id_feature]
                        break
                        
            else:
                finished = 0

            finished -= 1

        name_shp = dest_prefix + str(id) + '.gpkg'
        shp_out_path = os.path.join(shape_path, name_shp)
        save_feature_dict(feature_dict, shp_temp, shp_out_path)



def delete_small_polygons(perimeter_dissolve, source_prefix, dest_prefix,shape_path, min_area):
    '''

    '''
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']
        name_shp = source_prefix + str(id) + '.shp'

        # Load shapefile
        shp_temp = QgsVectorLayer(os.path.join(shape_path, name_shp))
        
        # Output path
        name_shp = dest_prefix + str(id) + '.shp'
        shp_out_path = os.path.join(shape_path, name_shp)

        # Create a new memory layer for the filtered features
        fields = shp_temp.fields()
        writer = QgsVectorFileWriter(
            shp_out_path,            
            'UTF-8', fields, QgsWkbTypes.Polygon, shp_temp.crs(),
            driverName="ESRI Shapefile"
        )

        # Iterate through the features and check their area
        for feature in shp_temp.getFeatures():
            geometry = feature.geometry()
            
            # Only process features that have geometry and are polygons (you can add more checks if needed)
            if geometry.isNull():
                continue
            
            # Check if the area is greater than the threshold
            if geometry.area() >= min_area:
                # Write the feature to the new shapefile
                writer.addFeature(feature)
        
        # Close the writer (this saves the new shapefile)
        del writer

 
def buffer_polygons(perimeter_dissolve, source_prefix, dest_prefix,shape_path,buffer_distance):
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']
        name_shp = source_prefix + str(id) + '.shp'

        # Load shapefile
        shp_temp = QgsVectorLayer(os.path.join(shape_path, name_shp))

        # Output path
        name_shp = dest_prefix + str(id) + '.shp'
        shp_out_path = os.path.join(shape_path, name_shp)

        params = {'INPUT': shp_temp, 'DISTANCE': buffer_distance, 'SEGMENTS': 5, 'END_CAP_STYLE': 0, 'JOIN_STYLE': 0,
                'MITER_LIMIT': 2, 'DISSOLVE': False, 'OUTPUT': shp_out_path}
        processing.run("native:buffer", params)


def multipart_to_singlepart(perimeter_dissolve, source_prefix, dest_prefix, shape_path):
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']
        name_shp = source_prefix + str(id) + '.shp'

        # Load shapefile
        shp_temp = QgsVectorLayer(os.path.join(shape_path, name_shp))

        # Output path
        name_shp = dest_prefix + str(id) + '.shp'
        shp_out_path = os.path.join(shape_path, name_shp)

        processing.run('qgis:multiparttosingleparts', {'INPUT':shp_temp, 'OUTPUT':shp_out_path})

def polygon_to_raster(perimeter_dissolve, source_prefix, reference_prefix, dest_prefix, vhm_clipped_path, shape_path):
    for perimeter in perimeter_dissolve.getFeatures():
        id = perimeter['id']
        name_shp = source_prefix + str(id) + '.shp'

        # Load reference raster
        name_tile_source = reference_prefix + str(id) + '.tif'
        vhm_temp = QgsRasterLayer(os.path.join(vhm_clipped_path, name_tile_source))

        extent = vhm_temp.extent()  # Get the extent of the raster (xmin, ymin, xmax, ymax)

        # Load shapefile
        shp_temp = QgsVectorLayer(os.path.join(shape_path, name_shp))

        # Output path
        name_raster = dest_prefix + str(id) + '.tif'
        raster_output_path = os.path.join(vhm_clipped_path, name_raster)
        #output_width = int((extent.xMaximum() - extent.xMinimum()) / resolution_x)
        #output_height = int((extent.yMaximum() - extent.yMinimum()) / resolution_y)
        processing.run("gdal:rasterize", {'INPUT':shp_temp,
                                          'FIELD':'ES','BURN':0,'USE_Z':False,'UNITS':1,'WIDTH':1,'HEIGHT':1,'EXTENT':extent,
                                          'NODATA':0,'OPTIONS':'','DATA_TYPE':0,'INIT':None,'INVERT':False,'EXTRA':'','OUTPUT':raster_output_path})
"""
        processing.run("grass7:v.to.rast", {
            'input':shp_temp,
            'type':[0,1,3],'where':'','use':0,
            'attribute_column':'ES',
            'rgb_column':'','label_column':'','value':1,'memory':300,
            'output':raster_output_path,
            'GRASS_REGION_PARAMETER':None,
            'GRASS_REGION_CELLSIZE_PARAMETER':1,
            'GRASS_RASTER_FORMAT_OPT':'','GRASS_RASTER_FORMAT_META':'',
            'GRASS_SNAP_TOLERANCE_PARAMETER':-1,'GRASS_MIN_AREA_PARAMETER':0.0001})
        
        processing.run("gdal:rasterize", {
            'INPUT': shp_temp,  # Input vector layer (shapefile)
            'FIELD': 'ES',  # Field to rasterize (use the unique ID or geometry field)
            'UNITS': 1,  # 1 for pixels, 0 for map units
            'WIDTH': int((extent.xMaximum() - extent.xMinimum()) / resolution_x),
            'HEIGHT': int((extent.yMaximum() - extent.yMinimum()) / resolution_y),
            'EXTENT': extent,  # Extent from the raster layer
            'CRS': crs.toWkt(),  # CRS from the raster
            'OUTPUT': raster_output_path  # Output path for the rasterized shapefile
        }) 
"""
    