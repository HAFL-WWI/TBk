# -*- coding: utf-8 -*-
# *************************************************************************** #
# Prepare VHM raster and MG as input for TBk.
#
# (C) Hannes Horneber (BFH-HAFL)
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

import os
from shutil import copyfile
import time
from datetime import datetime, timedelta

import glob

from osgeo import gdal
from osgeo import gdal_array
# from osgeo.gdalnumeric import *


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
                       QgsVectorLayer,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransformContext,
                       QgsApplication,
                       QgsRasterLayer)
from qgis.analysis import (
    QgsRasterCalculator,
    QgsRasterCalculatorEntry)
import processing

from tbk_qgis.tbk.utility.tbk_utilities import *

from .pre_processing_helper import PreProcessingHelper


class TBkPrepareAlgorithm(QgsProcessingAlgorithm):
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

    # --- Parameters (Class) ---

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    # Directory containing the input files
    OUTPUT_ROOT = "output_root"

    OUTPUT = "OUTPUT"

    # input
    VHM_INPUT = "vhm_input"
    MG_INPUT = "mg_input"
    MASK = "mask"

    # output
    VHM_DETAIL = "vhm_detail"
    VHM_10M = "vhm_10m"
    VHM_150CM = "vhm_150cm"
    MG_10M = "mg_10m"
    MG_10M_BINARY = "mg_10m_binary"

    # --- Advanced Parameters (Class) ---

    # vhm range
    DEL_TMP = "del_tmp"

    # advanced params
    MASK_VHM = "mask_vhm"
    VHM_RECLASSIFY = "vhm_reclassify"
    VHM_CONVERT_TO_BYTE = "vhm_convert_to_byte"
    VMIN = "vMin"
    VMAX = "vMax"
    VNA = "vNA"

    # advanced params
    MG_RESCALE_FACTOR = "100"
    MG_RECLASSIFY_VALUES = "reclassify_mg_values"
    MIN_LH = "min_lh"
    MAX_LH = "max_lh"
    MIN_NH = "min_nh"
    MAX_NH = "max_nh"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # --- Parameters (Tool UI) ---

        # input
        self.addParameter(QgsProcessingParameterRasterLayer(self.VHM_INPUT,
                                                            self.tr("Detailed input VHM (.tif)")))
        self.addParameter(QgsProcessingParameterRasterLayer(self.MG_INPUT,
                                                            self.tr("Forest mixture degree 10m input (.tif)")))
        self.addParameter(QgsProcessingParameterFeatureSource(self.MASK,
                                                              self.tr("Polygon mask to clip final result"),
                                                              [QgsProcessing.TypeVectorPolygon]))

        # Folder for algo output
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_ROOT, self.tr('Output folder')))

        ## output
        parameter = QgsProcessingParameterString(self.VHM_DETAIL,
                                                 self.tr("VHM detail output name (.tif)"),
                                                 defaultValue="VHM_detail.tif")
        self.addParameter(parameter)

        parameter = QgsProcessingParameterString(self.VHM_10M,
                                                 self.tr("VHM 10m output name (.tif)"),
                                                 defaultValue="VHM_10m.tif")
        self.addParameter(parameter)

        parameter = QgsProcessingParameterString(self.VHM_150CM,
                                                 self.tr("VHM 150cm output name (.tif)"),
                                                 defaultValue="VHM_150cm.tif")
        self.addParameter(parameter)

        parameter = QgsProcessingParameterString(self.MG_10M,
                                                 self.tr("Mixing degree 10m  output name (.tif)"),
                                                 defaultValue="MG_10m.tif")
        self.addParameter(parameter)

        parameter = QgsProcessingParameterString(self.MG_10M_BINARY,
                                                 self.tr("Binary Mixing degree 10m output name (.tif) (optional)"),
                                                 defaultValue="MG_10m_binary.tif")
        self.addParameter(parameter)

        # --- Advanced Parameters (Tool UI) ---

        parameter = QgsProcessingParameterBoolean(self.DEL_TMP,
                                                  self.tr("Delete temporary files"),
                                                  defaultValue=True)
        self.addAdvancedParameter(parameter)

        # advanced params (VHM)
        parameter = QgsProcessingParameterBoolean(self.MASK_VHM,
                                                  self.tr("Crop VHM to mask"),
                                                  defaultValue=True)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.VHM_CONVERT_TO_BYTE,
                                                  self.tr("Convert VHM to BYTE datatype " +
                                                          "(will do nothing if already BYTE)"),
                                                  defaultValue=True)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.VHM_RECLASSIFY,
                                                  self.tr("Reclassify VHM to min/max/NA values"),
                                                  defaultValue=False)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.VMIN, self.tr("VHM min value"),
                                                 type=QgsProcessingParameterNumber.Double,
                                                 defaultValue=0)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.VMAX, self.tr("VHM max value"),
                                                 type=QgsProcessingParameterNumber.Double,
                                                 defaultValue=60)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.VNA, self.tr("VHM NA value"),
                                                 type=QgsProcessingParameterNumber.Integer,
                                                 defaultValue=255)
        self.addAdvancedParameter(parameter)

        # advanced params (WMG reclassify values)
        parameter = QgsProcessingParameterNumber(self.MG_RESCALE_FACTOR,
                                                 self.tr("Rescale MG Values (set to 1 to do nothing)." +
                                                         "\nDefault (100) is optimized for WSL layer with " +
                                                         "values 0 - 10'000"),
                                                 defaultValue=100.0)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.MG_RECLASSIFY_VALUES,
                                                  self.tr("Create Binary MG Layer (reclassify to 0 and 100) " +
                                                          "for simplfied stand delineation." +
                                                          "\n (applied to rescaled values if rescale factor is not 1)."),
                                                  defaultValue=True)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_LH, self.tr("Minimum Decidious (Laubholz) value"),
                                                 type=QgsProcessingParameterNumber.Integer,
                                                 defaultValue=1)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MAX_LH, self.tr("Maximum Decidious (Laubholz) value"),
                                                 type=QgsProcessingParameterNumber.Integer,
                                                 defaultValue=50)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_NH, self.tr("Minimum Coniferous (Nadelholz) value"),
                                                 type=QgsProcessingParameterNumber.Integer,
                                                 defaultValue=50)
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MAX_NH, self.tr("Maximum Coniferous (Nadelholz) value"),
                                                 type=QgsProcessingParameterNumber.Integer,
                                                 defaultValue=100)
        self.addAdvancedParameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # --- Init Parameters
        settings_path = QgsApplication.qgisSettingsDirPath()
        feedback.pushInfo(settings_path)

        del_tmp = self.parameterAsBool(parameters, self.DEL_TMP, context)

        # advanced params
        # vhm range
        mask_vhm = self.parameterAsBool(parameters, self.MASK_VHM, context)
        vhm_convert_to_byte = self.parameterAsBool(parameters, self.VHM_CONVERT_TO_BYTE, context)
        vhm_reclassify = self.parameterAsBool(parameters, self.VHM_RECLASSIFY, context)
        vMin = self.parameterAsDouble(parameters, self.VMIN, context)
        vMax = self.parameterAsDouble(parameters, self.VMAX, context)
        vNA = self.parameterAsInt(parameters, self.VNA, context)
        # rasterize_mask = self.parameterAsBool(parameters, self.RASTERIZE_MASK, context)

        # advanced params mg reclassify values
        mg_rescale_factor = self.parameterAsDouble(parameters, self.MG_RESCALE_FACTOR, context)
        mg_reclassify_values = self.parameterAsBool(parameters, self.MG_RECLASSIFY_VALUES, context)

        min_lh = self.parameterAsInt(parameters, self.MIN_LH, context)
        max_lh = self.parameterAsInt(parameters, self.MAX_LH, context)
        min_nh = self.parameterAsInt(parameters, self.MIN_NH, context)
        max_nh = self.parameterAsInt(parameters, self.MAX_NH, context)

        # input
        vhm_input = str(self.parameterAsRasterLayer(parameters, self.VHM_INPUT, context).source())
        if not os.path.splitext(vhm_input)[1].lower() in (".tif", ".tiff"):
            raise QgsProcessingException("vhm_input must be a TIFF file")

        mg_input = str(self.parameterAsRasterLayer(parameters, self.MG_INPUT, context).source())
        if not os.path.splitext(mg_input)[1].lower() in (".tif", ".tiff"):
            raise QgsProcessingException("mg_input must be TIFF file")

        mask = str(self.parameterAsVectorLayer(parameters, self.MASK, context).source())

        # TODO check geometry validity

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

        mg_10m = str(self.parameterAsString(parameters, self.MG_10M, context))
        if (not mg_10m) or mg_10m == "":
            raise QgsProcessingException("no MG output file name specified")
        if not os.path.splitext(mg_10m)[1].lower() in (".tif", ".tiff"):
            raise QgsProcessingException("mg_10m must be TIFF file")

        mg_10m_binary = str(self.parameterAsString(parameters, self.MG_10M_BINARY, context))
        if mg_reclassify_values:
            if (not mg_10m_binary) or mg_10m_binary == "":
                raise QgsProcessingException("no MG binary output file name specified")
            if not os.path.splitext(mg_10m_binary)[1].lower() in (".tif", ".tiff"):
                raise QgsProcessingException("mg_10m_binary must be TIFF file")

        ensure_dir(output_root)
        working_root = output_root

        vhm_detail = os.path.join(output_root, vhm_detail)
        vhm_10m = os.path.join(output_root, vhm_10m)
        vhm_150cm = os.path.join(output_root, vhm_150cm)
        mg_10m = os.path.join(output_root, mg_10m)
        mg_10m_binary = os.path.join(output_root, mg_10m_binary)

        # tmp files
        tmp_vhm_byte = os.path.join(output_root, "vhm_byte.tif")
        tmp_vhm_cropped = os.path.join(output_root, "vhm_cropped.tif")
        tmp_vhm_mask = os.path.join(output_root, "vhm_mask.tif")
        tmp_mg_aligned = os.path.join(output_root, "mg_10m_aligned.tif")

        # remove existing rasters
        self.deleteRasterIfExists(vhm_detail)
        self.deleteRasterIfExists(vhm_10m)
        self.deleteRasterIfExists(vhm_150cm)
        self.deleteRasterIfExists(mg_10m)
        self.deleteRasterIfExists(mg_10m_binary)
        # remove existing tmp rasters
        self.deleteRasterIfExists(tmp_vhm_byte)
        self.deleteRasterIfExists(tmp_vhm_cropped)
        self.deleteRasterIfExists(tmp_vhm_mask)
        self.deleteRasterIfExists(tmp_mg_aligned)

        # --- Process VHM
        start_time = time.time()

        if vhm_convert_to_byte:
            feedback.pushInfo("Checking vhm input raster...")
            vhm_input_raster = gdal.Open(vhm_input)
            feedback.pushInfo(f"DataType Code: {vhm_input_raster.GetRasterBand(1).DataType}  "
                              f"(1: Byte, 3: Int16, 6: Float32)")

            if vhm_input_raster.GetRasterBand(1).DataType == 1:
                feedback.pushInfo("vhm raster is already byte, not converting...")
            else:
                feedback.pushInfo("convert vhm raster to byte...")
                param = {'INPUT': vhm_input, 'SOURCE_CRS': None, 'TARGET_CRS': None, 'RESAMPLING': 0,
                         'NODATA': vNA, 'TARGET_RESOLUTION': None, 'OPTIONS': '', 'DATA_TYPE': 1,
                         'TARGET_EXTENT': None, 'TARGET_EXTENT_CRS': None, 'MULTITHREADING': True,
                         'EXTRA': '-co COMPRESS=LZW -co BIGTIFF=YES', 'OUTPUT': tmp_vhm_byte}
                algoOutput = processing.run("gdal:warpreproject", param)
                vhm_input = tmp_vhm_byte

        if mask_vhm:
            feedback.pushInfo("mask vhm...")
            param = {'INPUT': vhm_input, 'MASK': mask, 'SOURCE_CRS': None, 'TARGET_CRS': None, 'NODATA': vNA,
                     'ALPHA_BAND': False, 'CROP_TO_CUTLINE': True, 'KEEP_RESOLUTION': False,
                     'SET_RESOLUTION': False, 'X_RESOLUTION': 0, 'Y_RESOLUTION': 0, 'MULTITHREADING': False,
                     'OPTIONS': '', 'DATA_TYPE': 0,
                     'EXTRA': '-multi -wm 5000 -co COMPRESS=LZW -co TILED=YES -co BIGTIFF=YES  -wo \"CUTLINE_ALL_TOUCHED=TRUE\"',
                     'OUTPUT': tmp_vhm_cropped}
            processing.run("gdal:cliprasterbymasklayer", param)

            # TODO this does nothing if no masking is necessary, resulting in no output generated
            # and the following command failing
            # solution: check for output, otherwise WARNING and proceed without cropping

            vhm_input = tmp_vhm_cropped

        if vhm_reclassify:
            feedback.pushInfo("reclassify vhm outliers...")
            if not os.path.exists(os.path.dirname(vhm_detail)):
                os.makedirs(os.path.dirname(vhm_detail))
            PreProcessingHelper.reclassify_min_max(vhm_input, vhm_detail, min_value=vMin, max_value=vMax)
        else:
            feedback.pushInfo("copy as vhm detail...")
            copy_raster_tiff(vhm_input, vhm_detail)

        feedback.pushInfo("aggregate vhm to 10m...")
        if not os.path.exists(os.path.dirname(vhm_10m)):
            os.makedirs(os.path.dirname(vhm_10m))
        param = {'INPUT': vhm_detail, 'SOURCE_CRS': None, 'TARGET_CRS': None,
                 'RESAMPLING': 7, 'NODATA': None, 'TARGET_RESOLUTION': 10, 'OPTIONS': '', 'DATA_TYPE': 0,
                 'TARGET_EXTENT': None,
                 'TARGET_EXTENT_CRS': None, 'MULTITHREADING': False, 'EXTRA': '-co COMPRESS=LZW ', 'OUTPUT': vhm_10m}
        algoOutput = processing.run("gdal:warpreproject", param)
        # os.system("gdalwarp -tr 10 10 -r max -co COMPRESS=LZW " + vhm_detail + " " + vhm_10m)

        feedback.pushInfo("aggregate vhm to 150cm...")
        if not os.path.exists(os.path.dirname(vhm_150cm)):
            os.makedirs(os.path.dirname(vhm_150cm))
        param = {'INPUT': vhm_detail, 'SOURCE_CRS': None, 'TARGET_CRS': None,
                 'RESAMPLING': 7, 'NODATA': None, 'TARGET_RESOLUTION': 1.5, 'OPTIONS': '', 'DATA_TYPE': 0,
                 'TARGET_EXTENT': None,
                 'TARGET_EXTENT_CRS': None, 'MULTITHREADING': False, 'EXTRA': '-co COMPRESS=LZW ', 'OUTPUT': vhm_150cm}
        algoOutput = processing.run("gdal:warpreproject", param)
        # os.system("gdalwarp -tr 1.5 1.5 -r max -co COMPRESS=LZW " + vhm_detail + " " + vhm_150cm)

        feedback.pushInfo("====================================================================")
        feedback.pushInfo(
            "Finished VHM processing after: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time))))
        feedback.pushInfo("Continue with MG processing")
        feedback.pushInfo("====================================================================")

        # --- Process MG

        feedback.pushInfo("match VHM<>MG extent, align pixels...")
        xmin, ymin, xmax, ymax = PreProcessingHelper.get_raster_extent(vhm_10m)
        meta_data = get_raster_metadata(vhm_10m)
        extent = "{0},{1},{2},{3} [EPSG:{4}]".format(meta_data["extent"][0], meta_data["extent"][2],
                                                     meta_data["extent"][1], meta_data["extent"][3], meta_data["epsg"])
        param = {'INPUT': mg_input,
                 'SOURCE_CRS': None, 'TARGET_CRS': None, 'RESAMPLING': 0, 'NODATA': None, 'TARGET_RESOLUTION': 10,
                 'OPTIONS': '',
                 'DATA_TYPE': 0, 'TARGET_EXTENT': extent, 'TARGET_EXTENT_CRS': None, 'MULTITHREADING': False,
                 'EXTRA': '-co COMPRESS=LZW -co BIGTIFF=YES', 'OUTPUT': tmp_mg_aligned}
        processing.run("gdal:warpreproject", param)

        if mg_rescale_factor != 1.0:
            feedback.pushInfo(f"rescale MG values by factor {mg_rescale_factor}...")
            param = {
                'INPUT_A': tmp_mg_aligned,
                'BAND_A': 1, 'INPUT_B': None, 'BAND_B': None, 'INPUT_C': None, 'BAND_C': None, 'INPUT_D': None,
                'BAND_D': None, 'INPUT_E': None, 'BAND_E': None, 'INPUT_F': None, 'BAND_F': None,
                'FORMULA': 'A/' + str(mg_rescale_factor),
                'NO_DATA': None, 'PROJWIN': None, 'RTYPE': 0, 'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                'EXTRA': '',
                'OUTPUT': mg_10m}
            processing.run("gdal:rastercalculator", param)
        else:
            feedback.pushInfo(f"not rescaling MG values (factor {mg_rescale_factor}...)")
            copy_raster_tiff(tmp_mg_aligned, mg_10m)

        if mg_reclassify_values:
            feedback.pushInfo(
                "{0}; {1}; {2}; {3}; {4}; {5};".format(mg_10m, mg_10m_binary, min_lh, max_lh, min_nh, max_nh))
            feedback.pushInfo("reclassify values to coniferous proportion (0-100)...")
            PreProcessingHelper.reclassify_mixture(mg_10m, mg_10m_binary, min_lh, max_lh, min_nh, max_nh)

        # delete all temporary files, including .tif.aux.xml files that are occasionally
        if del_tmp:
            feedback.pushInfo("clean up...")
            if os.path.exists(tmp_vhm_byte):
                os.remove(tmp_vhm_byte)
            if os.path.exists(tmp_vhm_byte + ".aux.xml"):
                os.remove(tmp_vhm_byte + ".aux.xml")

            if os.path.exists(tmp_vhm_cropped):
                os.remove(tmp_vhm_cropped)
                for filename in glob.glob(os.path.splitext(tmp_vhm_cropped)[0] + "*"):
                    os.remove(filename)
            if os.path.exists(tmp_vhm_mask):
                os.remove(tmp_vhm_mask)

            if os.path.exists(tmp_mg_aligned):
                os.remove(tmp_mg_aligned)
            if os.path.exists(tmp_mg_aligned + ".aux.xml"):
                os.remove(tmp_mg_aligned + ".aux.xml")

            if os.path.exists(vhm_detail + ".aux.xml"):
                os.remove(vhm_detail + ".aux.xml")

        # finished
        feedback.pushInfo("====================================================================")
        feedback.pushInfo("FINISHED")
        feedback.pushInfo("TOTAL PROCESSING TIME: %s (h:min:sec)" %
                          str(timedelta(seconds=(time.time() - start_time))))
        feedback.pushInfo("====================================================================")

        return {self.OUTPUT: working_root}

    # --- Algorithm ID, Name

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk prepare VHM and MG'

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
        return 'Y Testing and Legacy'

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'testing'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TBkPrepareAlgorithm()
