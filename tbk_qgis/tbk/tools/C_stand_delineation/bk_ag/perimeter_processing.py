######################################################################
# Functions for perimeter processing
# 07.12.2022
# (C) Raffael Bienz
######################################################################
import numpy as np
import os.path
from qgis.core import (QgsFeature)
from .bk_processing import *


def dissolve_perimeter (perimeter_split, min_area_polygons, shp_out_path):
    '''
    Takes features, a minimum area and a path.
    Dissolves the features smaller than minimum area. 
    Saves the new features as shapefile.
    '''
    feature_dict = {f.id(): f for f in perimeter_split.getFeatures()}
    areas=get_areas(feature_dict)
    areas_too_small = [i for i in areas if areas[i]<min_area_polygons]


    for id_feature in areas_too_small:
        feature_sel = feature_dict[id_feature]
        neighbors = find_neighbors(feature_dict, id_feature)
        neighbors_area = []

        for neighbor in neighbors:
            feature_neighbor = feature_dict[neighbor]
            neighbors_area.append(feature_neighbor.geometry().area())
                
        id_best = neighbors[np.argmax(neighbors_area)]
        feature_best_neighbor = feature_dict[id_best]
        feature_combined = feature_best_neighbor.geometry().combine(feature_sel.geometry())
        f = QgsFeature(perimeter_split.fields())
        f.setGeometry(feature_combined)
        f.setId(id_best)
        f.setAttributes(feature_best_neighbor.attributes())
        feature_dict[id_best] = f
        del feature_dict[id_feature]

    save_feature_dict (feature_dict, perimeter_split, shp_out_path)

