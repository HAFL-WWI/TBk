#######################################################################
# Reclassify function, because not fully provided by gdal
#
# (C) Dominique Weber, Christoph Schaller, HAFL
#######################################################################

from osgeo.gdalconst import *
from osgeo.gdalnumeric import *
import numpy as np

class PreProcessingHelper:
    ################################################
    # Reclassify all values outside min-max to min or max
    # Compress with LZW
    @staticmethod
    def reclassify_min_max(in_raster, out_raster, min_value, max_value):
        # Open the dataset
        ds = gdal.Open(in_raster, GA_ReadOnly)
        b1 = ds.GetRasterBand(1)
        vNA = b1.GetNoDataValue()
        dataIn = np.array(b1.ReadAsArray())

        # Clean outliers
        dataOut = np.copy(dataIn)
        dataOut[(dataOut < min_value) & (dataOut != vNA)] = min_value
        dataOut[(dataOut > max_value) & (dataOut != vNA)] = max_value

        # Write the out file
        driver = gdal.GetDriverByName("GTiff")
        dst_options = ['COMPRESS=LZW']
        dsOut = driver.Create(out_raster, ds.RasterXSize, ds.RasterYSize, 1, b1.DataType, dst_options)
        dsOut.GetRasterBand(1).SetNoDataValue(vNA)
        CopyDatasetInfo(ds, dsOut)
        bandOut = dsOut.GetRasterBand(1)
        BandWriteArray(bandOut, dataOut)
        del ds
        del dsOut

    ################################################
    # Reclassify mixture raster to coniferous proportion (0-100)
    @staticmethod
    def reclassify_mixture(in_raster, out_raster, min_lh, max_lh, min_nh, max_nh):
        # Open the dataset
        ds = gdal.Open(in_raster, GA_ReadOnly)
        b1 = ds.GetRasterBand(1)
        vNA = b1.GetNoDataValue()
        dataIn = np.array(b1.ReadAsArray())

        # Clean outliers
        dataOut = np.copy(dataIn)
        dataOut[(dataOut >= min_lh) & (dataOut <= max_lh)] = 0
        dataOut[(dataOut > min_nh) & (dataOut <= max_nh)] = 100

        # Write the out file
        driver = gdal.GetDriverByName("GTiff")
        dst_options = ['COMPRESS=LZW']
        dsOut = driver.Create(out_raster, ds.RasterXSize, ds.RasterYSize, 1, b1.DataType, dst_options)
        dsOut.GetRasterBand(1).SetNoDataValue(vNA)
        CopyDatasetInfo(ds, dsOut)
        bandOut = dsOut.GetRasterBand(1)
        BandWriteArray(bandOut, dataOut)
        del ds
        del dsOut

    ################################################
    # Get raster resolution (pixel size)
    @staticmethod
    def get_raster_resolution(in_raster):
        ds = gdal.Open(in_raster, GA_ReadOnly)
        return ds.GetGeoTransform()[1], ds.GetGeoTransform()[1]

    ################################################
    # Get raster extent (xmin, ymin, xmax, ymax)
    @staticmethod
    def get_raster_extent(in_raster):
        ds = gdal.Open(in_raster, GA_ReadOnly)
        xmin, xres, xskew, ymax, yskew, yres = ds.GetGeoTransform()
        xmax = xmin + (ds.RasterXSize * xres)
        ymin = ymax + (ds.RasterYSize * yres)
        return xmin, ymin, xmax, ymax


