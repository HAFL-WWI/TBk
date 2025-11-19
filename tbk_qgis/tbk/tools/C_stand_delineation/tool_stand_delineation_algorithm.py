# -*- coding: utf-8 -*-

""" TBk stand delineation algorithm.
This QGIS plugin allows to generate "raw" forest stand maps.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__authors__ = 'Dominique Weber, Christoph Schaller'
__copyright__ = '(C) 2024 by Berner Fachhochschule HAFL'
__date__ = '2020-08-03'
__email__ = "christian.rosset@bfh.ch"
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'
__version__ = '0.9'

import logging
import os
import time
import numpy as np
from osgeo import gdal, osr
from osgeo.gdalconst import GA_ReadOnly
from qgis.core import (QgsProcessingOutputFile,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterString,
                       QgsProcessingUtils,
                       QgsProcessingParameterNumber)
from tbk_qgis.tbk.general.persistence_utility import write_dict_to_toml_file
from tbk_qgis.tbk.general.tbk_utilities import ensure_dir
from tbk_qgis.tbk.tools.C_stand_delineation.bk_hafl_ClassificationHelper import ClassificationHelper as helper
from tbk_qgis.tbk.tools.C_stand_delineation.tbk_qgis_processing_algorithm_toolsC import TBkProcessingAlgorithmToolC


class TBkStandDelineationAlgorithm(TBkProcessingAlgorithmToolC):
    """
    todo
    """
    # ------- Define Constants -------#
    # Constants used to refer to parameters and outputs.

    # These constants will be used when calling the algorithm from another algorithm,
    # or when calling from the QGIS console.

    # Directory containing the output files
    OUTPUT_ROOT = "output_root"
    # File storing configuration parameters
    CONFIG_FILE = "config_file"
    # Default log file name
    LOGFILE_NAME = "logfile_name"

    # VHM 10m as main TBk input
    VHM_10M = "vhm_10m"
    # Coniferous raster to be used during stand delineation
    CONIFEROUS_RASTER_FOR_CLASSIFICATION = "coniferous_raster_for_classification"

    # Result directory output (folder with timestamp)
    OUTPUT_RESULT_DIR = "result_dir"
    # Main output layer
    OUTPUT_STAND_BOUNDARIES = "output_stand_boundaries"
    # Other outputs
    OUTPUT_H_MAX = "output_h_max"
    OUTPUT_CLASSIFIED_RAW = "classified_raw"
    OUTPUT_CLASSIFIED_SMOOTH_1 = "classified_smooth_1"
    OUTPUT_CLASSIFIED_SMOOTH_2 = "classified_smooth_2"


    # Short description
    DESCRIPTION = "description"
    # Relative min tolerance
    MIN_TOL = "min_tol"
    # Relative max tolerance
    MAX_TOL = "max_tol"
    # Extension of the range down [m]
    MIN_CORR = "min_corr"
    # Extension of the range up [m]
    MAX_CORR = "max_corr"
    # Minimum relative amount of valid cells
    MIN_VALID_CELLS = "min_valid_cells"
    # Minimum cells per stand
    MIN_CELLS_PER_STAND = "min_cells_per_stand"
    # Minimum cells for pure mixture stands
    MIN_CELLS_PER_PURE_STAND = "min_cells_per_pure_stand"
    # VHM minimum height
    VHM_MIN_HEIGHT = "vhm_min_height"
    # VHM maximum height
    VHM_MAX_HEIGHT = "vhm_max_height"
    # Delete temporary files and fields
    DEL_TMP = "del_tmp"

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and outputs of the algorithm.
        """
        # --- Handle config argument
        # Indicates whether the tool is running in standalone or modularized mode, and adjusts the GUI/behavior if needed.
        is_standalone_context = config.get('is_standalone_context') if config else True

        # --- Parameters

        # Config file containing all parameter key-value pairs
        self.addParameter(QgsProcessingParameterFile(self.CONFIG_FILE,
                                                     'Configuration file to set the algorithm parameters. The bellow '
                                                     'non-optional parameters must still be set but will not be used.',
                                                     optional=True))

        # VHM 10m as main TBk input
        self.addParameter(QgsProcessingParameterRasterLayer(self.VHM_10M,
                                                            "VHM 10m as main TBk input  (.tif)"))

        # Coniferous raster
        self.addParameter(QgsProcessingParameterRasterLayer(self.CONIFEROUS_RASTER_FOR_CLASSIFICATION,
                                                            "Coniferous raster to be used during stand "
                                                            "delineation (.tif)\nA simplified binarized "
                                                            "raster may achieve better results",
                                                            optional=True))

        # Folder for algorithm output
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_ROOT,
                                                                  "Output folder (a subfolder with timestamp will be "
                                                                  "created within)"))

        # Not needed in a modular context; can use the previous algorithm's output directly
        if is_standalone_context:
            # Main output (stand boundaries) for algorithm output
            self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_STAND_BOUNDARIES,
                                                                    "Stand Boundaries Output (GeoPackage)",
                                                                    "GPKG files (*.gpkg)",
                                                                    optional=True))

            # --- Add output definition, so that they can be used in model designer
            self.addOutput(QgsProcessingOutputFile(self.OUTPUT_RESULT_DIR,
                                                   "Result output folder (folder with timestamp)"))

            # Stand boundaries output
            self.addOutput(QgsProcessingOutputFile(self.OUTPUT_STAND_BOUNDARIES,
                                                   "Stand Boundaries Output file"))

            # H max output
            self.addOutput(QgsProcessingOutputFile(self.OUTPUT_H_MAX,
                                                   "H max Output file"))

        # --- Advanced Parameters

        # Main TBk Algorithm parameters

        parameter = QgsProcessingParameterString(self.LOGFILE_NAME, "Log File Name (.log)",
                                                 defaultValue="tbk_processing.log")
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterString(self.DESCRIPTION, "Short description",
                                                 defaultValue="TBk dataset")
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_TOL, "Relative min tolerance",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0.1)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MAX_TOL, "Relative max tolerance",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0.1)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_CORR, "Extension of the range down [m]",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=4)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MAX_CORR, "Extension of the range up [m]",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=4)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_VALID_CELLS,
                                                 "Minimum relative amount of valid cells",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0.5)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_CELLS_PER_STAND, "Minimum cells per stand",
                                                 type=QgsProcessingParameterNumber.Integer, defaultValue=10)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_CELLS_PER_PURE_STAND,
                                                 "Minimum cells for pure mixture stands",
                                                 type=QgsProcessingParameterNumber.Integer, defaultValue=30)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.VHM_MIN_HEIGHT, "VHM minimum height",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.VHM_MAX_HEIGHT, "VHM maximum height",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=60)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.DEL_TMP, "Delete temporary files and fields", defaultValue=True)
        self._add_advanced_parameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # prepare the algorithm
        self.prepare(parameters, context, feedback)

        # --- get and check input parameters

        params = self._extract_context_params(parameters, context)

        # Handle the outputs directories
        result_dir = self._get_result_dir(params.output_root)
        bk_dir = self._get_bk_output_dir(result_dir)
        ensure_dir(bk_dir)

        # set logger
        self._configure_logging(result_dir, params.logfile_name)
        log = logging.getLogger(self.name())

        # check tif files extension
        self._check_tif_extension(params.vhm_10m, self.VHM_10M)
        if params.coniferous_raster_for_classification:
            self._check_tif_extension(params.coniferous_raster_for_classification,
                                      self.CONIFEROUS_RASTER_FOR_CLASSIFICATION)

        # Write the used parameters in a toml file
        try:
            write_dict_to_toml_file(params.__dict__, bk_dir)
        except Exception:
            feedback.pushWarning('The TOML file was not writen in the output folder because an error occurred')

        # ------- TBk Processing --------#
        # --- Stand delineation (Main)
        log.info('Starting')

        # None correspond to the zone_raster_file that is not used yet
        params_args = {
            'del_tmp': params.del_tmp,
            'out_path': bk_dir,
            'input_vhm_raster': params.vhm_10m,
            'coniferous_raster_file': params.coniferous_raster_for_classification,
            'zone_raster': None,
            'min_tol': params.min_tol,
            'max_tol': params.max_tol,
            'min_corr': params.min_corr,
            'max_corr': params.max_corr,
            'min_valid_cells': params.min_valid_cells,
            'min_cells_per_stand': params.min_cells_per_stand,
            'min_cells_per_pure_stand': params.min_cells_per_pure_stand,
            'vhm_min_height': params.vhm_min_height,
            'vhm_max_height': params.vhm_max_height,
            'output_stand_boundaries': params.output_stand_boundaries,
        }

        log.debug(f"used parameters: {params_args}")

        results = self.run_stand_delineation(**params_args)

        log.debug(f"Results: {results}")
        log.info("Finished")

        results = {
            self.OUTPUT_CLASSIFIED_RAW: results["raw_classified"],
            self.OUTPUT_CLASSIFIED_SMOOTH_1: results["smooth_1"],
            self.OUTPUT_CLASSIFIED_SMOOTH_2: results["smooth_2"],
            self.OUTPUT_H_MAX: results["hmax"],
            self.OUTPUT_RESULT_DIR: result_dir,
            self.OUTPUT_STAND_BOUNDARIES: results["stand_boundaries"],
        }

        return results

    def createInstance(self):
        """
        Returns a new algorithm instance
        """
        return TBkStandDelineationAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '1 Delineate Stand'

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('Stand classification based on a vegetation height raster. The vegetation height raster (VHM) is '
                'usually a 10x10m max height raster from LiDAR or stereo image matching data.')

    def run_stand_delineation(self,
                              del_tmp,
                              out_path,
                              output_stand_boundaries,
                              input_vhm_raster,
                              coniferous_raster_file,
                              zone_raster,
                              min_tol,
                              max_tol,
                              min_corr,
                              max_corr,
                              min_valid_cells,
                              min_cells_per_stand,
                              min_cells_per_pure_stand,
                              vhm_min_height,
                              vhm_max_height):
        """
        Run stand classification based on vegetation height model input raster.

        :param out_path: Folder path in which to save the outputs
        :param input_vhm_raster: Input file, single band tif
        :param coniferous_raster_file: Coniferous proportion (0-100), single band tif
        :param zone_raster: single band tif
        :param min_tol: Min tolerance (example 0.25 = 25% less than the reference value)
        :param max_tol: Max tolerance (example 0.20 = 20% more than the reference value)
        :param min_corr: Additional correction of the min value. This is important to improve classification of smaller trees.
        :param max_corr: additional correction of the max value. This is important to improve classification of smaller trees.
        :param min_valid_cells: This is the factor of how many cells inside the search window must be found within the range to be assign to the stand.
        :param min_cells_per_stand: Min amount of cells assigned to the same stand to be kept as a separate stand at the end.
        :param min_cells_per_pure_stand: Min amount of cells to be classified as pure mixture stand if option is chosen.
        :param vhm_min_height: Min VHM height in meters for cells to be processed -> set to zero
        :param vhm_max_height: Max VHM height in meters for cells to be processed -> set to zero
        """

        # -------- INIT --------#

        log = logging.getLogger(self.name())
        gdal.UseExceptions()
        start_time = time.time()
        ensure_dir(out_path)

        # Define output file paths
        output_files = {
            "raw_classified": os.path.join(out_path, "classified_raw.tif"),
            "smooth_1": os.path.join(out_path, "classified_smooth_1.tif"),
            "smooth_2": os.path.join(out_path, "classified_smooth_2.tif"),
            "hmax": os.path.join(out_path, "hmax.tif"),
            "stand_boundaries": output_stand_boundaries
        }

        # Define temporary output file paths
        temp_file_folder = QgsProcessingUtils.tempFolder() if del_tmp else out_path
        if del_tmp:
            tmp_stat = os.path.join(temp_file_folder, "stand_boundaries_stat.gpkg")
        else:
            tmp_stat = output_stand_boundaries.rsplit(".gpkg", 1)[0] + "_stat.gpkg"

        temp_output_files = {
            "hdom": os.path.join(temp_file_folder, "hdom.tif"),
            'stand_boundaries_stat': tmp_stat,
        }

        # Log configurations
        log.info(f"TBk version: {__version__}")
        log.info(f"Output path: {out_path}")
        log.info(f"VHM input path: {input_vhm_raster}")
        log.info(f"Coniferous input path: {coniferous_raster_file}")

        # Load VHM data
        vhm_dataset = gdal.Open(input_vhm_raster, GA_ReadOnly)
        vhm_band = vhm_dataset.GetRasterBand(1)
        vhm_data = vhm_band.ReadAsArray().astype(float)  # format: data[row, col] -> data[y, x]
        geotransform = vhm_dataset.GetGeoTransform()
        vhm_projection = vhm_dataset.GetProjection()

        log.info(f"VHM raster info: "
                 f"{vhm_dataset.RasterCount} bands, "
                 f"{vhm_data.shape[0]} rows x {vhm_data.shape[1]} cols, "
                 f"{geotransform[1]} resolution, "
                 f"X: {round(geotransform[0], 2)}, "
                 f"Y: {round(geotransform[3], 2)}, "
                 f"CRS: {osr.SpatialReference(wkt=vhm_projection).GetAttrValue('projcs')}")

        # handle unrealistic values and NoData values
        nodata_value = vhm_band.GetNoDataValue()
        vhm_data[vhm_data == nodata_value] = np.nan
        tmp_zero_mask = (vhm_data < vhm_min_height) | (vhm_data > vhm_max_height)
        vhm_data[tmp_zero_mask] = 0

        # Sort VHM data (biggest tree on top)
        sorted_vhm_data = helper.getSortedList(vhm_data, vhm_data.size)

        # Init stand, hmax, hdom arrays
        stand = np.zeros(vhm_data.shape, dtype=int)
        hmax = np.zeros(vhm_data.shape, dtype=float)
        hdom = np.zeros(vhm_data.shape, dtype=float)

        # Init list to store stand information [ID, hmax, hdom]
        stands = []

        # if provided, load zone raster
        zone = np.ones(vhm_data.shape, dtype=int)
        if zone_raster:
            zone = self._load_raster(zone_raster, int)
            if not helper.compare_raster(input_vhm_raster, zone_raster):
                log.warning("VHM and ZONE raster have different extents and/or projections!")

        # if provided, load coniferous raster
        coniferous_data = None
        if coniferous_raster_file:
            coniferous_data = self._load_raster(coniferous_raster_file, int)

            if not helper.compare_raster(input_vhm_raster, coniferous_raster_file):
                log.warning("VHM and MG raster have different extents and/or projections!")

        log.info(f"--- {self._get_elapsed_time(start_time)} minutes, input data loaded---")

        # ------- STAND CLASSIFICATION -------#

        # Init stand number with one
        stand_nbr = 1

        if coniferous_data is not None:
            log.info("pre-classification with mixture information...")
            stand, stand_nbr, stands, hdom, hmax = self.classify_pixels(vhm_data, sorted_vhm_data, stand_nbr,
                                                                        min_tol, max_tol, min_corr, max_corr,
                                                                        min_valid_cells, min_cells_per_pure_stand,
                                                                        zone, coniferous_data,
                                                                        stand, stands, hdom, hmax)

        log.info("classification without mixture information...")
        stand, stand_nbr, stands, hdom, hmax = self.classify_pixels(vhm_data, sorted_vhm_data, stand_nbr,
                                                                    min_tol, max_tol, min_corr, max_corr,
                                                                    min_valid_cells, min_cells_per_stand,
                                                                    zone, None,
                                                                    stand, stands, hdom, hmax)

        log.info(f"--- {self._get_elapsed_time(start_time)} minutes, classification finished ---")

        # Assign remaining pixels to last stand number
        m_tmp = (vhm_data >= 0) & (stand == 0)
        stand[m_tmp] = stand_nbr

        # Save results
        helper.store_raster(stand, output_files["raw_classified"], vhm_projection, geotransform, gdal.GDT_UInt32)
        helper.store_raster(hmax, output_files["hmax"], vhm_projection, geotransform, gdal.GDT_Byte)
        helper.store_raster(hdom, temp_output_files["hdom"], vhm_projection, geotransform, gdal.GDT_Byte)
        log.info(f"--- {self._get_elapsed_time(start_time)} minutes, raw_classified, hmax and hdom saved  ---")

        # ------- SMOOTHING -------#

        # focal majority for all pixels where no stand was found (last stand number)
        stand = helper.focal_majority(stand, 3, stand_nbr, 0)
        helper.store_raster(stand, output_files["smooth_1"], vhm_projection, geotransform, gdal.GDT_UInt32)

        # focal majority for all pixels
        stand = helper.focal_majority(stand, 3, None, 0)
        helper.store_raster(stand, output_files["smooth_2"], vhm_projection, geotransform, gdal.GDT_UInt32)

        log.info(f"--- {self._get_elapsed_time(start_time)} minutes, raster smoothed and saved  ---")

        # ------- POLYGONIZE, ADD ATTRIBUTES -------#

        # polygonize the raster -> to vector file
        helper.polygonize(output_files["smooth_2"], output_files["stand_boundaries"])
        log.info(f"--- {self._get_elapsed_time(start_time)} minutes, stand boundaries vector file saved ---")

        # add stand information to polygon vector file
        helper.add_stand_attributes(output_files["stand_boundaries"], stands, stand_nbr)
        log.info(f"--- {self._get_elapsed_time(start_time)} minutes, stand attributes added ---")

        # zonal statistics for vhm per polygon, which is later used to calculate remainder hmax & hdom
        helper.add_vhm_stats(output_files["stand_boundaries"],
                             temp_output_files['stand_boundaries_stat'],
                             input_vhm_raster)
        log.info(f"--- {self._get_elapsed_time(start_time)} minutes, vhm stats calculated ---")

        return output_files

    def classify_pixels(self,
                        vhm_data,
                        sorted_vhm_data,
                        stand_nbr,
                        min_tol,
                        max_tol,
                        min_corr,
                        max_corr,
                        min_valid_cells,
                        min_cells_per_stand,
                        zone,
                        coniferous_data,
                        stand,
                        stands,
                        hdom,
                        hmax):

        log = logging.getLogger(self.name())
        progress_print_step = len(sorted_vhm_data) / 10
        next_print_threshold = progress_print_step

        def log_progress(i, value):
            log.info(f"{round(i / progress_print_step) * 10}% pixels classified --> "
                     f"({i} from {len(sorted_vhm_data)}), value {round(value, 1)}, standNbr {stand_nbr}")

        # loop over all pixels, starting with the biggest value
        for i, (value, row, col) in enumerate(sorted_vhm_data):

            # log every 10 % of pixel processed
            if i >= next_print_threshold:
                log_progress(i, value)
                next_print_threshold += progress_print_step

            # proceed if not already classified
            if stand[row, col] == 0 and value > 0:
                # store starting pixel value since it is later updated if the counter == 1
                start_value = value

                # lists to process
                rows_todo = [row]
                cols_todo = [col]

                # lists processed
                rows_classified = []
                cols_classified = []

                counter = 0
                while rows_todo:
                    row, col = rows_todo[0], cols_todo[0]

                    # calculate window size
                    if counter < 2:
                        s = helper.getWindowSize(value)

                    # get matrix subsets
                    vhm_data_sub = helper.get_matrix_subset(vhm_data, row, col, s)
                    stand_sub = helper.get_matrix_subset(stand, row, col, s)
                    zone_sub = helper.get_matrix_subset(zone, row, col, s)

                    # create True / False matrices
                    m_tol = helper.get_similar_neighbours(vhm_data_sub, value, min_tol, max_tol, min_corr, max_corr)
                    m_stand = np.logical_or(stand_sub == 0, stand_sub == stand_nbr)
                    m_zone = zone_sub == zone[row, col]

                    # get coniferous matrix if raster is provided
                    m_coniferous = np.ones(m_tol.shape, dtype=bool)
                    if coniferous_data is not None:
                        coniferous_sub = helper.get_matrix_subset(coniferous_data, row, col, s)
                        # initialize coniferous mean on first iteration
                        if counter == 0:
                            # only consider pixels that are within similar height threshold
                            if coniferous_sub[m_tol].size:
                                coniferous_mean = np.mean(coniferous_sub[m_tol])
                            else:
                                # ensure coniferous_mean is initialized. With 50 it won't trigger seperate delineation
                                coniferous_mean = 50
                        m_coniferous = helper.get_similar_neighbours_coniferous(coniferous_sub, coniferous_mean)

                    # combine matrices to get final filters
                    m_comb = m_tol & m_stand & m_zone & m_coniferous
                    m_expand = m_tol & (stand_sub == 0) & m_zone & m_coniferous

                    # check if enough similar cells found -> start searching for more, otherwise skip entry pixel
                    if np.sum(m_comb) > int(round(s * s * min_valid_cells)):
                        counter += 1
                        # classify already found pixels -> reference to stand matrix
                        stand_sub[m_comb] = stand_nbr

                        # calculate new check value
                        if counter == 1:
                            value = np.mean(vhm_data_sub[m_comb])

                        # add cell coordinates to processing lists
                        r_sub, c_sub = np.ogrid[row - s // 2: row + s // 2 + 1, col - s // 2: col + s // 2 + 1]

                        m_r_sub = np.repeat(r_sub, s).reshape(s, s)
                        m_c_sub = np.repeat(c_sub, s).reshape(s, s).T

                        # To make sure that no cells outside the raster will be added to the todo_lists
                        if m_r_sub.size != m_expand.shape[0] or m_c_sub.size != m_expand.shape[1]:
                            m_r_sub = m_r_sub[0:m_expand.shape[0], 0:m_expand.shape[1]]
                            m_c_sub = m_c_sub[0:m_expand.shape[0], 0:m_expand.shape[1]]

                        rows_todo.extend(m_r_sub[m_expand])
                        cols_todo.extend(m_c_sub[m_expand])

                    # add to finished list
                    rows_classified.append(rows_todo[0])
                    cols_classified.append(cols_todo[0])

                    #  remove processed entries
                    rows_todo.pop(0)
                    cols_todo.pop(0)

                # because of last iteration which was not successful but still added to the list
                classified_pixels = len(rows_classified) - 1

                # a minimum amount of pixels is needed, otherwise reset classification
                #       stand numbers are already stored in stand, as the subset is a reference to the main matrix
                if classified_pixels >= min_cells_per_stand:
                    # get hmax, which is the initial value for this stand (crystallisation point)
                    hmax_stand = start_value
                    # get hdom, which is the mean height of all classified cells within the stand
                    hdom_stand = np.mean(vhm_data[rows_classified, cols_classified])

                    # add stand information to the list
                    stands.append([stand_nbr, hmax_stand, hdom_stand])

                    # store information as arrays
                    hmax[row, col] = hmax_stand
                    hdom[rows_classified, cols_classified] = hdom_stand

                    stand_nbr += 1
                else:
                    # reset classification
                    stand[rows_classified, cols_classified] = 0
        return stand, stand_nbr, stands, hdom, hmax

    @staticmethod
    def _get_elapsed_time(start_time):
        """
        return the elapsed minutes between the start time and now
        """
        return round((time.time() - start_time) / 60, 2)

    @staticmethod
    def _load_raster(raster_path, dtype):
        """
        Load a raster file and read the data from its first band
        """
        dataset = gdal.Open(raster_path, gdal.GA_ReadOnly)
        band = dataset.GetRasterBand(1)
        return band.ReadAsArray().astype(dtype)
