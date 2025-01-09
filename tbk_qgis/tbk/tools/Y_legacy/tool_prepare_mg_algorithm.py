# -*- coding: utf-8 -*-
# *************************************************************************** #
# Prepare Miximg Degree raster as input for TBk.
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

import time
from datetime import timedelta

from osgeo.gdalnumeric import *


from qgis.PyQt.QtCore import QCoreApplication
import processing

from tbk_qgis.tbk.general.tbk_utilities import *

from .pre_processing_helper import PreProcessingHelper
from tbk_qgis.tbk.general.persistence_utility import (read_dict_from_toml_file,
                                         write_dict_to_toml_file)
from .tbk_qgis_processing_algorithm_toolsY import TBkProcessingAlgorithmToolY

class TBkPrepareMgAlgorithm(TBkProcessingAlgorithmToolY):
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

    def deleteRasterIfExists (self, raster_path):
        if os.path.exists(raster_path):
            delete_raster(raster_path)

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    # File storing the parameters
    CONFIG_FILE = "config_file"

    # Directory containing the input files
    OUTPUT_ROOT = "output_root"

    OUTPUT = "OUTPUT"

    # input
    MG_INPUT = "mg_input"
    VHM_10M = "vhm_10m"

    RECLASSIFY_MG_VALUES = "reclassify_mg_values"

    # output
    MG_OUTPUT = "mg_output"

    # advanced params
    MIN_LH = "min_lh"
    MAX_LH = "max_lh"
    MIN_NH = "min_nh"
    MAX_NH = "max_nh" 
    DEL_TMP ="del_tmp"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # Config file containing all parameter values
        self.addParameter(QgsProcessingParameterFile(self.CONFIG_FILE,
                                                     self.tr(
                                                         'Configuration file to set the parameters of the algorithm. '
                                                         'The parameters set in the file does not need to be set '
                                                         'bellow'),
                                                     optional=True))

        # input
        self.addParameter(QgsProcessingParameterRasterLayer(self.MG_INPUT, self.tr("Mixing degree 10m input (.tif)")))                                
        self.addParameter(QgsProcessingParameterRasterLayer(self.VHM_10M, self.tr("VHM 10m reference input (.tif)")))                                

        # Folder for algo output
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_ROOT,self.tr('Output folder')))

        ## output
        parameter = QgsProcessingParameterString(self.MG_OUTPUT, self.tr("Mixing degree output name (.tif)"),defaultValue = "MG.tif")
        self.addParameter(parameter)


        # reclassify values
        parameter = QgsProcessingParameterNumber(self.MIN_LH, self.tr("Minimum Laubholz value"), type=QgsProcessingParameterNumber.Integer, defaultValue=1)
        self.addParameter(parameter)  

        parameter = QgsProcessingParameterNumber(self.MAX_LH, self.tr("Maximum Laubholz value"), type=QgsProcessingParameterNumber.Integer, defaultValue=5000)
        self.addParameter(parameter)  

        parameter = QgsProcessingParameterNumber(self.MIN_NH, self.tr("Minimum Nadelholz value"), type=QgsProcessingParameterNumber.Integer, defaultValue=5000)
        self.addParameter(parameter)  

        parameter = QgsProcessingParameterNumber(self.MAX_NH, self.tr("Maximum Nadelholz value"), type=QgsProcessingParameterNumber.Integer, defaultValue=10000)
        self.addParameter(parameter) 

        # advanced params
        parameter = QgsProcessingParameterBoolean(self.RECLASSIFY_MG_VALUES, self.tr("Reclassify MG Values"), defaultValue=True)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.DEL_TMP, self.tr("Delete temporary files"), defaultValue=True)
        self.addAdvancedParameter(parameter)


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

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

        output_root = self.parameterAsString(parameters, self.OUTPUT_ROOT, context)

        settings_path = QgsApplication.qgisSettingsDirPath()
        feedback.pushInfo(settings_path)

        tbk_tool_path = os.path.join(settings_path,"python/plugins/tbk_qgis")

        # todo: use same variable name/description/error as the main algorithm
        # input
        mg_input = str(self.parameterAsRasterLayer(parameters, self.MG_INPUT, context).source())
        if not os.path.splitext(mg_input)[1].lower() in (".tif",".tiff"):
            raise QgsProcessingException("mg_input must be TIFF file")

        vhm_10m = str(self.parameterAsRasterLayer(parameters, self.VHM_10M, context).source())
        if not os.path.splitext(vhm_10m)[1].lower() in (".tif",".tiff"):
            raise QgsProcessingException("vhm_10m must be TIFF file")

        # Folder for algo output
        output_root = self.parameterAsString(parameters, self.OUTPUT_ROOT, context)

        # output
        mg_output = str(self.parameterAsString(parameters, self.MG_OUTPUT, context))
        if (not mg_output) or mg_output == "":
            raise QgsProcessingException("no MG output file name specified")
        if not os.path.splitext(mg_output)[1].lower() in (".tif",".tiff"):
            raise QgsProcessingException("mg_output must be TIFF file")

        # reclassify values
        min_lh = self.parameterAsInt(parameters, self.MIN_LH, context)
        max_lh = self.parameterAsInt(parameters, self.MAX_LH, context)
        min_nh = self.parameterAsInt(parameters, self.MIN_NH, context)
        max_nh = self.parameterAsInt(parameters, self.MAX_NH, context)

        reclassify_mg_values = self.parameterAsBool(parameters, self.RECLASSIFY_MG_VALUES, context)
        del_tmp = self.parameterAsBool(parameters, self.DEL_TMP, context)
        
        ensure_dir(output_root)
        working_root = output_root

        mg_output = os.path.join(output_root,mg_output)
        self.deleteRasterIfExists(mg_output)

        # Store the input parameters in a file
        params_with_sources = self.asMap(parameters, context)['inputs']
        try:
            write_dict_to_toml_file(params_with_sources, output_root)
        except Exception as error:
            feedback.pushWarning('The TOML file was not written in the output folder because an error occurred')
            feedback.pushWarning(f'Error: {error}')

        start_time = time.time()

        # tmp files
        tmp_mg_aligned = os.path.join(output_root, "tmp_mg_aligned.tif")
        self.deleteRasterIfExists(tmp_mg_aligned)


        feedback.pushInfo("match extent, align pixels...")
        xmin, ymin, xmax, ymax = PreProcessingHelper.get_raster_extent(vhm_10m)
        meta_data = get_raster_metadata(vhm_10m)
        extent = "{0},{1},{2},{3} [EPSG:{4}]".format(meta_data["extent"][0],meta_data["extent"][2],meta_data["extent"][1],meta_data["extent"][3],meta_data["epsg"]) 

        param = {'INPUT':mg_input,
        'SOURCE_CRS':None,'TARGET_CRS':None,'RESAMPLING':0,'NODATA':None,'TARGET_RESOLUTION':10,'OPTIONS':'',
        'DATA_TYPE':0,'TARGET_EXTENT':extent,'TARGET_EXTENT_CRS':None,'MULTITHREADING':False,
        'EXTRA':'-co COMPRESS=LZW -co BIGTIFF=YES','OUTPUT':tmp_mg_aligned}
        processing.run("gdal:warpreproject", param)
        #os.system("gdalwarp -tr 10 10 -te {0} {1} {2} {3}".format(xmin, ymin, xmax, ymax) + " " + mg_input + " " + tmp_mg_aligned)

        if reclassify_mg_values:
            feedback.pushInfo("{0}; {1}; {2}; {3}; {4}; {5};".format(tmp_mg_aligned, mg_output, min_lh, max_lh, min_nh, max_nh))
            feedback.pushInfo("reclassify values to coniferous proportion (0-100)...")
            PreProcessingHelper.reclassify_mixture(tmp_mg_aligned, mg_output, min_lh, max_lh, min_nh, max_nh)
        else:
            copy_raster_tiff(tmp_mg_aligned,mg_output)

        if del_tmp:
            feedback.pushInfo("clean up...")
            if os.path.exists(tmp_mg_aligned):
                os.remove(tmp_mg_aligned)

        feedback.pushInfo("====================================================================")
        feedback.pushInfo("FINISHED")
        feedback.pushInfo("TOTAL PROCESSING TIME: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time))))
        feedback.pushInfo("====================================================================")

        return {self.OUTPUT: working_root}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk prepare MG'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TBkPrepareMgAlgorithm()
