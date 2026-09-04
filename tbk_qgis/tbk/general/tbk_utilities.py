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
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant
from qgis.utils import iface
from qgis.core import QgsProject
from qgis.core import *

import os
import sys
import logging
import processing
import time
from datetime import timedelta

from osgeo import ogr
from osgeo import gdal
from osgeo import osr


class SubprocessTimer:
    """
    Timed, indented "Start <label> / ---- / [<tag> elapsed] step ... / Finished <label>
    (elapsed) / ----" block for a verbose subprocess, printed to `feedback` (Processing panel)
    and, if given, a Python `log`ger - so a long-running subprocess (e.g. CreateProject, local
    density, a region within Generate BK Regionwise) reads as a distinct, self-contained block
    within the enclosing workflow's own [W ...]-tagged timeline, rather than an undifferentiated
    stream of messages. `tag` distinguishes this block's own elapsed-time lines from the
    workflow's and from other subprocesses' (e.g. "R" for a region, "C" for CreateProject).
    """
    WRAP = "-" * 28

    def __init__(self, feedback, label, tag, log=None, indent=''):
        self.feedback = feedback
        self.log = log
        self.label = label
        self.tag = tag
        self.indent = indent
        self._start = time.time()
        self._emit("")  # blank line separates this block's start from whatever precedes it
        self._emit(f"Start {self.label}")
        self._emit(self.WRAP)

    def _elapsed(self):
        return str(timedelta(seconds=round(time.time() - self._start)))

    def _emit(self, msg):
        line = f"{self.indent}{msg}"
        if self.feedback is not None:
            self.feedback.pushInfo(line)
        if self.log is not None:
            self.log.info(line)

    def step(self, msg):
        """Logs one tagged, elapsed-time-stamped line within this subprocess block."""
        self._emit(f"[{self.tag} {self._elapsed()}] {msg}")

    def finish(self):
        """Closes the block with a "Finished <label> (elapsed)" line and a trailing wrap."""
        self._emit(f"Finished {self.label} ({self._elapsed()})")
        self._emit(self.WRAP)


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
def copy_raster_tiff(in_raster, out_raster, gdal_create_options='COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9'):
    driver = gdal.GetDriverByName('GTiff')
    in_ds = gdal.Open(in_raster)
    out_ds = driver.CreateCopy(out_raster, in_ds, 0, options=gdal_co_to_list(gdal_create_options))
    in_ds = None
    out_ds = None


def gdal_co_to_extra(options_str):
    """Convert pipe-separated OPTIONS string to -co flags for GDAL EXTRA parameter."""
    if not options_str:
        return ''
    return ' '.join(f'-co {opt}' for opt in options_str.split('|'))


def gdal_co_to_list(options_str):
    """Convert pipe-separated OPTIONS string to list for GDAL Python API options parameter."""
    if not options_str:
        return []
    return options_str.split('|')

# Function to copy a vector file elsewhere
def copy_vector_file(input_path: str, output_path: str, context: QgsProcessingContext, feedback: QgsProcessingFeedback, is_child_algorithm=True) -> str:
    return processing.run("native:savefeatures",
                          {'INPUT': input_path, 'OUTPUT': output_path},
                          context=context,
                          feedback=feedback,
                          is_child_algorithm=is_child_algorithm
                          )['OUTPUT']

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


def finalize_TBk(input_layer, output_layer):
    """
    Normalize the final TBk stand map schema (field types/order via native:refactorfields),
    calculate the PH_STRUCTURE forest structure classification field, and recalculate
    area_m2 from current geometry. Writes the result to output_layer.
    """
    processingResult = processing.run("native:refactorfields", {
        'INPUT': input_layer,
        'FIELDS_MAPPING': [
            {'alias': '', 'comment': '', 'expression': '"fid"', 'length': 0, 'name': 'fid', 'precision': 0,
             'sub_type': 0, 'type': 4, 'type_name': 'int8'},
            {'alias': '', 'comment': '', 'expression': '"ID"', 'length': 0, 'name': 'ID', 'precision': 0, 'sub_type': 0,
             'type': 10, 'type_name': 'text'},
            {'alias': '', 'comment': '', 'expression': '"hmax"', 'length': 0, 'name': 'hmax', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"hdom"', 'length': 0, 'name': 'hdom', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG"', 'length': 0, 'name': 'DG', 'precision': 0, 'sub_type': 0,
             'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"NH"', 'length': 0, 'name': 'NH', 'precision': 0, 'sub_type': 0,
             'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"area_m2"', 'length': 0, 'name': 'area_m2', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"type"', 'length': 1000, 'name': 'type', 'precision': 0,
             'sub_type': 0, 'type': 10, 'type_name': 'text'},
            {'alias': '', 'comment': '', 'expression': '"DG_ks"', 'length': 0, 'name': 'DG_ks', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG_us"', 'length': 0, 'name': 'DG_us', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG_ms"', 'length': 0, 'name': 'DG_ms', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG_os"', 'length': 0, 'name': 'DG_os', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG_ueb"', 'length': 0, 'name': 'DG_ueb', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"NH_OS"', 'length': 0, 'name': 'NH_OS', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"VegZone_Code"', 'length': 0, 'name': 'VegZone_Code',
             'precision': 0, 'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"ID_meta"', 'length': 0, 'name': 'ID_meta', 'precision': 0,
             'sub_type': 0, 'type': 10, 'type_name': 'text'},
            {'alias': '', 'comment': '', 'expression': '"ID_pre_merge"', 'length': 0, 'name': 'ID_pre_merge',
             'precision': 0, 'sub_type': 0, 'type': 4, 'type_name': 'int8'}], 'OUTPUT': 'TEMPORARY_OUTPUT'})

    processingResult = processing.run("native:fieldcalculator", {
        'INPUT': processingResult['OUTPUT'],
        'FIELD_NAME': 'PH_STRUCTURE', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
        'FORMULA': 'if("VegZone_Code" IN (-1, 0, 1, 2, 4, 5), \r\n    if("NH">50,\r\n        if("hdom">=26, \r\n            if("DG_os" + "DG_ueb" >= 45, \r\n                if("DG_ms" >= 35,\r\n                4,\r\n                    if("DG_ms">=25,\r\n                        if("DG_us" >=20,\r\n                            3,\r\n                            2\r\n                        ),\r\n                        if("DG_ms">=15,\r\n                            if("DG_us">=10,\r\n                                2,\r\n                                1\r\n                            ),\r\n                            if("DG_us">=10,\r\n                                1,\r\n                                0\r\n                            )\r\n                        )\r\n                    )\r\n                ),\r\n                5\r\n            ), \r\n            if("hdom">18,\r\n                -1, \r\n                if("hdom">10,\r\n                    -2,\r\n                    -3\r\n                )\r\n            )\r\n        ),\r\n        if("hdom">=23, \r\n            if("DG_os" + "DG_ueb" >= 45, \r\n                if("DG_ms" >= 35,\r\n                    4,\r\n                    if("DG_ms">=25,\r\n                        if("DG_us" >=20,\r\n                            3,\r\n                            2\r\n                        ),\r\n                        if("DG_ms">=15,\r\n                            if("DG_us">=10,\r\n                                2,\r\n                                1\r\n                            ),\r\n                            if("DG_us">=10,\r\n                                1,\r\n                                0\r\n                            )\r\n                        )\r\n                    )\r\n                ),\r\n            5), \r\n            if("hdom">16,\r\n                -1, \r\n                if("hdom">9,\r\n                    -2,\r\n                    -3\r\n                )\r\n            )\r\n        )\r\n    ),\r\n    if ("VegZone_Code" IN (6, 7),\r\n        if("NH">50,\r\n            if("hdom">=23, \r\n                if("DG_os" + "DG_ueb" >= 45, \r\n                    if("DG_ms" >= 35,\r\n                    4,\r\n                        if("DG_ms">=25,\r\n                            if("DG_us" >=20,\r\n                                3,\r\n                                2\r\n                            ),\r\n                            if("DG_ms">=15,\r\n                                if("DG_us">=10,\r\n                                    2,\r\n                                    1\r\n                                ),\r\n                                if("DG_us">=10,\r\n                                    1,\r\n                                    0\r\n                                )\r\n                            )\r\n                        )\r\n                    ),\r\n                    5\r\n                ), \r\n                if("hdom">16,\r\n                    -1, \r\n                    if("hdom">9,\r\n                        -2,\r\n                        -3\r\n                    )\r\n                )\r\n            ),\r\n            if("hdom">=19, \r\n                if("DG_os" + "DG_ueb" >= 45, \r\n                    if("DG_ms" >= 35,\r\n                        4,\r\n                        if("DG_ms">=25,\r\n                            if("DG_us" >=20,\r\n                                3,\r\n                                2\r\n                            ),\r\n                            if("DG_ms">=15,\r\n                                if("DG_us">=10,\r\n                                    2,\r\n                                    1\r\n                                ),\r\n                                if("DG_us">=10,\r\n                                    1,\r\n                                    0\r\n                                )\r\n                            )\r\n                        )\r\n                    ),\r\n                5), \r\n                if("hdom">13,\r\n                    -1, \r\n                    if("hdom">7,\r\n                        -2,\r\n                        -3\r\n                    )\r\n                )\r\n            )\r\n        ),\r\n        if("VegZone_Code" IN (8),\r\n            if("NH">50,\r\n                if("hdom">=19, \r\n                    if("DG_os" + "DG_ueb" >= 45, \r\n                        if("DG_ms" >= 35,\r\n                        4,\r\n                            if("DG_ms">=25,\r\n                                if("DG_us" >=20,\r\n                                    3,\r\n                                    2\r\n                                ),\r\n                                if("DG_ms">=15,\r\n                                    if("DG_us">=10,\r\n                                        2,\r\n                                        1\r\n                                    ),\r\n                                    if("DG_us">=10,\r\n                                        1,\r\n                                        0\r\n                                    )\r\n                                )\r\n                            )\r\n                        ),\r\n                        5\r\n                    ), \r\n                    if("hdom">13,\r\n                        -1, \r\n                        if("hdom">7,\r\n                            -2,\r\n                            -3\r\n                        )\r\n                    )\r\n                ),\r\n                if("hdom">=16, \r\n                    if("DG_os" + "DG_ueb" >= 45, \r\n                        if("DG_ms" >= 35,\r\n                            4,\r\n                            if("DG_ms">=25,\r\n                                if("DG_us" >=20,\r\n                                    3,\r\n                                    2\r\n                                ),\r\n                                if("DG_ms">=15,\r\n                                    if("DG_us">=10,\r\n                                        2,\r\n                                        1\r\n                                    ),\r\n                                    if("DG_us">=10,\r\n                                        1,\r\n                                        0\r\n                                    )\r\n                                )\r\n                            )\r\n                        ),\r\n                    5), \r\n                    if("hdom">11,\r\n                        -1, \r\n                        if("hdom">6,\r\n                            -2,\r\n                            -3\r\n                        )\r\n                    )\r\n                )\r\n            ),\r\n            if("NH">50,\r\n                if("hdom">=16, \r\n                    if("DG_os" + "DG_ueb" >= 45, \r\n                        if("DG_ms" >= 35,\r\n                        4,\r\n                            if("DG_ms">=25,\r\n                                if("DG_us" >=20,\r\n                                    3,\r\n                                    2\r\n                                ),\r\n                                if("DG_ms">=15,\r\n                                    if("DG_us">=10,\r\n                                        2,\r\n                                        1\r\n                                    ),\r\n                                    if("DG_us">=10,\r\n                                        1,\r\n                                        0\r\n                                    )\r\n                                )\r\n                            )\r\n                        ),\r\n                        5\r\n                    ), \r\n                    if("hdom">11,\r\n                        -1, \r\n                        if("hdom">6,\r\n                            -2,\r\n                            -3\r\n                        )\r\n                    )\r\n                ),\r\n                if("hdom">=13, \r\n                    if("DG_os" + "DG_ueb" >= 45, \r\n                        if("DG_ms" >= 35,\r\n                            4,\r\n                            if("DG_ms">=25,\r\n                                if("DG_us" >=20,\r\n                                    3,\r\n                                    2\r\n                                ),\r\n                                if("DG_ms">=15,\r\n                                    if("DG_us">=10,\r\n                                        2,\r\n                                        1\r\n                                    ),\r\n                                    if("DG_us">=10,\r\n                                        1,\r\n                                        0\r\n                                    )\r\n                                )\r\n                            )\r\n                        ),\r\n                    5), \r\n                    if("hdom">9,\r\n                        -1, \r\n                        if("hdom">5,\r\n                            -2,\r\n                            -3\r\n                        )\r\n                    )\r\n                )\r\n            )\r\n        )\r\n    )\r\n)\r\n\r\n',
        'OUTPUT': 'TEMPORARY_OUTPUT'})

    processing.run("native:fieldcalculator", {
        'INPUT': processingResult['OUTPUT'],
        'FIELD_NAME': 'area_m2', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
        'FORMULA': '$area',
        'OUTPUT': output_layer})
