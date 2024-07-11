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

from qgis.core import (QgsProcessingParameterFile,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber)
from tbk_qgis.tbk.bk_core.tbk_create_stands import run_stand_classification
from tbk_qgis.tbk.bk_core.tbk_qgis_processing_algorithm import TBkProcessingAlgorithm
from tbk_qgis.tbk.utility.persistence_utility import write_dict_to_toml_file
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
    # Folder for storing all input files and saving output files
    WORKING_ROOT = "working_root"
    # File storing configuration parameters
    CONFIG_FILE = "config_file"
    # Default log file name
    LOGFILE_NAME = "logfile_name"
    # VHM 10m as main TBk input
    VHM_10M = "vhm_10m"
    # Coniferous raster to be used during stand delineation
    CONIFEROUS_RASTER_FOR_CLASSIFICATION = "coniferous_raster_for_classification"
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

        # Config file containing all parameter key-value pairs
        self.addParameter(QgsProcessingParameterFile(self.CONFIG_FILE,
                                                     'Configuration file to set the algorithm parameters. The bellow '
                                                     'non-optional parameters must still be set but will not be used.',
                                                     extension='toml',
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

        # Working root folder. This is set only to be displayed when calling the algorithm help from the console
        self._add_hidden_parameter(QgsProcessingParameterFolderDestination(self.WORKING_ROOT,
                                                                          "Output subfolder containing the working "
                                                                          "root files",
                                                                           optional=True))

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

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # --- get and check input parameters

        # use the config file parameters if given, else input parameters
        params = self._get_input_or_config_params(parameters, context)

        # Handle the working root and temp output folders
        output_root = params.output_root
        working_root = self._get_working_root_path(output_root)
        ensure_dir(working_root)
        tmp_output_folder = self._get_tmp_output_path(working_root)

        # set logger
        log = self._configure_logging(working_root, params.logfile_name)

        # check tif files extension
        self._check_tif_extension(params.vhm_10m, self.VHM_10M)
        if params.coniferous_raster_for_classification:
            self._check_tif_extension(params.coniferous_raster_for_classification,
                                      self.CONIFEROUS_RASTER_FOR_CLASSIFICATION)

        # Write the used parameters in a toml file
        try:
            write_dict_to_toml_file(params.__dict__, working_root)
        except Exception:
            feedback.pushWarning('The TOML file was not writen in the output folder because an error occurred')

        # ------- TBk Processing --------#
        # --- Stand delineation (Main)
        log.info(f'Starting')

        # None correspond to the zone_raster_file that is not used yet
        output = run_stand_classification(working_root, tmp_output_folder,
                                          params.vhm_10m, params.coniferous_raster_for_classification,
                                          None, params.description,
                                          params.min_tol, params.max_tol,
                                          params.min_corr, params.max_corr,
                                          params.min_valid_cells, params.min_cells_per_stand,
                                          params.min_cells_per_pure_stand,
                                          params.vhm_min_height, params.vhm_max_height)

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
        return '1 Delineate Stand'

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('Stand classification based on a vegetation height raster. The vegetation height raster (VHM) is '
                'usually a 10x10m max height raster from LiDAR or stereo image matching data.')
