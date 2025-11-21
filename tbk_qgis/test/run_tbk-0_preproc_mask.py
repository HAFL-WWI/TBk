# -*- coding: utf-8 -*-
"""External call to QGIS to run/test/debug the TBk plugin main algorithm

This script runs TBk algorithm in a QGIS application without UI.

Make sure to run this with a Python environment similar (or identical) to the QGIS Python.
The environment needs to know about QGIS, the QGIS Core Plugins (i.e. Processing, GRASS) and the TBk Plugin.
Set your PYTHONPATH accordingly or use sys.path.append to add paths to these modules as needed.
"""

__author__ = 'Berner Fachhochschule HAFL'
__date__ = '2025-11-21'
__copyright__ = '(C) 2025 by Berner Fachhochschule HAFL'

import sys
from qgis.core import (
    QgsApplication,
    Qgis
)
import pathlib


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
tbk_path = 'C:/dev/hafl/TBk'

# The path to the plugin is environment specific
# Appending it is only necessary if that path is not on the PYTHONPATH. Do so e.g. with:
sys.path.append(tbk_path)
from tbk_qgis.tbk_qgis_provider import TBkProvider

print("\n\n#==============================#")
print("####   TEST TBK ALGORITHM   ####")
# print(f"#### git revision: {get_git_revision(tbk_path)} ####")
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

print("####------------------------####")
from grassprovider.grass_utils import GrassUtils
from processing.algs.gdal.GdalUtils import GdalUtils

print(f"# QGIS Version: {Qgis.QGIS_VERSION}")
print(f"# Python Version: {sys.version}")
from grassprovider.grass_utils import GrassUtils

print(f"# GDAL Version: {GdalUtils.version()}")
print("#==============================#\n")
print("####  call TBk Algorithm    ####")
print("#------------------------------#\n\n")

import processing

# two tests with input including geometry types MULTIPOLYGON & MULTISURFACE

# 1) default settings
processing.run(
    "TBk:TBk prepare mask",
    {
        'mask': f'{tbk_path}/data/basedata/FB24_demogebiete_with_MULTISURFACE.gpkg',
        'dissolve': True,
        'dissolve_fields': [],
        'fid_original': 'fid_original',
        'return_single_parts': True,
        'min_area': 100,
        'max_hole_size_to_remove': 10,
        'min_width': 10,
        'OUTPUT': f'{tbk_path}/data/tbk_test_output/processed_mask_default.gpkg'
    })

# 2) dissolve by attributes fid, DIS & ABT of mask input
processing.run(
    "TBk:TBk prepare mask",
    {
        'mask': f'{tbk_path}/data/basedata/FB24_demogebiete_with_MULTISURFACE.gpkg',
        'dissolve': True,
        'dissolve_fields': ['fid', 'DIS', 'ABT'],
        'fid_original': 'fid_original',
        'return_single_parts': False,
        'min_area': 100,
        'max_hole_size_to_remove': 10,
        'min_width': 10,
        'OUTPUT': f'{tbk_path}/data/tbk_test_output/processed_mask_dissolved_by_fid_DIS_ABT.gpkg'
    })
