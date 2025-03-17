# -*- coding: utf-8 -*-
"""External call to QGIS to run/test/debug the TBk plugin main algorithm

This script runs TBkAG algorithm in a QGIS application without UI.

Make sure to run this with a Python environment similar (or identical) to the QGIS Python.
The environment needs to know about QGIS, the QGIS Core Plugins (i.e. Processing, GRASS) and the TBk Plugin.
Set your PYTHONPATH accordingly or use sys.path.append to add paths to these modules as needed.
"""

__author__ = 'Raffael Bienz'
__date__ = '2025-02-07'
__copyright__ = '(C) 2025 Raffael Bienz'

import sys
from qgis.core import (
    QgsApplication,
    Qgis
)
import pathlib
import processing

# get git revision hash
# https://stackoverflow.com/a/56245722/6409572
def get_git_revision(base_path, short=True):
    git_dir = pathlib.Path(base_path) / '.git'
    with (git_dir / 'HEAD').open('r') as head:
        ref = head.readline().split(' ')[-1].strip()

    with (git_dir / ref).open('r') as git_hash:
        if short:
            return git_hash.readline().strip()[:8]
        else:
            return git_hash.readline().strip()

# Path to the TBk plugin folder/repository, containing plugin code and test data
tbk_path = 'C:/Auswertungen/TBk_AG/TBk'

# The path to the plugin is environment specific
# Appending it is only necessary if that path is not on the PYTHONPATH. Do so e.g. with:
sys.path.append(tbk_path)

from tbk_qgis.tbk_qgis_provider import TBkProvider

print("\n\n#==============================#")
print("####   TEST TBK ALGORITHM   ####")
print(f"#### git revision: {get_git_revision(tbk_path)} ####")
print("####------------------------####")
print("# imported TBk Provider")
print("# init QGIS Application")

# initialize QGIS Application
# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix
QgsApplication.setPrefixPath('C:/OSGeo4W/apps/qgis-ltr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

print("# load & init Processing")
# The path to the QGIS processing plugin (core) is environment specific
# Appending it is only necessary if that path is not on the PYTHONPATH. Do so e.g. with:
# sys.path.append('C:/OSGeo4W/apps/qgis-ltr/python/plugins')
from processing.core.Processing import Processing
Processing.initialize()

# Add TBk Plugin Provider so that the QGIS instance knows about it's algorithms
provider = TBkProvider()
QgsApplication.processingRegistry().addProvider(provider)
QgsApplication.processingRegistry().providers()
QgsApplication.processingRegistry().removeProvider("0")
# Get versions of tools
print("####------------------------####")
from grassprovider.Grass7Utils import Grass7Utils
from processing.algs.gdal.GdalUtils import GdalUtils
print(f"# QGIS Version: {Qgis.QGIS_VERSION}")
print(f"# Python Version: {sys.version}")
print(f"# GRASS Version: {Grass7Utils.installedVersion()}")
print(f"# GDAL Version: {GdalUtils.version()}")
print("#==============================#\n")
print("####  call TBk Algorithm    ####")
print("#------------------------------#\n\n")

# Main call of the algorithm
processing.run("TBk:Generate BK AG", {
    'VHM': f'{tbk_path}/data/ag_data/vhm_test.tif',
    'roads': f'{tbk_path}/data/ag_data/strassen_test.gpkg',
    #roads':None,
    'perimeter': f'{tbk_path}/data/ag_data/wa_test.gpkg',
    'field_dissolve': 'Eigentue_1',
    'window_size_all': 25,
    'window_size_sh1': 5,
    'weighting_sh1': 40, 
    'shrink_distance': 8,
    'sieve_threshold': 200,
    'min_area_bk': 2000, 
    'min_area_perimeter': 1000, 
    'simplify_threshold': 6,
    'limit_ju': 7, 
    'limit_sh1': 14, 
    'limit_sh2': 20, 
    'limit_bh1': 25, 
    'limit_bh2': 30,
    'output_root': f'{tbk_path}/data/ag_data/test_output',
    'output_format': 0,
    'del_tmp': True})

