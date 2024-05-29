# -*- coding: utf-8 -*-

""" TBk stand delineation algorithm.
This QGIS plugin allows to generate "raw" forest stand maps.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Todo:
    * merge main branch when config pull request is integrated
    * Enhance the helpstring
"""

__authors__ = 'Dominique Weber, Christoph Schaller'
__copyright__ = '(C) 2024 by Berner Fachhochschule HAFL'
__date__ = '2020-08-03'
__email__ = "christian.rosset@bfh.ch"
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import logging
from qgis.core import (QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber)
from tbk_qgis.tbk.bk_core.tbk_create_stands import run_stand_classification
from tbk_qgis.tbk.bk_core.tbk_qgis_processing_algorithm import TBkProcessingAlgorithm
from tbk_qgis.tbk.utility.tbk_utilities import ensure_dir


class TBkStandDelineationAlgorithm(TBkProcessingAlgorithm):
    """
    todo
    """
    # ------- Define Constants -------#
    # Constants used to refer to parameters and outputs.

    # These constants will be used when calling the algorithm from another algorithm,
    # or when calling from the QGIS console.

    # Directory containing the output files
    OUTPUT_ROOT = "output_root"
    # Directory containing the working_root output files
    WORKING_ROOT = "working_root"
    # Default log file name
    LOGFILE_NAME = "logfile_name"
    # VHM 10m as main TBk input
    VHM_10M = "vhm_10m"
    # Coniferous raster to be used during stand delineation
    CONIFEROUS_RASTER_FOR_CLASSIFICATION = "coniferous_raster_for_classification"
    # Zone raster
    ZONE_RASTER_FILE = "zoneRasterFile"
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

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and outputs of the algorithm.
        """
        # --- Parameters
        # VHM 10m as main TBk input
        self.addParameter(QgsProcessingParameterRasterLayer(self.VHM_10M,
                                                            "VHM 10m as main TBk input  (.tif)"))

        # Coniferous raster to calculate stand mean
        self.addParameter(QgsProcessingParameterRasterLayer(self.CONIFEROUS_RASTER_FOR_CLASSIFICATION,
                                                            "Coniferous raster to be used during stand "
                                                            "delineation (.tif)\nA simplified binarized "
                                                            "raster may achieve better results",
                                                            optional=True))

        # Folder for algorithm output
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_ROOT,
                                                                  "Output folder (a subfolder with timestamp will be "
                                                                  "created within)"))

        # Folder for root output, used for displaying in algorithm help when called from the console
        self.add_hidden_parameter(QgsProcessingParameterFolderDestination(self.WORKING_ROOT,
                                                                          "Output subfolder containing the working "
                                                                          "root files",
                                                                          optional=True))

        # --- Advanced Parameters

        # Main TBk Algorithm parameters

        parameter = QgsProcessingParameterString(self.LOGFILE_NAME, "Log File Name (.log)",
                                                 defaultValue="tbk_processing.log")
        self.add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterString(self.DESCRIPTION, "Short description",
                                                 defaultValue="TBk dataset")
        self.add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_TOL, "Relative min tolerance",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0.1)
        self.add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MAX_TOL, "Relative max tolerance",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0.1)
        self.add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_CORR, "Extension of the range down [m]",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=4)
        self.add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MAX_CORR, "Extension of the range up [m]",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=4)
        self.add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_VALID_CELLS,
                                                 "Minimum relative amount of valid cells",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0.5)
        self.add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_CELLS_PER_STAND, "Minimum cells per stand",
                                                 type=QgsProcessingParameterNumber.Integer, defaultValue=10)
        self.add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_CELLS_PER_PURE_STAND,
                                                 "Minimum cells for pure mixture stands",
                                                 type=QgsProcessingParameterNumber.Integer, defaultValue=30)
        self.add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.VHM_MIN_HEIGHT, "VHM minimum height",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0)
        self.add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.VHM_MAX_HEIGHT, "VHM maximum height",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=60)
        self.add_advanced_parameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # --- get and check input parameters
        # --- get input parameters
        inputs = self.get_inputs(parameters, context)

        # handle output root input
        output_root = inputs.output_root
        working_root = self.get_working_root_path(output_root)
        ensure_dir(working_root)
        tmp_output_folder = self.get_tmp_output_path(working_root)

        # get and check description
        description = inputs.description

        # set logger
        self.configure_logging(working_root, inputs.logfile_name)
        log = logging.getLogger('Stand Delineation')

        # check tif files extension
        self.check_tif_extension(inputs.vhm_10m, self.VHM_10M)
        if inputs.coniferous_raster_for_classification:
            self.check_tif_extension(inputs.coniferous_raster_for_classification,
                                     self.CONIFEROUS_RASTER_FOR_CLASSIFICATION)

        # ------- TBk Processing --------#
        # --- Stand delineation (Main)
        log.info(f'Starting')

        # None correspond to the zone_raster_file that is not used
        output = run_stand_classification(working_root, tmp_output_folder,
                                 inputs.vhm_10m, inputs.coniferous_raster_for_classification,
                                 None, description,
                                 inputs.min_tol, inputs.max_tol,
                                 inputs.min_corr, inputs.max_corr,
                                 inputs.min_valid_cells, inputs.min_cells_per_stand, inputs.min_cells_per_pure_stand,
                                 inputs.vhm_min_height, inputs.vhm_max_height)

        return {'WORKING_ROOT': output}

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
        return 'Delineate Stand'

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('Stand classification based on a vegetation height raster. The vegetation height raster (VHM) is '
                'usually a 10x10m max height raster from LiDAR or stereo image matching data.')
