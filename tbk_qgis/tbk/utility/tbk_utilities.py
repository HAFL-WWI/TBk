#######################################################################
# Helper Classes and Functions for TBk.
#
# (C) Dominique Weber, Christoph Schaller, HAFL
#######################################################################

from qgis import core
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant
from qgis.utils import iface
from qgis.core import QgsProject
from qgis.core import *

import os
import sys
import logging

from osgeo import ogr
from osgeo import gdal
from osgeo import osr

# Remove fields from QGIS layer
def delete_fields(layer, field_names):
    for f in field_names:
        fIndex = layer.fields().lookupField(f)
        if fIndex >= 0:
            layer.dataProvider().deleteAttributes([fIndex]) 
            layer.updateFields()

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
    return {"extent": [minx, miny, maxx, maxy], "xResolution": abs(xResolution), "yResolution": abs(yResolution), "epsg":proj.GetAttrValue('AUTHORITY',1)}

# Function that deletes an existing Shapefile
#Based on https://pcjericks.github.io/py-gdalogr-cookbook/vector_layers.html#delete-a-file
def delete_shapefile(path):
    DriverName = "ESRI Shapefile"
    driver = ogr.GetDriverByName(DriverName)
    if os.path.exists(path):
        driver.DeleteDataSource(path)

# Function that deletes an existing Geopackage
def delete_geopackage(path):
    DriverName = "GPKG"
    driver = ogr.GetDriverByName(DriverName)
    if os.path.exists(path):
        driver.DeleteDataSource(path)

# Function that deletes an existing Geotiff
def delete_raster(raster):
    data = gdal.Open(raster, gdal.GA_ReadOnly)
    driver = data.GetDriver()
    data = None
    if os.path.exists(raster):
        driver.Delete(raster)

#Function to copy a GeoTIFF raster
def copy_raster_tiff(in_raster, out_raster):
    driver = gdal.GetDriverByName('GTiff')
    in_ds = gdal.Open(in_raster)
    out_ds = driver.CreateCopy(out_raster, in_ds, 0)
    in_ds = None
    out_ds = None

# Delete files
# Code basing on https://gis.stackexchange.com/a/190435
def delete_shapefile_old(path):
    realpath = os.path.realpath(path)
    aDir, aFile = os.path.split(realpath)
    fnameNoExt = os.path.splitext(aFile)[0]

    extensions = [".shp", ".shx", ".dbf", ".prj", ".sbn", ".sbx", ".fbn", ".fbx", ".ain", ".aih", ".ixs", ".mxs", ".atx", ".xml", ".cpg", ".qix"]

    theFiles = []
    for f in os.listdir(aDir):
        if os.path.isfile(os.path.join(aDir, f)):
            theFiles.append(os.path.join(aDir, f))
            
    for f in theFiles:
        theFile = os.path.basename(f)
        name, extension = os.path.splitext(theFile)
        # If the name matches the input file and the extension is in that list, delete it:
        if (name == fnameNoExt or name == fnameNoExt + ".shp") and (extension in extensions): # handles the foo.shp.xml case too.
            os.remove(f)

# Function to ensure that a directory exists
# (creates directory if non existent)
def ensure_dir (path):
    if not os.path.isdir(path):
        os.mkdir(path)

def getVectorSaveOptions(format, encoding, only_selected_features = False, in_crs = None, out_crs = None):
    save_options = QgsVectorFileWriter.SaveVectorOptions()
    save_options.driverName = format
    save_options.fileEncoding = encoding
    save_options.onlySelectedFeatures = only_selected_features
    if in_crs and out_crs:
        save_options.ct =  QgsCoordinateTransform(in_crs, out_crs, QgsProject.instance())
    return save_options

class QgisHandler(logging.Handler):
    feedback = None
    def __init__(self,feedback, *args, **kwargs):
        super(QgisHandler, self).__init__(*args, **kwargs)
        self.feedback=feedback

    def emit(self, record):
        try:
            message = self.format(record)
            # Don't do anything if the StreamHandler does not exist
            if message == None:
                return
            self.feedback.pushInfo(message)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
        
        #QgsMessageLog.logMessage("File "+ii.source()+": all pixels set to no data", tag="Raster Processing", level=QgsMessageLog.INFO )

    #def format(self, record):
    #    try:
    #        message = logging.StreamHandler.format(self, record)
    #    # Catch the case when there is a zombie logger, when re-launching
    #    #  the simulation with 'p'.
    #    # This seems to be caused by an incorrect cleaning on the Builder
    #    except AttributeError as detail:
    #        return None
#
    #    return message