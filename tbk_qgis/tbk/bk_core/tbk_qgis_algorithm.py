# -*- coding: utf-8 -*-
# *************************************************************************** #
# TBk main algorithm for stand delineation (incl. post processing)
#
# Authors: Hannes Horneber, Dominique Weber, Christoph Schaller (BFH-HAFL)
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

__author__ = 'Berner Fachhochschule HAFL'
__date__ = '2020-08-03'
__copyright__ = '(C) 2023 by Berner Fachhochschule HAFL'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import shutil

if __name__ == "__main__":  # this will be invoked if this module is being run directly, but not via import!
    __package__ = 'bk_core'  # make sure relative imports work when testing

# --- Imports
import os
from shutil import copyfile
from datetime import timedelta
import time
import logging, logging.handlers
import sys

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterDefinition,

                       QgsApplication)

from .tbk_create_stands import *
from .post_process import *
from .merge_similar_neighbours import *
from .clip_to_perimeter import *
from .calculate_dg import *
from .add_coniferous_proportion import *
from .attributes_default import *
from tbk_qgis.tbk.utility.tbk_utilities import dict_diff
from tbk_qgis.tbk.utility.qgis_processing_utility import QgisHandler
from tbk_qgis.tbk.utility.persistence_utility import (read_dict_from_toml_file,
                                                      write_dict_to_toml_file)


class TBkAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    def addAdvancedParameter(self, parameter):
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        return self.addParameter(parameter)

    def addHiddenParameter(self, parameter):
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagHidden)
        return self.addParameter(parameter)

    # ------- Define Constants -------#
    # Constants used to refer to parameters and outputs.

    # These constants will be used when calling the algorithm from another algorithm,
    # or when calling from the QGIS console.

    OUTPUT = "OUTPUT"

    # Directory containing the output folder
    OUTPUT_ROOT = "output_root"
    # Directory containing the output files and subfolders with tmp and processing files
    WORKING_ROOT = "working_root"
    # File storing the parameters
    CONFIG_FILE = "config_file"
    # VHM 10m as main TBk input
    VHM_10M = "vhm_10m"
    # VHM 150cm to calculate DG                                  
    VHM_150CM = "vhm_150cm"
    # Coniferous raster to calculate stand mean                                  
    CONIFEROUS_RASTER = "coniferous_raster"
    # Coniferous raster to be used during stand delineation
    CONIFEROUS_RASTER_FOR_CLASSIFICATION = "coniferous_raster_for_classification"
    # Perimeter shapefile to clip final result                                 
    PERIMETER = "perimeter"

    # Whether to clip the VHM prior to classification
    CLIP_VHM_BEFORE = "clip_vhm_before"

    # Default log file name
    # Will be stored in the result directory
    LOGFILE_NAME = "logfile_name"

    # --- Advanced Parameters

    # VegZone parameters
    # Default Vegetation Zone
    VEGZONE_DEFAULT = "vegZoneDefault"
    # Vegetation Zone layer (polygons) for spatial join
    VEGZONE_LAYER = "vegZoneLayer"
    # Vegetation Zone Code field (in layer)
    VEGZONE_LAYER_FIELD = "vegZoneLayerField"
    # Default Forest Site Category
    FORESTSITE_DEFAULT = "forestSiteDefault"
    # Forest Site Category layer (polygons) for spatial join
    FORESTSITE_LAYER = "forestSiteLayer"
    # Forest Site Category field (in layer)
    FORESTSITE_LAYER_FIELD = "forestSiteLayerField"

    # Main TBk parameters (for details see run_stand_classification function)
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
    # Simplification tolerance                                                   
    SIMPLIFICATION_TOLERANCE = "simplification_tolerance"

    # Additional parameters
    # Min. area to eliminate small stands
    MIN_AREA_M2 = "min_area_m2"
    # Min. area to merge similar stands                                              
    SIMILAR_NEIGHBOURS_MIN_AREA_M2 = "similar_neighbours_min_area"
    # hdom relative diff to merge similar stands                                  
    SIMILAR_NEIGHBOURS_HDOM_DIFF_REL = "similar_neighbours_hdom_diff_rel"
    # Also calc coniferous prop. for main layer                          
    CALC_MIXTURE_FOR_MAIN_LAYER = "calc_mixture_for_main_layer"
    # Delete temporary files and fields
    DEL_TMP = "del_tmp"

    # ------- List of Algorithm Parameters -------#
    # Parameters with default values
    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along with some other properties.
        """
        # Config file containing all parameter values
        self.addParameter(QgsProcessingParameterFile(self.CONFIG_FILE,
                                                     self.tr(
                                                         'Configuration file to set the parameters of the algorithm.\n'
                                                         'Parameters set in the file will overwrite the settings below.'),
                                                     optional=True))

        # VHM 10m as main TBk input
        self.addParameter(QgsProcessingParameterRasterLayer(self.VHM_10M,
                                                            self.tr("VHM 10m as main TBk input  (.tif)")))
        # VHM 150cm to calculate DG                                  
        self.addParameter(QgsProcessingParameterRasterLayer(self.VHM_150CM,
                                                            self.tr("VHM 150cm to calculate DG (.tif)")))
        # Coniferous raster to calculate stand mean                                  
        self.addParameter(QgsProcessingParameterRasterLayer(self.CONIFEROUS_RASTER,
                                                            self.tr("Coniferous raster to calculate stand mean (.tif)"),
                                                            optional=True))
        # Coniferous raster to calculate stand mean
        self.addParameter(QgsProcessingParameterRasterLayer(self.CONIFEROUS_RASTER_FOR_CLASSIFICATION,
                                                            self.tr(
                                                                "Coniferous raster to be used during stand delineation (.tif)"
                                                                "\nA simplified binarized raster may achieve better results (optional)"),
                                                            optional=True))
        # Perimeter shapefile to clip final result                                 
        self.addParameter(
            QgsProcessingParameterFeatureSource(self.PERIMETER, self.tr("Perimeter shapefile to clip final result"),
                                                [QgsProcessing.TypeVectorPolygon]))

        # Folder for algorithm output
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_ROOT, self.tr('Output folder'
                                                                                            '\n(a subfolder with timestamp will be created within)')))

        # --- Advanced Parameters

        # Fields for Vegetation Zone
        self.addAdvancedParameter(QgsProcessingParameterNumber(self.VEGZONE_DEFAULT, self.tr(
            "Vegetation Zone default (Code). Will be applied if no vegetation zone can be assigned from VegZone layer."
            "\n1 - hyperinsubric, 2/3 - colline /with beech, 4 - submontane, "
            "\n5 - lower montane, 6 - upper montane, 8 - high montane, 9 - sub alpine"
        ), type=QgsProcessingParameterNumber.Integer, defaultValue=2))
        self.addAdvancedParameter(
            QgsProcessingParameterFeatureSource(self.VEGZONE_LAYER, self.tr("Vegetation Zone layer"),
                                                [QgsProcessing.TypeVectorPolygon], optional=True))
        self.addAdvancedParameter(
            QgsProcessingParameterField(self.VEGZONE_LAYER_FIELD, 'Vegetation Zone Code field (in layer)',
                                        type=QgsProcessingParameterField.Numeric,
                                        parentLayerParameterName=self.VEGZONE_LAYER, allowMultiple=False,
                                        defaultValue='Code', optional=True))

        # Fields for Forest Site Category
        self.addAdvancedParameter(
            QgsProcessingParameterString(self.FORESTSITE_DEFAULT, self.tr("Forest Site Category (Code, e.g. 7a)"),
                                         optional=True))
        self.addAdvancedParameter(
            QgsProcessingParameterFeatureSource(self.FORESTSITE_LAYER, self.tr("Forest Site Category layer"),
                                                [QgsProcessing.TypeVectorPolygon], optional=True))
        self.addAdvancedParameter(
            QgsProcessingParameterField(self.FORESTSITE_LAYER_FIELD, 'Forest Site Category field (in layer)',
                                        type=QgsProcessingParameterField.Any,
                                        parentLayerParameterName=self.FORESTSITE_LAYER, allowMultiple=False,
                                        optional=True))

        # Main TBk Algorithm parameters
        parameter = QgsProcessingParameterRasterLayer(self.ZONE_RASTER_FILE, self.tr("Zone raster (.tif)"),
                                                      optional=True)
        self.addHiddenParameter(parameter)

        parameter = QgsProcessingParameterString(self.LOGFILE_NAME, self.tr("Log File Name (.log)"),
                                                 defaultValue="tbk_processing.log")
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterString(self.DESCRIPTION, self.tr("Short description"),
                                                 defaultValue="TBk dataset")
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_TOL, self.tr("Relative min tolerance"),
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0.1)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MAX_TOL, self.tr("Relative max tolerance"),
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0.1)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_CORR, self.tr("Extension of the range down [m]"),
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=4)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MAX_CORR, self.tr("Extension of the range up [m]"),
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=4)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_VALID_CELLS,
                                                 self.tr("Minimum relative amount of valid cells"),
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0.5)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_CELLS_PER_STAND, self.tr("Minimum cells per stand"),
                                                 type=QgsProcessingParameterNumber.Integer, defaultValue=10)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_CELLS_PER_PURE_STAND,
                                                 self.tr("Minimum cells for pure mixture stands"),
                                                 type=QgsProcessingParameterNumber.Integer, defaultValue=30)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.VHM_MIN_HEIGHT, self.tr("VHM minimum height"),
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.VHM_MAX_HEIGHT, self.tr("VHM maximum height"),
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=60)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.SIMPLIFICATION_TOLERANCE, self.tr("Simplification tolerance [m]"),
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=8)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_AREA_M2, self.tr("Min. area to eliminate small stands"),
                                                 type=QgsProcessingParameterNumber.Integer, defaultValue=1000)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.SIMILAR_NEIGHBOURS_MIN_AREA_M2,
                                                 self.tr("Min. area to merge similar stands"),
                                                 type=QgsProcessingParameterNumber.Integer, defaultValue=2000)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.SIMILAR_NEIGHBOURS_HDOM_DIFF_REL,
                                                 self.tr("hdom relative diff to merge similar stands"),
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0.15)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.CALC_MIXTURE_FOR_MAIN_LAYER,
                                                  self.tr("Also calc coniferous prop. for main layer (Oberschicht).\n"
                                                          "Has no effect if no mixture raster is provided."),
                                                  defaultValue=True)
        self.addAdvancedParameter(parameter)

        # Additional parameters
        parameter = QgsProcessingParameterBoolean(self.DEL_TMP, self.tr("Delete temporary files and fields"),
                                                  defaultValue=True)
        self.addAdvancedParameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # ------- INIT Algorithm -------#

        # settings_path = QgsApplication.qgisSettingsDirPath()
        # tbk_tool_path = os.path.join(settings_path,"python/plugins/tbk_qgis")
        tbk_tool_path = os.path.dirname(__file__)  # needed for calling create project script

        # --- get and check input parameters

        # get configuration file path
        config_path = str(self.parameterAsFile(parameters, self.CONFIG_FILE, context))
        if config_path:
            # Set input parameters from config file
            try:
                config = read_dict_from_toml_file(config_path)
                # compare config file parameters and tool parameters
                config_removed, config_added, config_changed = dict_diff(parameters, config)

                # apply config_file to parameters (overwrite values in parameters if they have an entry in config_file values)
                parameters.update(config)
                feedback.pushInfo(f'Read config file: ')
                feedback.pushInfo(f'Parameters overwritten through provided config file:')
                feedback.pushInfo(f'{list(config_changed.keys())}')
                feedback.pushInfo(f'Parameters not contained in config file (using values from tool-dialog/defaults):')
                feedback.pushInfo(f'{list(config_removed.keys())}')
                feedback.pushInfo(f'Unused config file parameters:')
                feedback.pushInfo(f'{list(config_added.keys())}')
            except FileNotFoundError:
                raise QgsProcessingException(f"The configuration file was not found at this location: {config_path}")

        # get and check general input parameters
        output_root = self.parameterAsString(parameters, self.OUTPUT_ROOT, context)
        # get and check logfile
        logfile_name = str(self.parameterAsString(parameters, self.LOGFILE_NAME, context))
        if (not logfile_name) or logfile_name == "":
            raise QgsProcessingException("no logfile name specified")

        # get and check paths to VHMs
        vhm_10m = str(self.parameterAsRasterLayer(parameters, self.VHM_10M, context).source())
        if not os.path.splitext(vhm_10m)[1].lower() in (".tif", ".tiff"):
            raise QgsProcessingException("vhm_10m must be a TIFF file")
        vhm_150cm = str(self.parameterAsRasterLayer(parameters, self.VHM_150CM, context).source())
        if not os.path.splitext(vhm_150cm)[1].lower() in (".tif", ".tiff"):
            raise QgsProcessingException("vhm_150cm must be a TIFF file")

        # get coniferous_raster_layer path and check for TIFF if provided (else it is "")
        coniferous_raster_layer = self.parameterAsRasterLayer(parameters, self.CONIFEROUS_RASTER, context)
        # convert raster layer to path and check for TIFF
        coniferous_raster = ""
        if coniferous_raster_layer:
            coniferous_raster = str(coniferous_raster_layer.source())
        if coniferous_raster and (not os.path.splitext(coniferous_raster)[1].lower() in (".tif", ".tiff")):
            raise QgsProcessingException("coniferous_raster must be a TIFF file")

        # get coniferous_raster_for_classification path and check for TIFF if provided (else it is "")
        coniferous_raster_for_classification_layer \
            = self.parameterAsRasterLayer(parameters, self.CONIFEROUS_RASTER_FOR_CLASSIFICATION, context)
        # convert raster layer to path and check for TIFF
        coniferous_raster_for_classification = ""
        if coniferous_raster_for_classification_layer:
            coniferous_raster_for_classification = str(coniferous_raster_for_classification_layer.source())
            use_coniferous_raster = True
            print("Using coniferous raster for classification.")
        if coniferous_raster_for_classification and \
                (not os.path.splitext(coniferous_raster_for_classification)[1].lower() in (".tif", ".tiff")):
            raise QgsProcessingException("coniferous_raster_for_classification must be a TIFF file")

        # get calc_mixture_for_main_layer flag
        calc_mixture_for_main_layer = self.parameterAsBool(parameters, self.CALC_MIXTURE_FOR_MAIN_LAYER,
                                                           context)

        # get and check perimeter file
        perimeter = str(self.parameterAsVectorLayer(parameters, self.PERIMETER, context).source())

        # get and check zone raster file
        # get coniferous_raster_for_classification path and check for TIFF if provided (else it is None)
        zoneRasterFile_layer = self.parameterAsRasterLayer(parameters, self.ZONE_RASTER_FILE, context)
        zoneRasterFile = ""
        if zoneRasterFile_layer:
            zoneRasterFile = str(zoneRasterFile_layer.source())
        if zoneRasterFile and (not os.path.splitext(zoneRasterFile)[1].lower() in (".tif", ".tiff")):
            raise QgsProcessingException("zoneRasterFile must be a TIFF file")

        # get and check description
        description = str(self.parameterAsString(parameters, self.DESCRIPTION, context))
        if (not description) or description == "":
            description = "TBk dataset"
        # TODO use description for naming the output/project file

        # get and check join files/defaults
        vegZoneDefault = self.parameterAsInt(parameters, self.VEGZONE_DEFAULT, context)
        if self.parameterAsVectorLayer(parameters, self.VEGZONE_LAYER, context):
            vegZoneLayer = str(self.parameterAsVectorLayer(parameters, self.VEGZONE_LAYER, context).source())
        else:
            vegZoneLayer = None
        vegZoneLayerField = self.parameterAsString(parameters, self.VEGZONE_LAYER_FIELD, context)
        if vegZoneLayer and not vegZoneLayerField:
            raise QgsProcessingException("vegZoneLayer provided but no vegZoneLayerField for join")
        forestSiteDefault = str(self.parameterAsString(parameters, self.FORESTSITE_DEFAULT, context))
        if self.parameterAsVectorLayer(parameters, self.FORESTSITE_LAYER, context):
            forestSiteLayer = str(self.parameterAsVectorLayer(parameters, self.FORESTSITE_LAYER, context).source())
        else:
            forestSiteLayer = None
        forestSiteLayerField = self.parameterAsString(parameters, self.FORESTSITE_LAYER_FIELD, context)
        if forestSiteLayer and not forestSiteLayerField:
            raise QgsProcessingException("forestSiteLayer provided but no forestSiteLayerField for join")

        # get and check algorithm parameters
        min_tol = self.parameterAsDouble(parameters, self.MIN_TOL, context)
        max_tol = self.parameterAsDouble(parameters, self.MAX_TOL, context)
        min_corr = self.parameterAsDouble(parameters, self.MIN_CORR, context)
        max_corr = self.parameterAsDouble(parameters, self.MAX_CORR, context)
        min_valid_cells = self.parameterAsDouble(parameters, self.MIN_VALID_CELLS, context)
        min_cells_per_stand = self.parameterAsInt(parameters, self.MIN_CELLS_PER_STAND, context)
        min_cells_per_pure_stand = self.parameterAsInt(parameters, self.MIN_CELLS_PER_PURE_STAND, context)
        vhm_min_height = self.parameterAsDouble(parameters, self.VHM_MIN_HEIGHT, context)
        vhm_max_height = self.parameterAsDouble(parameters, self.VHM_MAX_HEIGHT, context)

        simplification_tolerance = self.parameterAsDouble(parameters, self.SIMPLIFICATION_TOLERANCE, context)

        min_area_m2 = self.parameterAsInt(parameters, self.MIN_AREA_M2, context)
        similar_neighbours_min_area = self.parameterAsInt(parameters, self.SIMILAR_NEIGHBOURS_MIN_AREA_M2,
                                                          context)
        similar_neighbours_hdom_diff_rel = self.parameterAsDouble(parameters,
                                                                  self.SIMILAR_NEIGHBOURS_HDOM_DIFF_REL,
                                                                  context)

        # get and check miscellaneous parameters
        del_tmp = self.parameterAsBool(parameters, self.DEL_TMP, context)

        # --- init directory
        ensure_dir(output_root)

        # Set up directory with timestamp in working_root
        output_root = os.path.join(output_root, '')  # Add the trailing slash if it's not already there.
        currentDatetime = datetime.now().strftime("%Y%m%d-%H%M")
        outputDirectory = currentDatetime
        tbk_result_dir = os.path.join(output_root, outputDirectory)
        tbk_result_dir = os.path.join(tbk_result_dir, '')  # Add the trailing slash if it's not already there.

        working_root = os.path.join(tbk_result_dir, 'bk_process', '')  # create subfolder (and add trailing slash)
        # create working root and all intermediate folders
        ensure_dir(working_root)
        tmp_output_folder = os.path.join(working_root, "tmp")
        # create tmp folder and all intermediate folders
        ensure_dir(tmp_output_folder)

        # --- configure logging
        logfile_tmp_path = os.path.join(working_root, logfile_name)

        # set up logging to file
        logging.basicConfig(
            filename=logfile_tmp_path,
            level=logging.DEBUG,
            format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
            # format="%(asctime)s; %(processName)s; %(levelname)s; %(name)s; %(message)s",
            datefmt='%H:%M:%S'
        )

        # set up logging to console
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

        # set up logging to QGIS feedback
        qgis_console = QgisHandler(feedback)
        qgis_console.setLevel(logging.DEBUG)
        # add the handler to the root logger
        logging.getLogger('').addHandler(qgis_console)

        # logger = logging.getLogger(__name__)
        # logging.basicConfig(
        #     level=logging.INFO,
        #     format="%(asctime)s; %(processName)s; %(levelname)s; %(name)s; %(message)s",
        #     handlers=[
        #         logging.FileHandler(logfile_tmp_path, mode='w'),
        #         QgisHandler(feedback),
        #         logging.StreamHandler()
        #     ])

        log = logging.getLogger('')
        log.info("====================================================================")
        log.info('Run TBk Generate BK')
        log.info("====================================================================")

        # ------- TBk MAIN Processing --------#

        # Store the input parameters in a file
        params_with_sources = self.asMap(parameters, context)['inputs']
        try:
            write_dict_to_toml_file(params_with_sources, working_root)
            log.info(f"Wrote input_config.txt with algorithm parameter configuration.\n")
        except Exception as error:
            feedback.pushWarning('The TOML file was not written in the output folder because an error occurred')
            feedback.pushWarning(f'Error: {error}')

        # Run TBk
        start_time = time.time()
        start_time_section = time.time()

        # --- Stand delineation (Main)
        log.info(' 1 --- Stand delineation')
        run_stand_classification(working_root, tmp_output_folder,
                                 vhm_10m,
                                 coniferous_raster_for_classification,  # is None if not provided, handled in function
                                 zoneRasterFile,
                                 description,
                                 min_tol, max_tol,
                                 min_corr, max_corr,
                                 min_valid_cells, min_cells_per_stand, min_cells_per_pure_stand,
                                 vhm_min_height, vhm_max_height)
        log.info("   --- done: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time_section))))
        log.info("   --- 15%" + " | estimated remaining time: %s (h:min:sec)\n" % str(
            timedelta(seconds=((time.time() - start_time) * 100 / 15 - (time.time() - start_time)))))

        # --- Simplify & Eliminate
        log.info(' 2 --- Simplify & Eliminate')
        start_time_section = time.time()
        post_process(working_root, tmp_output_folder, min_area_m2, simplification_tolerance=simplification_tolerance,
                     del_tmp=del_tmp)
        log.info("   --- done: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time_section))))
        log.info("   --- 30%" + " | estimated remaining time: %s (h:min:sec)\n" % str(
            timedelta(seconds=((time.time() - start_time) * 100 / 30 - (time.time() - start_time)))))

        # --- Merge similar neighbours
        log.info(' 3 --- Merge similar neighbours')
        start_time_section = time.time()
        merge_similar_neighbours(working_root, similar_neighbours_min_area,
                                 similar_neighbours_hdom_diff_rel,
                                 del_tmp=del_tmp)
        log.info("   --- done: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time_section))))
        log.info("   --- 50%" + " | estimated remaining time: %s (h:min:sec)\n" % str(
            timedelta(seconds=((time.time() - start_time) * 100 / 50 - (time.time() - start_time)))))

        # --- Clip to perimeter and eliminate gaps
        log.info(' 4 --- Clip to perimeter and eliminate gaps')
        start_time_section = time.time()
        # run clip function
        clip_to_perimeter(working_root, tmp_output_folder, perimeter, del_tmp=del_tmp)
        # run gaps function
        eliminate_gaps(working_root, tmp_output_folder, perimeter, del_tmp=del_tmp)
        log.info("   --- done: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time_section))))
        log.info("   --- 65%" + " | estimated remaining time: %s (h:min:sec)\n" % str(
            timedelta(seconds=((time.time() - start_time) * 100 / 65 - (time.time() - start_time)))))

        # --- Calculate DG
        log.info(' 5 --- Calculate DG')
        start_time_section = time.time()
        calculate_dg(working_root, tmp_output_folder, tbk_result_dir, vhm_150cm, del_tmp=del_tmp)
        log.info("   --- done: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time_section))))
        log.info("   --- 80%" + " | estimated remaining time: %s (h:min:sec)\n" % str(
            timedelta(seconds=((time.time() - start_time) * 100 / 80 - (time.time() - start_time)))))

        # --- Add coniferous proportion
        if coniferous_raster:
            log.info(' 6 --- Add coniferous proportion')
            start_time_section = time.time()
            add_coniferous_proportion(working_root, tmp_output_folder, tbk_result_dir, coniferous_raster,
                                      calc_mixture_for_main_layer, del_tmp=del_tmp)
            log.info("   --- done: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time_section))))
            log.info("   --- 85%" + " | estimated remaining time: %s (h:min:sec)\n" % str(
                timedelta(seconds=((time.time() - start_time) * 100 / 85 - (time.time() - start_time)))))

        # --- Calc specific attributes
        log.info(' 7 --- Calc specific attributes')
        start_time_section = time.time()
        stands_file_attributed = calc_attributes(working_root, tmp_output_folder, tbk_result_dir, del_tmp=del_tmp)
        log.info("   --- done: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time_section))))

        # --- Cleanup stand file
        log.info(' 8 --- Run clean up')
        start_time_section = time.time()
        stands_file_cleaned = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_clean.gpkg")
        processing.run("TBk:TBk postprocess Cleanup", {
            'tbk_bestandeskarte': stands_file_attributed,
            'Tbk_bestandeskarte_clean': stands_file_cleaned})
        log.info("   --- done: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time_section))))
        log.info("   --- 90%" + " | estimated remaining time: %s (h:min:sec)\n" % str(
            timedelta(seconds=((time.time() - start_time) * 100 / 90 - (time.time() - start_time)))))

        # --- Append attributes from join layers
        log.info(' 9 --- Append attributes from join layers')
        start_time_section = time.time()
        # join VegZone if layer is provided
        if vegZoneLayer:
            stands_file_join = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_vegZone1join.gpkg")
            param = {'layer_to_join_attribute_on': stands_file_cleaned,
                     'attribute_layer': vegZoneLayer,
                     'fields_to_join': [vegZoneLayerField], 'joined_attributes_prefix': 'VegZone_',
                     'output_with_attribute': stands_file_join}
            processing.run("TBk:Optimized Spatial Join", param)

            # rename field to VegZone_Code (if vegZoneLayerField is anything other than "Code")
            vegZone_output_fieldname = 'VegZone_' + vegZoneLayerField
            if not (vegZone_output_fieldname == "VegZone_Code"):
                stands_file_rename = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_vegZone2Rename.gpkg")
                processing.run("native:renametablefield", {
                    'INPUT': stands_file_join,
                    'FIELD': vegZone_output_fieldname, 'NEW_NAME': 'VegZone_Code',
                    'OUTPUT': stands_file_rename})
                # make output the input of nextstep
                stands_file_join = stands_file_rename

            # make output the input of nextstep
            stands_file_cleaned = stands_file_join

        # create field VegZone_Code (if not already existent through join) and fill (NULL values) with default
        stands_file_appended = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_vegZone3.gpkg")
        formula = f'if("VegZone_Code","VegZone_Code", {vegZoneDefault})'
        processing.run("native:fieldcalculator", {
            'INPUT': stands_file_cleaned,
            'FIELD_NAME': 'VegZone_Code', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
            'FORMULA': formula, 'OUTPUT': stands_file_appended})

        # join if layer is provided
        if forestSiteLayer:
            stands_file_join = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_ForestSite1join.gpkg")
            param = {'layer_to_join_attribute_on': stands_file_appended,
                     'attribute_layer': forestSiteLayer,
                     'fields_to_join': [forestSiteLayerField], 'joined_attributes_prefix': 'ForestSite_',
                     'output_with_attribute': stands_file_join}
            processing.run("TBk:Optimized Spatial Join", param)

            # rename field to ForestSite
            forestSite_output_fieldname = 'ForestSite_' + forestSiteLayerField
            stands_file_rename = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_ForestSite2Rename.gpkg")
            processing.run("native:renametablefield", {
                'INPUT': stands_file_join,
                'FIELD': forestSite_output_fieldname, 'NEW_NAME': 'ForestSite',
                'OUTPUT': stands_file_rename})

            # make output the input of nextstep
            stands_file_appended = stands_file_rename

        if (forestSiteDefault is not None) and not (forestSiteDefault == ""):
            # create field ForestSite_Code (if not already existent through join) and fill (NULL values) with default
            stands_file_forestSite = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_ForestSite3.gpkg")
            formula = f'if("ForestSite","ForestSite", \'{forestSiteDefault}\')'
            processing.run("native:fieldcalculator", {
                'INPUT': stands_file_appended,
                'FIELD_NAME': 'ForestSite', 'FIELD_TYPE': 2, 'FIELD_LENGTH': 80, 'FIELD_PRECISION': 0,
                'FORMULA': formula, 'OUTPUT': stands_file_forestSite})
            stands_file_appended = stands_file_forestSite

        log.info("   --- done: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time_section))))
        log.info("   --- 95%" + " | estimated remaining time: %s (h:min:sec)\n" % str(
            timedelta(seconds=((time.time() - start_time) * 100 / 95 - (time.time() - start_time)))))

        # --- Clean up unneeded fields
        log.info('10 --- Remove obsolete fields in TBk_Bestandeskarte')
        start_time_section = time.time()
        # remove fid with processing tool, as deleting doesn't seem to work
        # stands_file_fid_del = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_fiddel.gpkg")
        stands_file_final = os.path.join(tbk_result_dir, "TBk_Bestandeskarte.gpkg")

        processing.run("native:deletecolumn", {
            'INPUT': stands_file_appended,
            'COLUMN': ['fid', 'FID_orig', 'OBJECTID', 'NH_CLASS'],
            'OUTPUT': stands_file_final})
        log.info("   --- done: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time_section))))

        # --- Delete tmp directory
        if del_tmp:
            log.info(f'11 --- Delete temporary files: {tmp_output_folder}')
            start_time_section = time.time()
            # TODO: this usually fails with a Permission Error, since QGIS doesn't seem to close the file handles
            # PermissionError: [WinError 32] The process cannot access the file because it is being used by another process:
            # 'C:\\Users\\hbh1\\Projects\\H07_TBk\\Dev\\TBk_QGIS_Plugin\\data\\tbk_hafl\\tbk2012_v02\\20240414-2304\\bk_process\\tmp\\gaps_single_tmp.gpkg'
            # shutil.rmtree(tmp_output_folder, ignore_errors=True)
            log.info("   --- done: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time_section))))

        # --- Create default Project
        log.info('12 --- Create default Project')
        start_time_section = time.time()
        # os.system("\"" + arcgis_python + "\" " + tbk_tool_path + "\\post_processing_arcpy\\create_mxd.py" +
        #           " " + working_root + " " + tbk_tool_path + " " + working_root + " " + vhm_10m + " " + vhm_150cm)

        # Run Script in separate process, since otherwise the current project would be unloaded
        # make sure the called python environment has all necessary modules on PYTHONPATH
        qgisPath = QgsApplication.prefixPath()
        qgisPythonPath = os.path.join(qgisPath, "python")
        if "PYTHONPATH" in os.environ:
            # append to PYTHONPATH
            os.environ["PYTHONPATH"] = qgisPythonPath + os.pathsep + os.environ["PYTHONPATH"]
        else:
            # create PYTHONPATH
            os.environ["PYTHONPATH"] = qgisPythonPath

        # construct a python call command with all necessary paramters and call
        script_path = os.path.join(tbk_tool_path, "create_project.py")
        command = "python3.exe \"" + script_path.replace("\\", "/") + "\" \"" \
                  + working_root.replace("\\", "/") + "\" \"" \
                  + tmp_output_folder.replace("\\", "/") + "\" \"" \
                  + tbk_result_dir.replace("\\", "/") + "\" \"" \
                  + tbk_tool_path.replace("\\", "/") + "\" \"" \
                  + vhm_10m + "\" \"" \
                  + vhm_150cm + "\" \"" \
                  + coniferous_raster + "\" \"" \
                  + str(del_tmp) + "\""

        log.info(command)
        os.system(command)

        # if del_tmp:
        #     output_tmp_folder = os.path.join(working_root,"tmp")
        #     if os.path.isdir(output_tmp_folder):
        #         shutil.rmtree(output_tmp_folder)

        # --- Copy temporary logfile to result directory
        # log.info("Copy logfile from: " + logfile_tmp_path)
        # logfile = os.path.join(working_root, logfile_name)
        # log.info("Copy logfile to: " + logfile)
        # copyfile(logfile_tmp_path, logfile)

        log.info("   --- done: %s (h:min:sec)\n" % str(timedelta(seconds=(time.time() - start_time_section))))
        # finished
        feedback.pushInfo("====================================================================")
        feedback.pushInfo("FINISHED")
        feedback.pushInfo("TOTAL PROCESSING TIME: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time))))
        feedback.pushInfo("====================================================================")
        log.info("====================================================================")
        log.info("FINISHED")
        log.info("TOTAL PROCESSING TIME: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time))))
        log.info("====================================================================")

        #        # Compute the number of steps to display within the progress bar and
        #        # get features from source
        #        total = 100.0 / source.featureCount() if source.featureCount() else 0
        #        features = source.getFeatures()
        #
        #        for current, feature in enumerate(features):
        #            # Stop the algorithm if cancel button has been clicked
        #            if feedback.isCanceled():
        #                break
        #
        #            # Add a feature in the sink
        #            #sink.addFeature(feature, QgsFeatureSink.FastInsert)
        #
        #            # Update the progress bar
        #            feedback.setProgress(int(current * total))

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: working_root}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Generate BK'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        # return self.tr(self.groupId())
        return '1 Bk generation (core)'

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'tbkcore'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TBkAlgorithm()
