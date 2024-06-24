# -*- coding: utf-8 -*-
"""External call to QGIS to run/test/debug the TBk plugin main algorithm

This script runs TBk algorithm in a QGIS application without UI.

Make sure to run this with a Python environment similar (or identical) to the QGIS Python.
The environment needs to know about QGIS, the QGIS Core Plugins (i.e. Processing, GRASS) and the TBk Plugin.
Set your PYTHONPATH accordingly or use sys.path.append to add paths to these modules as needed.
"""

__author__ = 'Berner Fachhochschule HAFL'
__date__ = '2023-10-18'
__copyright__ = '(C) 2023 by Berner Fachhochschule HAFL'

import sys
from qgis.core import (
    QgsApplication,
    QgsProcessingFeedback,
    QgsVectorLayer
)

# Path to the TBk plugin folder/repository, containing plugin code and test data
tbk_path = 'C:/dev/hafl/TBk'

# The path to the plugin is environment specific
# Appending it is only necessary if that path is not on the PYTHONPATH. Do so e.g. with:
sys.path.append(tbk_path)
from tbk_qgis.tbk_qgis_provider import TBkProvider

# initialize QGIS Application
# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix
QgsApplication.setPrefixPath('C:/OSGeo4W/apps/qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

# The path to the QGIS processing plugin (core) is environment specific
# Appending it is only necessary if that path is not on the PYTHONPATH. Do so e.g. with:
# sys.path.append('C:/OSGeo4W/apps/qgis-ltr/python/plugins')
import processing
from processing.core.Processing import Processing

Processing.initialize()

# Add TBk Plugin Provider so that the QGIS instance knows about it's algorithms
provider = TBkProvider()
QgsApplication.processingRegistry().addProvider(provider)

# Main call of the algorithm
processing.run("TBk:TBk postprocess local density", {
    'path_tbk_input': f'{tbk_path}/data/tbk_2012/20240619-1704_tbk_test_reference',
    'mg_use': True, 'mg_input': f'{tbk_path}/data/tbk_2012/MG_10m.tif',
    'tbk_input_file': 'TBk_Bestandeskarte.gpkg',
    # 'output_suffix': '',
    'table_density_classes': [
        1, 85, 100, 'False',
        2, 60, 85, 'True',
        3, 40, 60, 'True',
        4, 25, 40, 'True',
        5, 0, 25, 'False',
        12, 60, 100, 'True'
    ],
    'calc_all_dg': True, 'mw_rad': 7, 'mw_rad_large': 14,
    'min_size_clump': 1200, 'min_size_stand': 1200, 'holes_thresh': 400, 'buffer_smoothing': True,
    'buffer_smoothing_dist': 7})