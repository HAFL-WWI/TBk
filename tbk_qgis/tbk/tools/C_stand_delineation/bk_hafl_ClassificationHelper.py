# *************************************************************************** #
# Helper Class for VHM classification.
#
# Authors: Dominique Weber, Christoph Schaller (BFH-HAFL)
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

from osgeo.gdalconst import *
from collections import Counter
import math
import numpy
# from rasterstats import zonal_stats


import processing

from tbk_qgis.tbk.general.tbk_utilities import *


class ClassificationHelper:

    ################################################
    # getSortedList
    @staticmethod
    def getSortedList(data, count):
        rows = data.shape[0]
        cols = data.shape[1]
        dataList = list()
        for y in range(rows):
            for x in range(cols):
                if (data[y, x] > 0):
                    dataList.append([data[y, x], y, x])
        dataList.sort(reverse=True)
        return dataList[:count]

    ################################################
    # getWindowSize
    @staticmethod
    def getWindowSize(value):
        if value < 0:
            value = 0
        pixelsTmp = math.sqrt(value)
        pixels = round(pixelsTmp)
        if pixels % 2 == 0:
            # Even number
            if pixelsTmp - pixels > 0:
                pixels += 1
            else:
                pixels -= 1
        pixels = int(pixels)
        if pixels < 3:
            pixels = int(3)
        return pixels

    ################################################
    # Create polygons (ESRI Shapefile) from classified
    # raster.
    @staticmethod
    def polygonize(raster_file, output_file):
        # Opening the raster file
        ds = gdal.Open(raster_file, GA_ReadOnly)
        band = ds.GetRasterBand(1)
        prj = ds.GetProjection()
        srs = osr.SpatialReference(wkt=prj)

        # Create shapefile and layer
        drv = ogr.GetDriverByName("GPKG")
        dst_ds = drv.CreateDataSource(output_file)
        dst_layer = dst_ds.CreateLayer("Polygonized", srs)

        # add field for stand ID
        dst_fieldname = 'ID'
        fd = ogr.FieldDefn(dst_fieldname, ogr.OFTInteger)
        dst_layer.CreateField(fd)
        dst_field = 0
        # use same raster as mask, this will exclude stands with number 0
        mask_band = band

        # polygonize raster data to shape layer
        # gdal.Polygonize(band, mask_band, dst_layer, dst_field, callback=gdal.TermProgress)
        gdal.Polygonize(band, mask_band, dst_layer, dst_field, callback=None)
        print("File %s saved" % output_file)

    ################################################
    # Add stand attributes to polygon shapefile
    @staticmethod
    def add_stand_attributes(vector_file_path, stand_list, remainder_stand_id):
        # open stand polygon file
        dataSource = gdal.OpenEx(vector_file_path, 1)
        layer = dataSource.GetLayer()

        # add stand attribute fields
        layer.CreateField(ogr.FieldDefn('OBJECTID', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('hmax', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('hdom', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('type', ogr.OFTString))
        layer.CreateField(ogr.FieldDefn('area_m2', ogr.OFTInteger64))

        # iterate over all features and add stand attribute values
        new_id_counter = 0
        objectid_counter = 0
        for feature in layer:
            # get current stand ID
            current_id = feature.GetField("ID")
            objectid_counter += 1

            # set stand attributes
            feature.SetField('OBJECTID', objectid_counter)
            feature.SetField('hmax', round(ClassificationHelper.getHmaxByStandId(stand_list, current_id)))
            feature.SetField('hdom', round(ClassificationHelper.getHdomByStandId(stand_list, current_id)))
            feature.SetField('type', ClassificationHelper.getStandType(current_id, remainder_stand_id))
            feature.SetField("area_m2", feature.GetGeometryRef().GetArea())

            # assign new, unique stand ID for remainders
            if ClassificationHelper.isRemainder(feature.GetField("type")):
                feature.SetField('ID', remainder_stand_id + new_id_counter)
                new_id_counter += 1

            # store information
            layer.SetFeature(feature)

        try:
            # this threw errors in specific QGIS versions (e.g. QGIS 3.28.4
            #TODO : check if gdal actually needs close and/or how this is properly handled
            dataSource.Close()
        except:
            print(f"Closing dataSource >> {dataSource} << failed with exception (origin: \n {vector_file_path}")

    ################################################
    # Add hmax effective and 80th percentile (zonal stats)
    @staticmethod
    def add_vhm_stats(vector_file_path, vhm):
        # get max VHM value and 80 percentile per polygon
        vectorfile_path_stat_path = vector_file_path.replace(".gpkg", "_stat.gpkg")
        param = {'map': vector_file_path, 'raster': vhm, 'column_prefix': 'rs', 'method': [2, 12], 'percentile': 80,
                 'output': vectorfile_path_stat_path, 'GRASS_REGION_PARAMETER': None,
                 'GRASS_REGION_CELLSIZE_PARAMETER': 0, 'GRASS_SNAP_TOLERANCE_PARAMETER': -1,
                 'GRASS_MIN_AREA_PARAMETER': 0.0001, 'GRASS_OUTPUT_TYPE_PARAMETER': 0, 'GRASS_VECTOR_DSCO': '',
                 'GRASS_VECTOR_LCO': '', 'GRASS_VECTOR_EXPORT_NOCAT': False}
        algoOutput = processing.run("grass7:v.rast.stats", param)

        statLayer = QgsVectorLayer(vectorfile_path_stat_path, 'stats', 'ogr')
        stats = {}
        counter = 0
        for feature in statLayer.getFeatures():
            stats[feature["OBJECTID"]] = {"max": feature["rs_maximum"], "percentile_80": feature["rs_percentile_80"]}
            counter += 1

        # print(stats)

        # open stand polygon file
        dataSource = gdal.OpenEx(vector_file_path, 1)
        layer = dataSource.GetLayer()

        # add stand attribute fields
        layer.CreateField(ogr.FieldDefn('hmax_eff', ogr.OFTInteger))
        layer.CreateField(ogr.FieldDefn('hp80', ogr.OFTInteger))

        # iterate over all features and add stand attribute values
        counter = 0
        for feature in layer:
            fid = feature.GetField("OBJECTID")
            hmax_eff = 0
            if stats[fid].get('max') is not None and stats[fid].get('max') != NULL:
                hmax_eff = stats[fid].get('max')

            hp80 = 0
            if stats[fid].get('percentile_80') is not None and stats[fid].get('percentile_80') != NULL:
                hp80 = stats[fid].get('percentile_80')

            # set and store hmax_eff
            feature.SetField('hmax_eff', hmax_eff)
            feature.SetField('hp80', hp80)
            layer.SetFeature(feature)
            counter += 1

        try:
            # this threw errors in specific QGIS versions (e.g. QGIS 3.28.4
            #TODO : check if gdal actually needs close and/or how this is properly handled
            dataSource.Close()
        except:
            print(f"Closing dataSource >> {dataSource} << failed with exception (origin: \n {vector_file_path}")
        # delete_geopackage(vectorfile_path_stat_path)

    ################################################
    # get hmax by stand ID
    @staticmethod
    def getHmaxByStandId(stand_list, current_id):
        for s in stand_list:
            if s[0] == current_id:
                return s[1]
        return 0

    ################################################
    # get hdom by stand ID
    @staticmethod
    def getHdomByStandId(stand_list, current_id):
        for s in stand_list:
            if s[0] == current_id:
                return s[2]
        return 0

    ################################################
    # get stand type
    @staticmethod
    def getStandType(current_id, remainder_stand_id):
        if current_id == remainder_stand_id:
            return 'remainder'
        else:
            return 'classified'

    ################################################
    # Returns true if stand type is 'remainder'
    @staticmethod
    def isRemainder(stand_type):
        return stand_type == 'remainder'

    ################################################
    # sieveFilter -> see online description gdal_sieve.bat
    @staticmethod
    def sieveFilter(raster_file, output_file):
        print("starting with sieve filter")
        # Opening the raster file
        src_ds = gdal.Open(raster_file, GA_ReadOnly)
        # Getting Band 1
        srcband = src_ds.GetRasterBand(1)

        # Getting driver
        drv = gdal.GetDriverByName("GTiff")

        # Create file
        dst_ds = drv.Create(output_file, src_ds.RasterXSize, src_ds.RasterYSize, 1,
                            srcband.DataType)
        wkt = src_ds.GetProjection()
        if wkt != '':
            dst_ds.SetProjection(wkt)
        dst_ds.SetGeoTransform(src_ds.GetGeoTransform())

        dstband = dst_ds.GetRasterBand(1)

        maskband = None
        prog_func = None
        result = gdal.SieveFilter(srcband, maskband, dstband, 10, 4,
                                  callback=prog_func)  # min. 10 cells for a valid polygon

        print("File %s saved" % output_file)

        # Clean up
        srcband = None
        src_ds = None
        dst_ds = None
        dstband = None

    @staticmethod
    def focal_majority(data, block_size, criteria, remove):
        """ Reclassifies pixels based on the focal majority
        :param data: Raster data
        :param block_size: Block size (i.e. 3 -> 3 x 3 window)
        :param criteria: To reclassify on pixels with a certain value. Use None to run for all pixels.
        :param remove: Value to ignore. For example "0", to ignore NoData areas.
        :return: Smoothed raster
        """

        data_copy = numpy.copy(data)

        # get subset pixels
        if criteria != None:
            rows, cols = numpy.where(data == criteria)
        else:
            rows, cols = numpy.where(data != 0)

        # loop over all cells (rows and cols)
        for i in range(len(rows)):
            r, c = rows[i], cols[i]
            value_check = data[r, c]

            # get pixel values within the search window (block)
            block = ClassificationHelper.get_matrix_subset2(data, r, c, block_size)
            block = block.flatten()

            # get counts, and remove for examples zeros
            b = Counter(block)
            if remove != None:
                del b[remove]

            # reclassify to the most common value
            most_common = b.most_common(1)[0][0]
            data_copy[r, c] = most_common

            # check if the origin value should be kept (minimum of 3 neighbours needed) regardless
            if criteria == None:
                for i in b.most_common():
                    if (i[0] == value_check) and (i[1] > 3):
                        # keep the current value
                        data_copy[r, c] = value_check
        return data_copy

    ################################################
    # get_block
    #
    # Returns a subset of the data array based on the position (r, c)
    # and block_size
    @staticmethod
    def get_block(data, r, c, block_size):
        block = []
        relativeStartPos = int(block_size / 2) * -1
        for rp in range(block_size):
            for cp in range(block_size):
                rTmp = r + rp + relativeStartPos
                cTmp = c + cp + relativeStartPos
                # add to block if valid cell (not outside matrix extent)
                if (rTmp >= 0) and (rTmp < data.shape[0]) and (cTmp >= 0) and (cTmp < data.shape[1]):
                    block.append(data[rTmp][cTmp])
        return block

    ################################################
    # get_matrix_subset
    #
    # Returns a subset of the data array based on the position (r, c)
    # and block size. Squared matrix with r/c being the center.
    @staticmethod
    def get_matrix_subset(matrix, r, c, s):
        return matrix[r - s // 2:r + s // 2 + 1, c - s // 2:c + s // 2 + 1]

    ################################################
    # get_matrix_subset2
    #
    # Returns a subset of the data array based on the position (r, c)
    # and block size. Squared matrix with r/c being the center.
    @staticmethod
    def get_matrix_subset2(matrix, r, c, s):
        r_start = r - s // 2
        r_end = r + s // 2 + 1
        c_start = c - s // 2
        c_end = c + s // 2 + 1
        if r_start < 0:
            r_start = 0
        if r_end > matrix.shape[0]:
            r_end = matrix.shape[0]
        if c_start < 0:
            c_start = 0
        if c_end > matrix.shape[1]:
            c_end = matrix.shape[1]

        return matrix[r_start:r_end, c_start:c_end]

    ################################################
    # replaceMatrixSubset
    #
    # Returns a matrix which was replaced by a subset based on the position (r, c)
    # and block size. Squared matrix with r/c being the center.
    @staticmethod
    def replace_matrix_subset(matrix, r, c, subset):
        s = subset.shape[0]
        matrix[r - s // 2:r + s // 2 + 1, c - s // 2:c + s // 2 + 1] = subset
        return matrix

    ################################################
    # get_similar_neighbours
    #
    # Returns a true/false matrix for a block of a certain
    # size indicating pixels within a certain tolerance.
    @staticmethod
    def get_similar_neighbours(data, value, min_tol, max_tol, min_corr, max_corr):
        m_min = data >= (value - value * min_tol) - min_corr
        m_max = data <= (value + value * max_tol) + max_corr
        return m_min & m_max

    ################################################
    # get_similar_neighbours_coniferous
    #
    # Returns a true/false matrix for a block of a certain
    # size indicating pixels within the same coniferous class
    @staticmethod
    def get_similar_neighbours_coniferous(data, value):
        if (value >= 0.0) & (value <= 20.0):
            return (data >= 0.0) & (data <= 50.0)
        elif (value >= 80.0) & (value <= 100.0):
            return (data >= 50.0) & (data <= 100.0)
        else:
            return numpy.zeros(data.shape, dtype=bool)

    ################################################
    # store_raster
    #
    # Stores the raster file
    @staticmethod
    def store_raster(data, path, projectionfrom, geotransform, datatype):
        rows, cols = data.shape
        driver = gdal.GetDriverByName('GTiff')
        ds_out = driver.Create(path, cols, rows, 1, datatype, )
        ds_out.SetProjection(projectionfrom)
        ds_out.SetGeoTransform(geotransform)
        ds_out.GetRasterBand(1).WriteArray(data)
        del ds_out

    def store_raster(data, path, projectionfrom, geotransform, datatype):
        """
        Save raster data to a compressed GeoTIFF file.

        Parameters:
        - data: 2D numpy array containing the raster data.
        - path: Output file path for the GeoTIFF.
        - projectionfrom: Projection string (e.g., WKT or EPSG) for the raster.
        - geotransform: GeoTransform tuple for the raster.
        - datatype: GDAL data type (e.g., gdal.GDT_Float32).
        """
        from osgeo import gdal

        # Define compression options
        compress_options = [
            "COMPRESS=DEFLATE",
            "PREDICTOR=2",  # Best for floating-point data
            "ZLEVEL=9"  # Maximum compression level
        ]

        # Get rows and columns from the data array
        rows, cols = data.shape

        # Get the GeoTIFF driver
        driver = gdal.GetDriverByName('GTiff')
        # Create the raster dataset with compression options
        ds_out = driver.Create(
            path, cols, rows, 1, datatype, options=compress_options
        )

        # Set projection and geotransform
        ds_out.SetProjection(projectionfrom)
        ds_out.SetGeoTransform(geotransform)
        # Write data to the raster band
        ds_out.GetRasterBand(1).WriteArray(data)
        # Flush and clean up
        del ds_out



    ################################################
    # Compare raster projection and extent
    @staticmethod
    def compare_raster(raster_file_1, raster_file_2):
        ds1 = gdal.Open(raster_file_1, GA_ReadOnly)
        ds2 = gdal.Open(raster_file_2, GA_ReadOnly)

        return (ds1.GetProjection() == ds2.GetProjection()) and \
            (ds1.GetGeoTransform() == ds2.GetGeoTransform()) and \
            (ds1.RasterXSize == ds2.RasterXSize) and (ds1.RasterYSize == ds2.RasterYSize)
