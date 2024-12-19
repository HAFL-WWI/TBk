# -*- coding: utf-8 -*-
# *************************************************************************** #
# Prepare VHM raster and / or MG raster as input for TBk.
#
# Authors: Attilio Benini, Hannes Horneber (BFH-HAFL)
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

import os # os is used below, so make sure it's available in any case
import time
from datetime import datetime, timedelta
import glob
import math

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProcessingParameterDefinition,
    QgsVectorLayer,
    QgsApplication,
    QgsProcessingException,
    QgsProcessingParameterEnum
)

import processing

from tbk_qgis.tbk.utility.tbk_utilities import *

from .pre_processing_helper import PreProcessingHelper


class TBkPrepareVhmMgAlgorithm(QgsProcessingAlgorithm):

    def addAdvancedParameter(self, parameter):
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        return self.addParameter(parameter)

    def deleteRasterIfExists (self, raster_path):
        if os.path.exists(raster_path):
            delete_raster(raster_path)

    #--- Parameters (Class) ---

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

    #--- Advanced Parameters (Class) ---

    # advanced params
    ALIGN_METHOD = "align_method"
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

        #--- Parameters (Tool UI) ---

        # input
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.VHM_INPUT,
                self.tr("Detailed input VHM (.tif)")
            )
        )
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.MG_INPUT,
                self.tr("Forest mixture degree input (.tif)"),
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.MASK,
                self.tr("Polygon mask to clip final result"),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # Folder for algo output
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_ROOT,self.tr('Output folder')))

        # --- Advanced Parameters (Tool UI) ---

        ## output
        parameter = QgsProcessingParameterString(
            self.VHM_DETAIL,
            self.tr("VHM detail output name (.tif)"),
            defaultValue = "VHM_detail.tif"
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterString(
            self.VHM_10M,
            self.tr("VHM 10m output name (.tif)"),
            defaultValue = "VHM_10m.tif"
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterString(
            self.VHM_150CM,
            self.tr("VHM 150cm output name (.tif)"),
            defaultValue = "VHM_150cm.tif"
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterString(
            self.MG_10M,
            self.tr("Mixture degree 10m output name (.tif)"),
            defaultValue = "MG_10m.tif"
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterString(
            self.MG_10M_BINARY,
            self.tr("Binary mixture degree 10m output name (.tif) (optional)"),
            defaultValue = "MG_10m_binary.tif"
        )
        self.addAdvancedParameter(parameter)

        # alignment of rasters
        parameter = QgsProcessingParameterEnum(
            self.ALIGN_METHOD,
            self.tr(
                'Method aligning output raster layers (for details s. description)'
                '\n - Align to origin (X,Y) = (0,0)'
                '\n - Align to mixture degree raster'
                '\n - Random / driven by extent of mask'
            ),
            options=[
                'Align to origin (X,Y) = (0,0)',
                'Align to mixture degree raster',
                'Random / driven by extent of mask'
            ],
            defaultValue=0,
            optional=False
            )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(
            self.DEL_TMP,
            self.tr("Delete temporary files"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # advanced params (VHM)
        parameter = QgsProcessingParameterBoolean(
            self.MASK_VHM,
            self.tr("Crop VHM to mask"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(
            self.VHM_CONVERT_TO_BYTE,
            self.tr("Convert VHM to BYTE datatype " + "(will do nothing if already BYTE)"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(
            self.VHM_RECLASSIFY,
            self.tr("Reclassify VHM values < VHM min resp. > VHM max value as NoData."),
            defaultValue=False
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(
            self.VMIN,
            self.tr("VHM min value"),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=0
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(
            self.VMAX,
            self.tr("VHM max value"),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=60
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(
            self.VNA,
            self.tr("VHM NoData value"),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=255
        )
        self.addAdvancedParameter(parameter)

        # advanced params (WMG reclassify values)
        parameter = QgsProcessingParameterNumber(
            self.MG_RESCALE_FACTOR,
            self.tr(
                "Rescale Forest mixture degree values (set to 1 to do nothing)." +
                "\nDefault (100) is optimized for WSL layer with " +
                "values 0 - 10'000"
            ),
            defaultValue=100.0
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterBoolean(
            self.MG_RECLASSIFY_VALUES,
            self.tr(
                "Create Binary mixture degree layer (reclassify to 0 and 100) " +
                "for simplified stand delineation." +
                "\n (applied to rescaled values if rescale factor is not 1)."
            ),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(
            self.MIN_LH,
            self.tr("Minimum Deciduous (Laubholz) value"),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=0
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(
            self.MAX_LH, self.tr("Maximum Deciduous (Laubholz) value"),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=50
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(
            self.MIN_NH,
            self.tr("Minimum Coniferous (Nadelholz) value"),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=50
        )
        self.addAdvancedParameter(parameter)

        parameter = QgsProcessingParameterNumber(
            self.MAX_NH,
            self.tr("Maximum Coniferous (Nadelholz) value"),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=100
        )
        self.addAdvancedParameter(parameter)



    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        #--- Init Parameters

        align_method = self.parameterAsInt(parameters, self.ALIGN_METHOD, context)
        del_tmp = self.parameterAsBool(parameters, self.DEL_TMP, context)

        # advanced params
        # vhm range
        mask_vhm = self.parameterAsBool(parameters, self.MASK_VHM, context)
        vhm_convert_to_byte = self.parameterAsBool(parameters, self.VHM_CONVERT_TO_BYTE, context)
        vhm_reclassify = self.parameterAsBool(parameters, self.VHM_RECLASSIFY, context)
        vMin = self.parameterAsDouble(parameters, self.VMIN, context)
        vMax = self.parameterAsDouble(parameters, self.VMAX, context)
        vNA = self.parameterAsInt(parameters, self.VNA, context)

        # advanced params mg reclassify values
        mg_rescale_factor = self.parameterAsDouble(parameters, self.MG_RESCALE_FACTOR, context)
        mg_reclassify_values = self.parameterAsBool(parameters, self.MG_RECLASSIFY_VALUES, context)

        min_lh = self.parameterAsInt(parameters, self.MIN_LH, context)
        max_lh = self.parameterAsInt(parameters, self.MAX_LH, context)
        min_nh = self.parameterAsInt(parameters, self.MIN_NH, context)
        max_nh = self.parameterAsInt(parameters, self.MAX_NH, context)

        # # input
        vhm_input = str(self.parameterAsRasterLayer(parameters, self.VHM_INPUT, context).source())
        if not os.path.splitext(vhm_input)[1].lower() in (".tif", ".tiff"):
            raise QgsProcessingException("vhm_input must be a TIFF file")

        mg_input_layer = self.parameterAsRasterLayer(parameters, self.MG_INPUT, context)
        mg_input = None
        mg_use = False
        if mg_input_layer:
            mg_input = str(mg_input_layer.source())
            mg_use = True
        if mg_use and mg_input and (not os.path.splitext(mg_input)[1].lower() in (".tif", ".tiff")):
            raise QgsProcessingException("mg_input must be a TIFF file")

        mask = str(self.parameterAsVectorLayer(parameters, self.MASK, context).source())

        # Folder for algo output
        output_root = self.parameterAsString(parameters, self.OUTPUT_ROOT, context)

        # output
        vhm_detail = str(self.parameterAsString(parameters, self.VHM_DETAIL, context))
        if (not vhm_detail) or vhm_detail == "":
            raise QgsProcessingException("no VHM detail file name specified")
        if not os.path.splitext(vhm_detail)[1].lower() in (".tif",".tiff"):
            raise QgsProcessingException("vhm_detail must be a TIFF file name")

        vhm_10m = str(self.parameterAsString(parameters, self.VHM_10M, context))
        if (not vhm_10m) or vhm_10m == "":
            raise QgsProcessingException("no VHM 10m file name specified")
        if not os.path.splitext(vhm_10m)[1].lower() in (".tif",".tiff"):
            raise QgsProcessingException("vhm_10m must be a TIFF file name")

        vhm_150cm = str(self.parameterAsString(parameters, self.VHM_150CM, context))
        if (not vhm_150cm) or vhm_150cm == "":
            raise QgsProcessingException("no VHM 150cm file name specified")
        if not os.path.splitext(vhm_150cm)[1].lower() in (".tif",".tiff"):
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

        vhm_detail = os.path.join(output_root,vhm_detail)
        vhm_10m = os.path.join(output_root,vhm_10m)
        vhm_150cm = os.path.join(output_root,vhm_150cm)
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

        #--- Process VHM
        start_time = time.time()

        def get_raster_extent(raster):
            meta_data = get_raster_metadata(raster)
            ext = "{0},{1},{2},{3} [EPSG:{4}]".format(
                meta_data["extent"][0],
                meta_data["extent"][2],
                meta_data["extent"][1],
                meta_data["extent"][3],
                meta_data["epsg"]
            )
            return(ext)

        def get_aligned_extent(vector_layer, res):
            v = QgsVectorLayer(vector_layer)
            ext = v.extent()
            xmin = math.floor(ext.xMinimum() / res) * res
            xmax = math.ceil(ext.xMaximum() / res) * res
            ymin = math.floor(ext.yMinimum() / res) * res
            ymax = math.ceil(ext.yMaximum() / res) * res
            # epsg = v.crs().authid()[5:]  # remove suffix 'EPSG:', but is the suffix always == 'EPSG:'?
            epsg = v.crs().authid()
            # ext = "{0},{1},{2},{3} [EPSG:{4}]".format(xmin, xmax, ymin, ymax, epsg)  # using epsg without suffix 'EPSG:'
            ext = "{0},{1},{2},{3} [{4}]".format(xmin, xmax, ymin, ymax, epsg)
            return(ext)

        # print("input of align_method: " + str( align_method))
        # print("mg_use: " + str(mg_use))

        # non-aligned extents used if align_method == 2 (raster alignment driven by extent of mask / random)
        extent_10m = None
        extent_150cm = None

        # if align_method == 1 (to pixel of mg_input), but mg is not among inputs ...
        if align_method == 1 and mg_use == False:
            feedback.pushInfo("Switch align_method from 1 to 0, because mg_imput is not specified...")
            align_method = 0  # ... align to origin (X,Y) = (0,0)

        # if align_method == 1 (to pixel of mg_input) and mg is among inputs ...
        if align_method == 1 and mg_use:
            param = {'INPUT': mg_input, 'BAND': None}
            mg_input_properties = processing.run("native:rasterlayerproperties", param)
            # ... but mg_input resolution != 10m x 10m ...
            if mg_input_properties['PIXEL_HEIGHT'] != 10.0 or mg_input_properties['PIXEL_WIDTH'] != 10.0:
                feedback.pushInfo("Switch align_method from 1 to 0, because mg_imput resolution is not 10m x 10m...")
                align_method = 0  # ... align to origin (X,Y) = (0,0)

        # print("reset of align_method: " + str(align_method))

        # if raster 10m x 10m are aligned to origin (X,Y) = (0,0) ...
        if align_method == 0:
            # ... get corresponding extent
            feedback.pushInfo("Define extent of VHM 10m and optionally MG 10m as aligned to origin (X,Y) = (0,0)...")
            extent_10m = get_aligned_extent(mask, res=10)

        # if raster 10m x 10m are aligned to mixture degree input ...
        if align_method == 1:
            # ... get overlapping part of mixture degree and ...
            feedback.pushInfo("clip MG by mask extent...")
            param = {
                'INPUT': mg_input,
                'PROJWIN': QgsVectorLayer(mask).extent(),
                'OVERCRS': False,
                'NODATA': None,
                'OPTIONS': '',
                'DATA_TYPE': 0,
                'EXTRA': '',
                'OUTPUT': tmp_mg_aligned
            }
            processing.run("gdal:cliprasterbyextent", param)
            # ... get corresponding extent
            feedback.pushInfo("Defined extent of VHM 10m and MG 10m as aligned to mg_input...")
            extent_10m = get_raster_extent(tmp_mg_aligned)

        # if raster alignment is not radom ...
        if align_method != 2:
            # ... align edges of 150cm x 150cm pixels to origin (X,Y) = (0,0)
            feedback.pushInfo("Define extent of VHM 150cm as aligned to origin (X,Y) = (0,0)...")
            extent_150cm = get_aligned_extent(mask, res=1.5)

        # print("extent of mask aligned to 10m:")
        # print(extent_10m)
        # print("extent of mask aligned to 150cm:")
        # print(extent_150cm)

        if vhm_convert_to_byte:
            feedback.pushInfo("Checking vhm input raster...")
            vhm_input_raster = gdal.Open(vhm_input)
            feedback.pushInfo(f"DataType Code: {vhm_input_raster.GetRasterBand(1).DataType}  "
                              f"(1: Byte, 3: Int16, 6: Float32)")

            if vhm_input_raster.GetRasterBand(1).DataType == 1:
                feedback.pushInfo("vhm raster is already byte, not converting...")
            else:
                feedback.pushInfo("convert vhm raster to byte...")
                param = {
                    'INPUT': vhm_input,
                    'SOURCE_CRS': None,
                    'TARGET_CRS': None,
                    'RESAMPLING': 0,  # nearest neighbour
                    'NODATA': vNA,
                    'TARGET_RESOLUTION': None,
                    'OPTIONS': '',
                    'DATA_TYPE': 1,
                    'TARGET_EXTENT': None,
                    'TARGET_EXTENT_CRS': None,
                    'MULTITHREADING': True,
                    'EXTRA': '-co COMPRESS=LZW -co BIGTIFF=YES',
                    'OUTPUT': tmp_vhm_byte
                }
                processing.run("gdal:warpreproject", param)
                vhm_input = tmp_vhm_byte

        if mask_vhm:
            feedback.pushInfo("mask vhm...")
            param = {
                'INPUT': vhm_input,
                'MASK': mask,
                'SOURCE_CRS': None,
                'TARGET_CRS': None,
                'NODATA': vNA,
                'ALPHA_BAND': False,
                'CROP_TO_CUTLINE': True,
                'KEEP_RESOLUTION': False,
                'SET_RESOLUTION': False,
                'X_RESOLUTION': 0,
                'Y_RESOLUTION': 0,
                'MULTITHREADING': False,
                'OPTIONS': '',
                'DATA_TYPE': 0,
                'EXTRA': '-multi -wm 5000 -co COMPRESS=LZW -co TILED=YES -co BIGTIFF=YES  -wo \"CUTLINE_ALL_TOUCHED=TRUE\"',
                'OUTPUT': tmp_vhm_cropped
            }
            processing.run("gdal:cliprasterbymasklayer", param)

            vhm_input = tmp_vhm_cropped

        if vhm_reclassify:
            feedback.pushInfo("reclassify vhm outliers...")
            if not os.path.exists(os.path.dirname(vhm_detail)):
                os.makedirs(os.path.dirname(vhm_detail))
            PreProcessingHelper.reclassify_min_max(vhm_input, vhm_detail, min_value=vMin, max_value=vMax)
        else:
            feedback.pushInfo("copy as vhm detail...")
            copy_raster_tiff(vhm_input, vhm_detail)

        feedback.pushInfo("aggregate vhm to 150cm...")
        if not os.path.exists(os.path.dirname(vhm_150cm)):
            os.makedirs(os.path.dirname(vhm_150cm))
        param = {
            'INPUT': vhm_detail,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'RESAMPLING': 7,  # maximum
            'NODATA': None,
            'TARGET_RESOLUTION': 1.5,
            'OPTIONS': '',
            'DATA_TYPE': 0,
            'TARGET_EXTENT': extent_150cm,
            'TARGET_EXTENT_CRS': None,
            'MULTITHREADING': False,
            'EXTRA': '-co COMPRESS=LZW ',
            'OUTPUT': vhm_150cm
        }
        processing.run("gdal:warpreproject", param)

        feedback.pushInfo("aggregate vhm to 10m...")
        if not os.path.exists(os.path.dirname(vhm_10m)):
            os.makedirs(os.path.dirname(vhm_10m))
        param = {
            'INPUT': vhm_detail,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'RESAMPLING': 7,  # maximum
            'NODATA': None,
            'TARGET_RESOLUTION': 10,
            'OPTIONS': '',
            'DATA_TYPE': 0,
            'TARGET_EXTENT': extent_10m,
            'TARGET_EXTENT_CRS': None,
            'MULTITHREADING': False,
            'EXTRA': '-co COMPRESS=LZW ',
            'OUTPUT': vhm_10m
        }
        processing.run("gdal:warpreproject", param)

        if mg_use:
            # if raster 10m x 10m are NOT aligned to mixture degree input ...
            if align_method != 1:
                feedback.pushInfo("match VHM<>MG extent, align pixels...")
                param = {
                    'INPUT': mg_input,
                    'SOURCE_CRS': None,
                    'TARGET_CRS': None,
                    'RESAMPLING': 0,  # nearest neighbour
                    'NODATA': None,
                    'TARGET_RESOLUTION': 10,
                    'OPTIONS': '',
                    'DATA_TYPE': 0,
                    # ... align mixture degree layers to VHM 10m layer (however that itself may or may not be aligned)
                    'TARGET_EXTENT': get_raster_extent(vhm_10m),
                    'TARGET_EXTENT_CRS': None,
                    'MULTITHREADING': False,
                    'EXTRA': '-co COMPRESS=LZW -co BIGTIFF=YES',
                    'OUTPUT': tmp_mg_aligned
                }
                processing.run("gdal:warpreproject", param)

            if mg_rescale_factor != 1.0:
                feedback.pushInfo(f"rescale MG values by factor {mg_rescale_factor}...")
                param = {
                    'INPUT_A': tmp_mg_aligned,
                    'BAND_A': 1,
                    'INPUT_B': None, 'BAND_B': None,
                    'INPUT_C': None, 'BAND_C': None,
                    'INPUT_D': None, 'BAND_D': None,
                    'INPUT_E': None, 'BAND_E': None,
                    'INPUT_F': None, 'BAND_F': None,
                    'FORMULA': 'A/' + str(mg_rescale_factor),
                    'NO_DATA': None,
                    'PROJWIN': None,
                    'RTYPE': 0,
                    'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                    'EXTRA': '',
                    'OUTPUT': mg_10m
                }
                processing.run("gdal:rastercalculator", param)
            else:
                feedback.pushInfo(f"not rescaling MG values (factor {mg_rescale_factor}...)")
                copy_raster_tiff(tmp_mg_aligned, mg_10m)

            if mg_reclassify_values:
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

    #--- Algorithm ID, Name

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk prepare VHM (and MG)'

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
        return '0 TBk preprocessing tools'

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'preproc'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Processes VHM (<i>Vegetation Height Model</i>) and optionally <i>Forest Mixture Degree</i> (coniferous raster) raw data to ready to use raster inputs for <b><i>TBk</i></b>’s main algorithm <b><i>Generate BK</i></b>.</p></body></html></p>

<h2>Input parameters</h2>
<h3>Detailed input VHM (.tif)</h3>
<p>VHM raster layer with high resolution (&le; 1.5m x 1.5m)</p>
<h3>Forest mixture degree input (.tif)</h3>
<p>Optional raster layer with <i>Forest Mixture Degree</i> documenting coniferous / delicious share of (woody) vegetation</p>
<h3>Polygon mask to clip final result</h3>
<p>Layer holding (multi-)polygon(s) determines extent of all outputs and masks VHM-derivative, if advanced parameter <b><i>Crop VHM to mask</i></b> is True / checked.</p>
<h3>Output folder</h3>
<p>Path to folder, where output layers are gathered. Ideally in this very folder the later by <b><i>TBk</i></b>'s main algorithm <b><i>Generate BK</i></b> produced output folder is saved.</p>

<h2>Advanced parameters</h2>
<h3>VHM detail output name (.tif)</h3>
<p>string / filename: default <i>VHM_detail.tif</i></p>
<h3>VHM 10m output name (.tif)</h3>
<p>string / filename: default <i>VHM_10m.tif</i></p>
<h3>VHM 150cm output name (.tif)</h3>
<p>string / filename: default <i>VHM_150cm.tif</i></p>
<h3>Mixture degree 10m output name (.tif)</h3>
<p>string / filename: default <i>MG_10m.tif</i></p>
<h3>Binary mixture degree 10m output name (.tif)</h3>
<p>string / filename: default <i>MG_10m_binary.tif</i></p>
<h3>Method aligning output raster layers</h3>
<p>Dropdown menu with three methods to choose from:

<b><i>Align to origin (X,Y) = (0,0)</i></b> (default): All pixel edges match coordinates = <i>k</i> &#183; pixel-resolution (1.5m or 10m), where <i>k</i> is an integer.

<b><i>Align to mixture degree raster</i></b>: If <i>Forest Mixture Degree</i> is among inputs and has pixel resolution 10m x 10m, all pixels of outputs <i>VHM 10m</i>, <i>MG 10m</i> and <i>MG 10m binary</i> are aligned to the original <i>Mixture Degree</i>, while alignment of <i>VHM 150cm</i> is handled as with the default method. If this method is chosen, but the preconditions for its usage are not fulfilled, the alignment is under hood switched to the default method. The advantage of aligning to the original <i>Mixture Degree</i> with resolution 10m x 10m is, that pixels of both <i>MG 10m</i> and <i>MG 10m binary</i> are not shifted.  

<b><i>Random / driven by extent of masks</i></b>: Outputs <i>VHM 10m</i>, <i>MG 10m</i> and <i>MG 10m binary</i> are aligned to each other, but with a random offset from the origin. <i>VHM 150cm</i> has its own random offset.

Notes:
1) No alignment is applied to <i>VHM detail</i>, as this layer is only a (partial) copy of the original VHM. 
2) <b><i>Methods Align to origin</i></b> and <b><i>Align to mixture degree raster</i></b> return the same outputs, if <i>Forest Mixture Degree</i> (10m x 10m) is already aligned to the origin (X,Y) = (0,0). This is the case for the <i>Forest Mixture Degree</i> (Mishunggrad) raster layer provided by WSL with EPSG:2056. 
3) Raster outputs generated with different masks and thus covering different areas, align with each other, if method chosen is either <b><i>Align to origin</i></b> or <b><i>Align to mixture degree raster</i></b>.
4) Method <b><i>Random / driven by extent of masks</i></b> is a legacy allowing to prepare inputs for <b><i>TBk</i></b>’s main algorithm <b><i>Generate BK</i></b> with the sole method in praxis until July 2024.</p>
<h3>Delete temporary files</h3>
<p>Check box: default True.</p>
<h3>Crop VHM to mask</h3>
<p>Check box: default True.</p>
<h3>Convert VHM to BYTE datatype (...)</h3>
<p>Check box: default True.</p>
<h3>Reclassify VHM values < VHM min resp. > VHM max value as NoData.</h3>
<p>Check box: default False.</p>
<h3>VHM min value</h3>
<p>float [m]: default 0m</p>
<h3>VHM max value</h3>
<p>float [m]: default 60m</p>
<h3>VHM NoData value</h3>
<p>integer: default 255</p>
<h3>Rescale Forest mixture degree values ...</h3>
<p>integer: default 100</p>
<h3>Create Binary mixture degree layer ...</h3>
<p>Check box: default True.</p>
<h3>Minimum Deciduous (Laubholz) value</h3>
<p>integer [%]: default 0%</p>
<h3>Maximum Deciduous (Laubholz) value</h3>
<p>integer [%]: default 50%</p>
<h3>Minimum Coniferous (Nadelholz) value</h3>
<p>integer [%]: default 50%</p>
<h3>Maximum Coniferous (Nadelholz) value</h3>
<p>integer [%]: default 100%</p>

<h2>Outputs</h2>
<p>Three VHM and optionally two <i>Forest Mixture Degree</i> derivative raster layers placed in the <b><i>Output folder</i></b> (s. above). File names of these outputs are defined vai the five corresponding advanced parameters (s. above).</p>

<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html></p><br><p align="right">Algorithm authors: Attilio Benini, Hannes Horneber @ BFH-HAFL (2024)</p></body></html>"""

    def createInstance(self):
        return TBkPrepareVhmMgAlgorithm()
