# -*- coding: utf-8 -*-
# *************************************************************************** #
# Prepare VHM raster as input for TBk.
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

import glob

from osgeo.gdalnumeric import *

from qgis.PyQt.QtCore import QCoreApplication
from qgis.analysis import (
    QgsRasterCalculator,
    QgsRasterCalculatorEntry)
import processing

from tbk_qgis.tbk.general.tbk_utilities import *

from .pre_processing_helper import PreProcessingHelper
from tbk_qgis.tbk.general.persistence_utility import (read_dict_from_toml_file,
                                         write_dict_to_toml_file)
from .tbk_qgis_processing_algorithm_toolsY import TBkProcessingAlgorithmToolY


class TBkPrepareVhmAlgorithm(TBkProcessingAlgorithmToolY):
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

    def deleteRasterIfExists(self, raster_path):
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
    VHM_INPUT = "vhm_input"
    MASK = "mask"

    # output
    VHM_DETAIL = "vhm_detail"
    VHM_10M = "vhm_10m"
    VHM_150CM = "vhm_150cm"

    # vhm range
    VMIN = "vMin"
    VMAX = "vMax"

    # advanced params
    VNA = "vNA"
    DEL_TMP = "del_tmp"
    CONVERT_TO_BYTE = "convert_to_byte"
    CROP_VHM = "crop_vhm"
    RASTERIZE_MASK = "rasterize_mask"

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
        self.addParameter(QgsProcessingParameterRasterLayer(self.VHM_INPUT, self.tr("Detailed input VHM (.tif)")))
        self.addParameter(
            QgsProcessingParameterFeatureSource(self.MASK, self.tr("Mask shapefile to clip final result (.shp)"),
                                                [QgsProcessing.TypeVectorPolygon]))

        # Folder for algo output
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_ROOT, self.tr('Output folder')))

        ## output
        parameter = QgsProcessingParameterString(self.VHM_DETAIL, self.tr("VHM detail output name (.tif)"),
                                                 defaultValue="vhm_detail.tif")
        self.addParameter(parameter)
        # todo: names are confusing since VHM_10M and VHM_150CM refers to the inputs in the main algorithm
        parameter = QgsProcessingParameterString(self.VHM_10M, self.tr("VHM 10m output name (.tif)"),
                                                 defaultValue="vhm_10m.tif")
        self.addParameter(parameter)

        parameter = QgsProcessingParameterString(self.VHM_150CM, self.tr("VHM 150cm output name (.tif)"),
                                                 defaultValue="vhm_150cm.tif")
        self.addParameter(parameter)

        ## vhm range
        parameter = QgsProcessingParameterNumber(self.VMIN, self.tr("VHM min value"),
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0)
        self.addParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.VMAX, self.tr("VHM max value"),
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=60)
        self.addParameter(parameter)

        # advanced params
        parameter = QgsProcessingParameterNumber(self.VNA, self.tr("VHM NA value"),
                                                 type=QgsProcessingParameterNumber.Integer, defaultValue=255)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.DEL_TMP, self.tr("Delete temporary files"), defaultValue=True)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.CONVERT_TO_BYTE, self.tr("Convert VHM to BYTE datatype"),
                                                  defaultValue=True)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.CROP_VHM, self.tr("Crop VHM to mask"), defaultValue=True)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.RASTERIZE_MASK, self.tr("Rasterize mask"), defaultValue=False)
        self.addAdvancedParameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        print(f'parameters: {parameters}')
        settings_path = QgsApplication.qgisSettingsDirPath()
        feedback.pushInfo(settings_path)

        tbk_tool_path = os.path.join(settings_path, "python/plugins/tbk_qgis")

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

        # input
        vhm_input = str(self.parameterAsRasterLayer(parameters, self.VHM_INPUT, context).source())
        if not os.path.splitext(vhm_input)[1].lower() in (".tif", ".tiff"):
            raise QgsProcessingException("vhm_input must be a TIFF file")

        mask = str(self.parameterAsVectorLayer(parameters, self.MASK, context).source())
        if "|layername=" in mask.lower():
            mask = mask.split("|")[0]
        # todo: allow gpkg format?
        if not os.path.splitext(mask)[1].lower() in (".shp"):
            raise QgsProcessingException("Mask must be a Shape file")

        # Folder for algo output
        output_root = self.parameterAsString(parameters, self.OUTPUT_ROOT, context)

        # output
        vhm_detail = str(self.parameterAsString(parameters, self.VHM_DETAIL, context))
        if (not vhm_detail) or vhm_detail == "":
            raise QgsProcessingException("no VHM detail file name specified")
        if not os.path.splitext(vhm_detail)[1].lower() in (".tif", ".tiff"):
            raise QgsProcessingException("vhm_detail must be a TIFF file name")

        vhm_10m = str(self.parameterAsString(parameters, self.VHM_10M, context))
        if (not vhm_10m) or vhm_10m == "":
            raise QgsProcessingException("no VHM 10m file name specified")
        if not os.path.splitext(vhm_10m)[1].lower() in (".tif", ".tiff"):
            raise QgsProcessingException("vhm_10m must be a TIFF file name")

        vhm_150cm = str(self.parameterAsString(parameters, self.VHM_150CM, context))
        if (not vhm_150cm) or vhm_150cm == "":
            raise QgsProcessingException("no VHM 150cm file name specified")
        if not os.path.splitext(vhm_150cm)[1].lower() in (".tif", ".tiff"):
            raise QgsProcessingException("vhm_150cm must be a TIFF file name")

        # vhm range
        vMin = self.parameterAsDouble(parameters, self.VMIN, context)
        vMax = self.parameterAsDouble(parameters, self.VMAX, context)

        # advanced params
        vNA = self.parameterAsInt(parameters, self.VNA, context)
        del_tmp = self.parameterAsBool(parameters, self.DEL_TMP, context)
        convert_to_byte = self.parameterAsBool(parameters, self.CONVERT_TO_BYTE, context)
        crop_vhm = self.parameterAsBool(parameters, self.CROP_VHM, context)
        rasterize_mask = self.parameterAsBool(parameters, self.RASTERIZE_MASK, context)

        ensure_dir(output_root)
        working_root = output_root

        vhm_detail = os.path.join(output_root, vhm_detail)
        vhm_10m = os.path.join(output_root, vhm_10m)
        vhm_150cm = os.path.join(output_root, vhm_150cm)

        # tmp files
        tmp_byte = os.path.join(output_root, "vhm_byte.tif")
        tmp_cropped = os.path.join(output_root, "vhm_cropped.tif")
        tmp_mask = os.path.join(output_root, "vhm_mask.tif")

        # remove existing rasters
        self.deleteRasterIfExists(vhm_detail)
        self.deleteRasterIfExists(vhm_10m)
        self.deleteRasterIfExists(vhm_150cm)
        self.deleteRasterIfExists(tmp_byte)
        self.deleteRasterIfExists(tmp_cropped)
        self.deleteRasterIfExists(tmp_mask)

        # Store the input parameters in a file
        params_with_sources = self.asMap(parameters, context)['inputs']
        try:
            write_dict_to_toml_file(params_with_sources, output_root)
        except Exception as error:
            feedback.pushWarning('The TOML file was not written in the output folder because an error occurred')
            feedback.pushWarning(f'Error: {error}')

        start_time = time.time()

        # get input raster resolution
        xRes, yRes = PreProcessingHelper.get_raster_resolution(vhm_input)

        if convert_to_byte:
            feedback.pushInfo("covert raster to byte...")
            param = {'INPUT': vhm_input, 'SOURCE_CRS': None, 'TARGET_CRS': None, 'RESAMPLING': 0,
                     'NODATA': vNA, 'TARGET_RESOLUTION': None, 'OPTIONS': '', 'DATA_TYPE': 1,
                     'TARGET_EXTENT': None, 'TARGET_EXTENT_CRS': None, 'MULTITHREADING': True,
                     'EXTRA': '-co COMPRESS=LZW -co BIGTIFF=YES', 'OUTPUT': tmp_byte}
            algoOutput = processing.run("gdal:warpreproject", param)
            # os.system("gdalwarp -of GTiff -ot Byte -dstnodata " + str(vNA) + " -co COMPRESS=LZW -co BIGTIFF=YES " + vhm_input + " " + tmp_byte)
            vhm_input = tmp_byte

        if crop_vhm:
            feedback.pushInfo("clip vhm...")
            if rasterize_mask:

                vhm_lyr = QgsRasterLayer(vhm_input, 'vhm')
                if not vhm_lyr.isValid():
                    print('VHM Layer failed to load!')
                raster_size = vhm_lyr.rasterUnitsPerPixelX()

                feedback.pushInfo("rasterize mask...")
                mask_layer = QgsVectorLayer(mask, "union_tmp", "ogr")
                mask_extent = mask_layer.extent()
                extent = "{0},{1},{2},{3} [EPSG:{4}]".format(mask_extent.xMinimum(), mask_extent.xMaximum(),
                                                             mask_extent.yMinimum(), mask_extent.yMaximum(),
                                                             mask_layer.sourceCrs().srsid())

                param = {'INPUT': mask, 'FIELD': None, 'BURN': 1, 'UNITS': raster_size, 'WIDTH': xRes, 'HEIGHT': yRes,
                         'EXTENT': extent, 'NODATA': vNA, 'OPTIONS': '', 'DATA_TYPE': 0, 'INIT': vNA, 'INVERT': False,
                         'EXTRA': '-co COMPRESS=LZW ', 'OUTPUT': tmp_mask}
                algoOutput = processing.run("gdal:rasterize", param)
                # os.system("gdal_rasterize -burn 1 -at -tr " + str(xRes) + " " + str(yRes) + " -ot Byte -init "
                #        + str(vNA) + " -a_nodata " + str(vNA) + " -co COMPRESS=LZW " + mask + " " + tmp_mask)

                feedback.pushInfo("mask vhm...")
                # param = {'raster':tmp_mask,'input':vhm_input,'maskcats':'*','-i':False,
                # 'output':tmp_cropped,'GRASS_REGION_PARAMETER':None,'GRASS_REGION_CELLSIZE_PARAMETER':0,
                # 'GRASS_RASTER_FORMAT_OPT':'','GRASS_RASTER_FORMAT_META':''}
                # algoOutput = processing.run("grass7:r.mask.rast", param)

                mask_lyr = QgsRasterLayer(tmp_mask, 'mask')
                if not mask_lyr.isValid():
                    print('Mask Layer failed to load!')

                entries = []
                vhm_entry = QgsRasterCalculatorEntry()
                vhm_entry.raster = vhm_lyr
                vhm_entry.ref = vhm_lyr.name() + "@1"
                vhm_entry.bandNumber = 1
                entries.append(vhm_entry)
                mask_entry = QgsRasterCalculatorEntry()
                mask_entry.raster = mask_lyr
                mask_entry.ref = mask_lyr.name() + "@1"
                mask_entry.bandNumber = 1
                entries.append(mask_entry)

                context = QgsCoordinateTransformContext()
                calc = QgsRasterCalculator(vhm_lyr.name() + '@1 * ' + mask_lyr.name() + '@1', tmp_cropped, "GTiff",
                                           vhm_lyr.extent(), vhm_lyr.width(), vhm_lyr.height(), entries, context)

                calc.processCalculation()
                print(calc.lastError())

                del vhm_lyr
                del mask_lyr

                param = {'INPUT': tmp_cropped,
                         'CRS': QgsCoordinateReferenceSystem('EPSG:{0}'.format(mask_layer.sourceCrs().srsid()))}
                algoOutput = processing.run("gdal:assignprojection", param)

                ## TODO: find gdal / rasterio solution (not found yet)
                # os.system("\"" + arcgis_python + "\" " + tbk_tool_path + "\\pre_processing\\extract_by_mask.py" + " " + vhm_input + " " + tmp_mask + " " + tmp_cropped)

                del mask_layer
            else:
                param = {'INPUT': vhm_input, 'MASK': mask, 'SOURCE_CRS': None, 'TARGET_CRS': None, 'NODATA': vNA,
                         'ALPHA_BAND': False, 'CROP_TO_CUTLINE': True, 'KEEP_RESOLUTION': False,
                         'SET_RESOLUTION': False, 'X_RESOLUTION': 0, 'Y_RESOLUTION': 0, 'MULTITHREADING': False,
                         'OPTIONS': '', 'DATA_TYPE': 0,
                         'EXTRA': '-multi -wm 5000 -co COMPRESS=LZW -co TILED=YES -co BIGTIFF=YES  -wo \"CUTLINE_ALL_TOUCHED=TRUE\"',
                         'OUTPUT': tmp_cropped}
                processing.run("gdal:cliprasterbymasklayer", param)
                # os.system("gdalwarp -of GTiff -cutline " + mask + " -crop_to_cutline -wo \"CUTLINE_ALL_TOUCHED=TRUE\"" +
                #        " -tr " + str(xRes) + " " + str(yRes) + " -dstnodata " + str(vNA) +
                #        " -multi -wm 5000 -co COMPRESS=LZW -co TILED=YES -co BIGTIFF=YES " +  # large raster processing
                #        vhm_input + " " + tmp_cropped)
            vhm_input = tmp_cropped

        feedback.pushInfo("reclassify outliers...")
        if not os.path.exists(os.path.dirname(vhm_detail)):
            os.makedirs(os.path.dirname(vhm_detail))
        PreProcessingHelper.reclassify_min_max(vhm_input, vhm_detail, min_value=vMin, max_value=vMax)

        feedback.pushInfo("aggregate to 10m...")
        if not os.path.exists(os.path.dirname(vhm_10m)):
            os.makedirs(os.path.dirname(vhm_10m))
        param = {'INPUT': vhm_detail, 'SOURCE_CRS': None, 'TARGET_CRS': None,
                 'RESAMPLING': 7, 'NODATA': None, 'TARGET_RESOLUTION': 10, 'OPTIONS': '', 'DATA_TYPE': 0,
                 'TARGET_EXTENT': None,
                 'TARGET_EXTENT_CRS': None, 'MULTITHREADING': False, 'EXTRA': '-co COMPRESS=LZW ', 'OUTPUT': vhm_10m}
        algoOutput = processing.run("gdal:warpreproject", param)
        # os.system("gdalwarp -tr 10 10 -r max -co COMPRESS=LZW " + vhm_detail + " " + vhm_10m)

        feedback.pushInfo("aggregate to 150cm...")
        if not os.path.exists(os.path.dirname(vhm_150cm)):
            os.makedirs(os.path.dirname(vhm_150cm))
        param = {'INPUT': vhm_detail, 'SOURCE_CRS': None, 'TARGET_CRS': None,
                 'RESAMPLING': 7, 'NODATA': None, 'TARGET_RESOLUTION': 1.5, 'OPTIONS': '', 'DATA_TYPE': 0,
                 'TARGET_EXTENT': None,
                 'TARGET_EXTENT_CRS': None, 'MULTITHREADING': False, 'EXTRA': '-co COMPRESS=LZW ', 'OUTPUT': vhm_150cm}
        algoOutput = processing.run("gdal:warpreproject", param)
        # os.system("gdalwarp -tr 1.5 1.5 -r max -co COMPRESS=LZW " + vhm_detail + " " + vhm_150cm)

        if del_tmp:
            feedback.pushInfo("clean up...")
            if os.path.exists(tmp_byte):
                os.remove(tmp_byte)
            if os.path.exists(tmp_cropped):
                os.remove(tmp_cropped)
                for filename in glob.glob(os.path.splitext(tmp_cropped)[0] + "*"):
                    os.remove(filename)
            if os.path.exists(tmp_mask):
                os.remove(tmp_mask)

        # finished
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
        return 'TBk prepare VHM'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TBkPrepareVhmAlgorithm()
