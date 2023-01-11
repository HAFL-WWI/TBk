#######################################################################
# Description: Main script, stand classification based on a vegetation height raster.
# The vegetation height raster (VHM) is usually a 10x10m max height raster from
# LiDAR or stereo image matching data.
#
# (C) Dominique Weber, Christoph Schaller, HAFL, BFH.
#######################################################################

from osgeo import gdal, osr
from osgeo.gdalconst import *
import numpy as np
from tbk.bk_core.Classification import ClassificationHelper as CH
import time
import logging
from datetime import datetime
import os
import sys

# TBk version, update this string manually
version = "0.9"

def run_stand_classification(workingRoot,
                             inputRasterFile,
                             coniferousRasterFile = 'null',
                             zoneRasterFile = 'null',
                             shortDescription = "No description",
                             min_tol= 0.1,
                             max_tol = 0.1,
                             min_corr = 4,
                             max_corr = 4,
                             min_valid_cells = 0.5,
                             min_cells_per_stand = 10,
                             min_cells_per_pure_stand = 30,
                             vhm_min_height = 0,
                             vhm_max_height = 60):
    '''
    Run stand classification based on VHM input raster.

    :param workingRoot: Working folder (ex. 'C:\\Temp\\Bestandeskarte\\'), use double backslash
    :param inputRasterFile: Input file, single band tif, 10x10m. In the working root folder!
    :param coniferousRasterFile: Coniferous proportion (0-100). Same format as inputRasterFile. If not used, use 'null'.
    :param zoneRasterFile: Same format as inputRasterFile. If no zone mask, use 'null'.
    :param shortDescription: Description used in log file.
    :param min_tol: Min tolerance (example 0.25 = 25% less than the reference value)
    :param max_tol: Max tolerance (example 0.20 = 20% more than the reference value)
    :param min_corr: Additional correction of the min value. This is important to improve classification of smaller trees.
    :param max_corr: additional correction of the max value. This is important to improve classification of smaller trees.
    :param min_valid_cells: This is the factor of how many cells inside the search window must be found within the range to be assign to the stand.
    :param min_cells_per_stand: Min amount of cells assigned to the same stand to be kept as a separate stand at the end.
    :param min_cells_per_pure_stand: Min amount of cells to be classified as pure mixture stand if option is chosen.
    :param vhm_min_height: Min VHM height in meters for cells to be processed -> set to zero
    :param vhm_max_height: Max VHM height in meters for cells to be processed -> set to zero
    '''

    print("--------------------------------------------")
    print("START stand delineation...")

    # Get time for testing performance
    start_time = time.time()

    # Standard file names
    outputRasterFileRaw = 'classified_raw.tif' # output filename, raw classification raster
    outputRasterFileSmooth1 = 'classified_smooth_1.tif' # output filename, smoothing for not-assigned pixels
    outputRasterFileSmooth2 = 'classified_smooth_2.tif' # output filename, smoothing for all pixels
    outputRasterFileHmax = 'hmax.tif'  # output filename for Hmax (initial tree of each stand)
    outputRasterFileHdom = 'hdom.tif'  # output filename for Hdom (mean height per stand -> before smoothing)
    outputShapefile = 'stand_boundaries.shp' # shapefile, generated from raster (after polygonize)
    logfile = 'tbk_log.log' # name of the logfile (config params)

    # Add the trailing slash if it's not already there.
    workingRoot = os.path.join(workingRoot, '')

    # Creating a new directory for the current classification
    currentDatetime = datetime.now().strftime("%Y%m%d-%H%M")
    outputDirectory = currentDatetime
    out_path = workingRoot + outputDirectory
    #out_path = workingRoot
    out_path = os.path.join(out_path, '')
    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    # Define input and output file paths
    inputFilePath = inputRasterFile
    coniferousFilePath =  coniferousRasterFile
    zoneFilePath = zoneRasterFile
    outputRawFilePath = os.path.join(out_path, outputRasterFileRaw)
    outputSmooth1FilePath = os.path.join(out_path, outputRasterFileSmooth1)
    outputSmooth2FilePath = os.path.join(out_path, outputRasterFileSmooth2)
    outputShapefilePath = os.path.join(out_path, outputShapefile)
    outputHmaxPath = os.path.join(out_path, outputRasterFileHmax)
    outputHdomPath = os.path.join(out_path, outputRasterFileHdom)

    # Logging the configurations
    logging.info('TBk version: %s' %version)
    logging.info('Output path: %s' %out_path)
    logging.info('VHM path: %s' % inputFilePath)

    # Opening the raster file and getting band 1 as numpy array
    if not os.path.exists(inputFilePath):
        sys.exit("Error: Raster input file (inputFilePath) not found!")
    ds = gdal.Open(inputFilePath, GA_ReadOnly)
    band = ds.GetRasterBand(1)
    data = band.ReadAsArray().astype(np.float)  # format: data[row, col] -> data[y, x]

    # Get and print main input raster information
    geotransform = ds.GetGeoTransform()
    projectionfrom = ds.GetProjection()
    print("VHM raster info: %s bands, %s rows x %s cols, %s resolution, X: %s, Y: %s, CRS: %s"
          %(ds.RasterCount, data.shape[0], data.shape[1], geotransform[1], round(geotransform[0], 2),
            round(geotransform[3], 2), osr.SpatialReference(wkt=projectionfrom).GetAttrValue('projcs')))

    # get NoData value
    nodata_value = band.GetNoDataValue()

    # set unrealistically low or height values to zero
    tmp_zero_mask = (data < vhm_min_height) | (data > vhm_max_height)
    data[tmp_zero_mask & (data != nodata_value)] = 0
    # set NoData value to -128, so it will not be processed
    data[data == nodata_value] = -128

    # Get sorted list of pixel values (biggest value=largest tree on top)
    dataList = CH.getSortedList(data, data.size)

    # Init stand, hmax, hdom arrays
    stand = np.zeros(data.shape, dtype=int)
    hmax = np.zeros(data.shape, dtype=float)
    hdom = np.zeros(data.shape, dtype=float)

    # Init list to store stand information [ID, hmax, hdom]
    standList = list()

    # if provided, load coniferous raster
    coniferous = None
    if coniferousRasterFile != 'null' and coniferousRasterFile != None:
        ds = gdal.Open(coniferousFilePath, GA_ReadOnly)
        band = ds.GetRasterBand(1)
        coniferous = band.ReadAsArray().astype(np.int) # format: data[row, col] -> data[y, x]
        if not CH.compare_raster(inputFilePath, coniferousFilePath):
            logging.warning("VHM and MG raster have different extents and/or projections!")

    # if provided, load zone raster
    zone = np.ones(data.shape, dtype=int)
    if zoneRasterFile != 'null' and zoneRasterFile != None:
        ds = gdal.Open(zoneFilePath, GA_ReadOnly)
        band = ds.GetRasterBand(1)
        zone = band.ReadAsArray().astype(np.int) # format: data[row, col] -> data[y, x]
        if not CH.compare_raster(inputFilePath, zoneFilePath):
            logging.warning("VHM and ZONE raster have different extents and/or projections!")

    print("--- %s minutes, input data loaded---" % round((time.time() - start_time)/60, 2))

    # Init stand number with one
    standNbr = 1

    if coniferous is not None:
        print("pre-classification with mixture information...")
        stand, standNbr, standList, hdom, hmax = classify_pixels(data, dataList, standNbr,
                                                                 min_tol, max_tol, min_corr, max_corr, min_valid_cells, min_cells_per_pure_stand,
                                                                 zone, coniferous,
                                                                 stand, standList, hdom, hmax)

    print("classification without mixture information...")
    stand, standNbr, standList, hdom, hmax = classify_pixels(data, dataList, standNbr,
                                                             min_tol, max_tol, min_corr, max_corr, min_valid_cells, min_cells_per_stand,
                                                             zone, None,
                                                             stand, standList, hdom, hmax)

    print("--- %s minutes, classification finished ---" % round((time.time() - start_time)/60, 2))

    # classify all value not classified till now
    m_tmp = (data >= 0) & (stand == 0)
    stand[m_tmp] = standNbr

    # Save raw classification file
    CH.store_raster(stand, outputRawFilePath, projectionfrom, geotransform, gdal.GDT_UInt32)
    print("File %s saved" %outputRawFilePath)

    # Save hmax raster
    CH.store_raster(hmax, outputHmaxPath, projectionfrom, geotransform, gdal.GDT_Byte)
    print("File %s saved" %outputHmaxPath)

    # Save hdom raster
    CH.store_raster(hdom, outputHdomPath, projectionfrom, geotransform, gdal.GDT_Byte)
    print("File %s saved" %outputHdomPath)

    # focal majority for all pixels where no stand was found (last stand number)
    stand = CH.focal_majority(stand, 3, standNbr, 0)
    # save file after reclassify
    CH.store_raster(stand, outputSmooth1FilePath, projectionfrom, geotransform, gdal.GDT_UInt32)
    print("File %s saved" %outputSmooth1FilePath)

    # focal majority for all pixels
    stand = CH.focal_majority(stand, 3, None, 0)
    # save file after reclassify
    CH.store_raster(stand, outputSmooth2FilePath, projectionfrom, geotransform, gdal.GDT_UInt32)
    print("File %s saved" %outputSmooth2FilePath)
    print("--- %s minutes, raster smoothed and saved  ---" % round((time.time() - start_time)/60, 2))

    # polygonize the raster -> to ESRI Shapefile
    CH.polygonize(outputSmooth2FilePath, outputShapefilePath)
    print("--- %s minutes, shapefile saved ---" % round((time.time() - start_time)/60, 2))

    # add stand information to polygon shapefile
    CH.add_stand_attributes(outputShapefilePath, standList, standNbr)
    print("--- %s minutes, stand attributes added ---" % round((time.time() - start_time)/60, 2))

    # zonal statistics for vhm per polygon, which is later used to calculate remainder hmax & hdom
    print("stats input file path", inputFilePath)
    CH.add_vhm_stats(outputShapefilePath, inputFilePath)
    print("--- %s minutes, vhm stats calculated ---" % round((time.time() - start_time)/60, 2))

    # DONE
    print('DONE ! ')

    # Return output directory
    return out_path


def classify_pixels(data,
                    dataList,
                    standNbr,
                    min_tol,
                    max_tol,
                    min_corr,
                    max_corr,
                    min_valid_cells,
                    min_cells_per_stand,
                    zone,
                    coniferous,
                    stand,
                    standList,
                    hdom,
                    hmax):
    prz10 = len(dataList) / 10
    przPrint = prz10
    # loop over all pixels, starting with the biggest value
    for i in range(len(dataList)):
        # get value, row and col of current pixel
        v, r, c = dataList[i]

        # print every 10 % of pixel processed
        if i > przPrint:
            print("%s%% pixels classified --> (%s from %s), value %s, standNbr %s" % (
            round(przPrint / prz10) * 10, i, len(dataList), round(v, 1), standNbr))
            przPrint += prz10

        # proceed if not already classified
        if stand[r, c] == 0 and v > 0:

            # store starting cell information
            v_start, r_start, c_start = v, r, c

            # lists to process
            rows_todo = [r]
            cols_todo = [c]

            # lists processed
            rows_classified = []
            cols_classified = []

            counter = 0
            while len(rows_todo) > 0:
                r = rows_todo[0]
                c = cols_todo[0]

                # calculate window size
                if counter == 0 or counter == 1:
                    s = CH.getWindowSize(v)

                # get matrix subsets
                data_sub = CH.get_matrix_subset(data, r, c, s)
                stand_sub = CH.get_matrix_subset(stand, r, c, s)
                zone_sub = CH.get_matrix_subset(zone, r, c, s)

                # create True / False matrices
                m_tol = CH.get_similar_neighbours(data_sub, v, min_tol, max_tol, min_corr, max_corr)
                m_stand = np.logical_or(stand_sub == 0, stand_sub == standNbr)
                m_zone = (zone_sub == zone[r, c])

                # get coniferous matrix if raster is provided
                m_coniferous = np.ones(m_tol.shape, dtype=bool)
                if coniferous is not None:
                    coniferous_sub = CH.get_matrix_subset(coniferous, r, c, s)
                    if counter == 0 and len(coniferous_sub[m_tol]) != 0:
                        coniferous_mean = np.mean(coniferous_sub[m_tol])
                    m_coniferous = CH.get_similar_neighbours_coniferous(coniferous_sub, coniferous_mean)

                # combine matrices to get final filters
                m_comb = m_tol & m_stand & m_zone & m_coniferous
                m_expand = m_tol & (stand_sub == 0) & m_zone & m_coniferous

                # check if enough similar cells found -> start searching for more, otherwise skip entry pixel
                if np.sum(m_comb) > int(round(s * s * min_valid_cells)):
                    counter += 1
                    # classify already found pixels -> reference to stand matrix
                    stand_sub[m_comb] = standNbr

                    # calculate new check value
                    if counter == 1:
                        v = np.mean(data_sub[m_comb])
                        if coniferous is not None:
                            coniferous_mean = np.mean(coniferous_sub[m_comb])

                    # add cell coordinates to processing lists
                    r_sub = range(r - s // 2, r + s // 2 + 1)
                    c_sub = range(c - s // 2, c + s // 2 + 1)
                    m_r_sub = np.repeat(r_sub, s).reshape(s, s)
                    m_c_sub = np.repeat(c_sub, s).reshape(s, s).T

                    # To make sure that no cells outside the raster will be added to the todo_lists
                    if (m_r_sub.size != m_expand.shape[0] or m_c_sub.size != m_expand.shape[1]):
                        m_r_sub = m_r_sub[0:m_expand.shape[0], 0:m_expand.shape[1]]
                        m_c_sub = m_c_sub[0:m_expand.shape[0], 0:m_expand.shape[1]]

                    rows_todo.extend(m_r_sub[m_expand])
                    cols_todo.extend(m_c_sub[m_expand])

                # add to finished list
                rows_classified.append(rows_todo[0])
                cols_classified.append(cols_todo[0])

                #  remove processed entries
                del rows_todo[-0]
                del cols_todo[-0]

            # because of last iteration which was not successful but still added to the list
            classified_pixels = len(rows_classified) - 1

            # a minimum amount of pixels is needed, otherwise remove classification
            #       stand numbers are already stored in stand, as the subset is a reference to the main matrix
            if classified_pixels >= min_cells_per_stand:
                # get hmax, which is the initial value for this stand (crystallisation point)
                hmax_stand = v_start
                # get hdom, which is the mean height of all classified cells within the stand
                hdom_stand = np.mean(data[rows_classified, cols_classified])

                # add stand information to the list
                standList.append([standNbr, hmax_stand, hdom_stand])

                # store information as arrays
                hmax[r_start, c_start] = hmax_stand
                hdom[rows_classified, cols_classified] = hdom_stand

                # increment stand number
                standNbr += 1
            else:
                # reset classification
                stand[rows_classified, cols_classified] = 0
    return stand, standNbr, standList, hdom, hmax


