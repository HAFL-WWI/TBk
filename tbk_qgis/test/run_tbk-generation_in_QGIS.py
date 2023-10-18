# -*- coding: utf-8 -*-
"""QGIS call to run/test/debug the TBk plugin main algorithm

This script runs TBk algorithm in a QGIS application.
"""

__author__ = 'Berner Fachhochschule HAFL'
__date__ = '2023-10-18'
__copyright__ = '(C) 2023 by Berner Fachhochschule HAFL'

import processing

# Main call of the algorithm
# paths to files are exemplary here and need to be adjusted to the local system
processing.run("TBk:Generate BK",
               {'vhm_10m':'C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/TBk_main/vhm_10m.tif',
                'vhm_150cm':'C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/TBk_main/vhm_150cm.tif',
                'coniferous_raster':'C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/TBk_main/MG.tif',
                'perimeter':'C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/perimeter_test_waldgebiet.shp|layername=perimeter_test_waldgebiet',
                'output_root':'C:\\Users\\hbh1\\Projects\\H07_TBk\\Dev\\TBk_QGIS_Plugin\\data\\TBk_main',
                'useConiferousRasterForClassification':True,
                'logfile_name':'tbk_processing.log',
                'description':'TBk dataset',
                'min_tol':0.1,'max_tol':0.1,'min_corr':4,'max_corr':4,
                'min_valid_cells':0.5,'min_cells_per_stand':10,'min_cells_per_pure_stand':30,
                'vhm_min_height':0,'vhm_max_height':60,
                'simplification_tolerance':8,'min_area_m2':1000,
                'similar_neighbours_min_area':2000,'similar_neighbours_hdom_diff_rel':0.15,
                'calc_mixture_for_main_layer':True,
                'del_tmp':True})