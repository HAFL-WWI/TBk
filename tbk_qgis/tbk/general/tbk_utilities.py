# -*- coding: utf-8 -*-
# *************************************************************************** #
# Helper Classes and Functions for TBk.
#
# (C) Hannes Horneber, Dominique Weber, Christoph Schaller (BFH-HAFL)
# *************************************************************************** #
"""
/***************************************************************************
    TBk: Toolkit Bestandeskarte (QGIS Plugin)
    Toolkit for the generating and processing forest stand maps
    Copyright (C) 2025 BFH-HAFL (hannes.horneber@bfh.ch, christian.rosset@bfh.ch)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
 ***************************************************************************/
"""
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from qgis import core
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import QVariant
from qgis.utils import iface
from qgis.core import QgsProject
from qgis.core import *

import os
import sys
import logging

from osgeo import ogr
from osgeo import gdal
from osgeo import osr


def ensure_dir(path):
    """Function to ensure that a directory exists
    (creates directory if non existent)

    :param path: Path of directory to check
    """
    if not os.path.isdir(path):
        return os.makedirs(path, exist_ok=True)


# File removal with graceful error handling (avoid error interrupts)
def os_remove_graceful(file_path):
    if file_path:  # Ensure the variable is not None or empty
        if os.path.exists(file_path):  # Check if the file exists
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Could not delete {file_path}: {e}")
        else:
            print(f"File does not exist, skipping: {file_path}")
    else:
        print("No file path provided, skipping.")


# Function that deletes an existing Geotiff
def delete_raster(raster):
    data = gdal.Open(raster, gdal.GA_ReadOnly)
    driver = data.GetDriver()
    data = None
    if os.path.exists(raster):
        driver.Delete(raster)


# Function that deletes an existing Geopackage
def delete_geopackage(path):
    DriverName = "GPKG"
    driver = ogr.GetDriverByName(DriverName)
    if os.path.exists(path):
        driver.DeleteDataSource(path)


# Function that deletes an existing Shapefile
# Based on https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html#delete-a-file
def delete_shapefile(path):
    DriverName = "ESRI Shapefile"
    driver = ogr.GetDriverByName(DriverName)
    if os.path.exists(path):
        driver.DeleteDataSource(path)


# Delete Shapefile
# Code based on https://gis.stackexchange.com/a/190435
def delete_shapefile_old(path):
    realpath = os.path.realpath(path)
    aDir, aFile = os.path.split(realpath)
    fnameNoExt = os.path.splitext(aFile)[0]

    extensions = [".shp", ".shx", ".dbf", ".prj", ".sbn", ".sbx", ".fbn", ".fbx", ".ain", ".aih", ".ixs", ".mxs",
                  ".atx", ".xml", ".cpg", ".qix"]

    theFiles = []
    for f in os.listdir(aDir):
        if os.path.isfile(os.path.join(aDir, f)):
            theFiles.append(os.path.join(aDir, f))

    for f in theFiles:
        theFile = os.path.basename(f)
        name, extension = os.path.splitext(theFile)
        # If the name matches the input file and the extension is in that list, delete it:
        if (name == fnameNoExt or name == fnameNoExt + ".shp") and (
                extension in extensions):  # handles the foo.shp.xml case too.
            os.remove(f)


def get_raster_metadata(raster):
    data = gdal.Open(raster, gdal.GA_ReadOnly)
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    proj = osr.SpatialReference(wkt=data.GetProjection())
    xResolution = geoTransform[1]
    yResolution = geoTransform[5]
    data = None
    return {"extent": [minx, miny, maxx, maxy], "xResolution": abs(xResolution), "yResolution": abs(yResolution),
            "epsg": proj.GetAttrValue('AUTHORITY', 1)}


# Function to copy a GeoTIFF raster
def copy_raster_tiff(in_raster, out_raster):
    driver = gdal.GetDriverByName('GTiff')
    in_ds = gdal.Open(in_raster)
    out_ds = driver.CreateCopy(out_raster, in_ds, 0, options=["COMPRESS=ZSTD"])
    in_ds = None
    out_ds = None


# Function to create and empty copy of a GeoTIFF raster
def create_empty_copy(input_raster, output_raster):
    in_ds = gdal.Open(input_raster)
    driver = in_ds.GetDriver()
    out_ds = driver.Create(output_raster, in_ds.RasterXSize, in_ds.RasterYSize, in_ds.RasterCount,
                           in_ds.GetRasterBand(1).DataType)
    out_ds.SetGeoTransform(in_ds.GetGeoTransform())
    out_ds.SetProjection(in_ds.GetProjection())
    ds = None
    out_ds = None


# Remove fields from QGIS layer
def delete_fields(layer, field_names):
    for f in field_names:
        fIndex = layer.fields().lookupField(f)
        if fIndex >= 0:
            layer.dataProvider().deleteAttributes([fIndex])
            layer.updateFields()


# Remove fields from QGIS layer
def keep_only_specific_fields(layer, fields_to_keep):
    # all_names = [field.name() for field in layer.dataProvider().fields()]
    fields_to_delete = []
    prov = layer.dataProvider()
    for field in prov.fields():
        if not field.name() in fields_to_keep:
            fields_to_delete.append(field.name())

    for f in fields_to_delete:
        fIndex = layer.fields().lookupField(f)
        if fIndex >= 0:
            layer.dataProvider().deleteAttributes([fIndex])
            layer.updateFields()
    # all_names_after = [field.name() for field in layer.dataProvider().fields()]


def getVectorSaveOptions(format, encoding, only_selected_features=False, in_crs=None, out_crs=None):
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = format
    save_options.fileEncoding = encoding
    save_options.onlySelectedFeatures = only_selected_features
    if in_crs and out_crs:
        save_options.ct = QgsCoordinateTransform(in_crs, out_crs, QgsProject.instance())
    return save_options


def dict_diff(a, b):
    """
    Return differences from dictionaries a to b.

    Return a tuple of three dicts: removed, added, changed.
    'removed' has all keys and values removed from a. 'added' has
    all keys and values that were added to b. 'changed' has all
    keys and their values in b that are different from the corresponding
    key in a.

    Source: https://stackoverflow.com/questions/715234/python-dict-update-diff

    :param a: base dictionary
    :param b: updated dictionary
    :return: Return a tuple of three dicts: removed, added , changed (from a to b)
    """

    removed = dict()
    added = dict()
    changed = dict()

    for key, value in a.items():
        if key not in b:
            removed[key] = value
        elif b[key] != value:
            changed[key] = b[key]
    for key, value in b.items():
        if key not in a:
            added[key] = value
    return removed, added, changed


def generate_timestamp_dir(root_dir, prefix='', suffix=''):
    """
    Generate a directory with current timestamp in root_dir
    The directory name may contain a prefix/suffix in addition to the timestamp
    """
    # Set up timestamp and directory name and path
    time = datetime.now().strftime("%Y%m%d-%H%M")
    dir_name = f"{prefix}{time}{suffix}"
    new_directory = os.path.join(root_dir, dir_name)

    # create directory
    ensure_dir(new_directory)

    return new_directory
