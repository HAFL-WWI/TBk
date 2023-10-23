# -*- coding: utf-8 -*-
"""External call to QGIS to test whether GRASS is correctly loaded

This script runs QGIS application without UI and probes a grass algorithm to check if GRASS is loaded.

Make sure to run this with a Python environment similar (or identical) to the QGIS Python.
The environment needs to know about QGIS, the QGIS Core Plugins (i.e. Processing, GRASS).
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

# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix
QgsApplication.setPrefixPath('C:/OSGeo4W/apps/qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

import processing
from grassprovider.Grass7AlgorithmProvider import Grass7AlgorithmProvider

processing.core.Processing.Processing.initialize()
print(f'Number of registered algorithms = {len(QgsApplication.processingRegistry().algorithms())}')

# Note: Adding the Grass7AlgorithmProvider shouldn't have an effect anymore.
# It should be loaded by default in QGIS 3.24 or higher.
# See https://github.com/qgis/QGIS/pull/47114
QgsApplication.processingRegistry().addProvider(Grass7AlgorithmProvider())
print(f'Number of registered algorithms = {len(QgsApplication.processingRegistry().algorithms())}')

processing.algorithmHelp('grass7:v.dissolve')  # fail if "Algorithm "grass7:r.clump" not found."
