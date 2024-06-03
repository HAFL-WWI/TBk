# -*- coding: utf-8 -*-

#######################################################################
# Extract TBk project with overlapping perimeter.
#
# (C) Attilio Benini, HAFL
#######################################################################

"""
/***************************************************************************
 TBk
                                 A QGIS plugin
 Toolkit for the generation of forest stand maps
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-08-03
        copyright            : (C) 2023 by Berner Fachhochschule HAFL
        email                : christian.rosset@bfh.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Berner Fachhochschule HAFL'
__date__ = '2020-08-03'
__copyright__ = '(C) 2023 by Berner Fachhochschule HAFL'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import time
from datetime import datetime, timedelta

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterDefinition,
                       QgsVectorLayer,
                       QgsApplication)
import processing

from tbk_qgis.tbk.utility.tbk_utilities import *


class TBkPostprocessExtractPerimeter(QgsProcessingAlgorithm):

    def addAdvancedParameter(self, parameter):
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        return self.addParameter(parameter)

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = "OUTPUT"

    # Perimeter with geometries for extracting (polygons/multipolygons)
    PERIMETER = "perimeter"

    # Directory containing the input files
    PATH_TBk_INPUT = "path_tbk_input"

    # Directory containing the extracted material
    OUTPUT_ROOT = "output_root"

    # advanced parameters (list of material to copy resp. to extract)

    # TBk-qgis-project-file (boolean)
    # TBK_QGIS_PROJ = "tbk_qgis_proj"
    # degree of cover raster layer (boolean)
    DG = "dg"
    # degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB)
    # relative to dominant tree height of stand (boolean)
    ALL_DG = "all_dg"
    # VHM with 10m resolution, main input to generate TBk-stand-map (boolean)
    VHM_10M = "vhm_10m"
    # VHM 150cm resolution, used to genrate DG-raster layers (boolean)
    VHM_150CM = "vhm_150cm"
    # detailed VHM raster with original resolution (boolean)
    VHM_DETAIL = "vhm_detail"
    # coniferous raster (boolean)
    MG_10M = "mg_10m"
    # binary coniferous raster, used for stand delineation (boolean)
    MG_10M_BINARY = "mg_10m_binary"
    # clip both coniferous raster and binary coniferous raster by extent, else by mask (boolean)
    MG_CLIP_BY_EXTENT = "mg_clip_by_extent"
    # intermediate layers from TBk-proecessing  (boolean)
    BK_PROCESS = "bk_process"
    # local densities within TBk-stands (post-process output) (boolean)
    LOCAL_DENSITIES = "local_densities"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # Perimeter with geometries for extracting (polygons/multipolygons)
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.PERIMETER,
            self.tr("Perimeter of extraction (polygon(s) and/or mutlipolygon(s)"),
            [QgsProcessing.TypeVectorPolygon])
        )

        # Folder with input
        self.addParameter(QgsProcessingParameterFile(
            self.PATH_TBk_INPUT, self.tr("Folder with TBk project to extract from"),
            behavior=QgsProcessingParameterFile.Folder,
            fileFilter='All Folders (*.*)', defaultValue=None)
        )

        # Folder for algorithm output
        self.addParameter(QgsProcessingParameterFolderDestination(
            self.OUTPUT_ROOT, self.tr('Folder where the extracted material will be stored'))
        )

        # TBk-qgis-project-file (boolean)
        # parameter = QgsProcessingParameterBoolean(
        #     self.TBK_QGIS_PROJ,
        #     self.tr("Copy TBk-qgis-project-file"),
        #     defaultValue=True
        # )
        # self.addAdvancedParameter(parameter)

        # degree of cover raster layer (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.DG,
            self.tr("Degree of cover raster layer"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB)
        # relative to dominant tree height of stand (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.ALL_DG,
            self.tr(
                "Degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB)"
                "\nrelative to dominant tree height of stand"
            ),
        # relative to dominant tree height of stand"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # VHM with 10m resolution, main input to generate TBk-stand-map (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.VHM_10M,
            self.tr("VHM with 10m resolution, main input to generate TBk-stand-map"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # VHM 150cm with resolution, used to genrate DG-raster layers (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.VHM_150CM,
            self.tr("VHM with 150cm resolution, used to genrate degree of cover raster layers"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # detailed VHM raster with original resolution (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.VHM_DETAIL,
            self.tr("Detailed VHM raster with original resolution"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # coniferous raster (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.MG_10M,
            self.tr("Coniferous raster / forest mixture degree with 10m resolution"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # binary coniferous raster, used for stand delineation (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.MG_10M_BINARY,
            self.tr("Binary coniferous raster with 10m resolution, used for stand delineation"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # clip both coniferous raster and binary coniferous raster by extent, else by mask (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.MG_CLIP_BY_EXTENT,
            self.tr("Clip both coniferous raster and binary coniferous raster by extent, else by mask"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # intermediate layers from TBk-proecessing  (boolean)
        BK_PROCESS = "bk_process"
        parameter = QgsProcessingParameterBoolean(
            self.BK_PROCESS,
            self.tr("Intermediate layers from TBk-proecessing (folder bk_process)"),
            defaultValue=False
        )
        self.addAdvancedParameter(parameter)

        # local densities within TBk-stands (post-process output) (boolean)
        LOCAL_DENSITIES = "local_densities"
        parameter = QgsProcessingParameterBoolean(
            self.LOCAL_DENSITIES,
            self.tr("Local densities within TBk-stands (post-process output)"),
            defaultValue=False
        )
        self.addAdvancedParameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # get and check perimeter file
        perimeter = str(self.parameterAsVectorLayer(parameters, self.PERIMETER, context).source())

        path_tbk_input = self.parameterAsString(parameters, self.PATH_TBk_INPUT, context)

        output_root = self.parameterAsString(parameters, self.OUTPUT_ROOT, context)
        path_output = output_root
        ensure_dir(path_output)

        settings_path = QgsApplication.qgisSettingsDirPath()
        feedback.pushInfo(settings_path)

        tbk_tool_path = os.path.join(settings_path, "python/plugins/tbk_qgis")

        # TBk-qgis-project-file (boolean)
        # tbk_qgis_proj = self.parameterAsBool(parameters, self.TBK_QGIS_PROJ, context)

        # degree of cover raster layer (boolean)
        dg = self.parameterAsBool(parameters, self.DG, context)

        # degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB)
        # relative to dominant tree height of stand (boolean)
        all_dg = self.parameterAsBool(parameters, self.ALL_DG, context)

        # VHM with 10m resolution, main input to generate TBk-stand-map (boolean)
        vhm_10m = self.parameterAsBool(parameters, self.VHM_10M, context)

        # VHM 150cm resolution, used to genrate DG-raster layers (boolean)
        vhm_150cm = self.parameterAsBool(parameters, self.VHM_150CM, context)

        # detailed VHM raster with original resolution (boolean)
        vhm_detail = self.parameterAsBool(parameters, self.VHM_DETAIL, context)

        # coniferous raster (boolean)
        mg_10m = self.parameterAsBool(parameters, self.MG_10M, context)

        # binary coniferous raster, used for stand delineation (boolean)
        mg_detail_binary = self.parameterAsBool(parameters, self.MG_10M_BINARY, context)

        # clip both coniferous raster and binary coniferous raster by extent, else by mask (boolean)
        mg_clip_by_extent = self.parameterAsBool(parameters, self.MG_CLIP_BY_EXTENT, context)

        # intermediate layers from TBk-proecessing  (boolean)
        bk_process = self.parameterAsBool(parameters, self.BK_PROCESS, context)

        # local densities within TBk-stands (post-process output) (boolean)
        local_densities = self.parameterAsBool(parameters, self.LOCAL_DENSITIES, context)

        start_time = time.time()

        # if tbk_qgis_proj:
        #     path_tbk_qgis_proj = os.path.join(path_tbk_input, "TBk_Project.qgz")
        #     if os.path.exists(path_tbk_qgis_proj) == False:
        #         raise QgsProcessingException(
        #             "No TBk-QGIS-file found:\n" + path_tbk_qgis_proj + "\ndoes not exist.")

        # list to gather TBk vector layer for extraction (TBk main dataset not included)
        tbk_vector_datasets = []
        # list to gather TBk vector layer for extraction (TBk main dataset not included)
        tbk_raster_datasets = []

        # if required add degree of cover to list of raster datasets
        if dg:
            path_dg = os.path.join(path_tbk_input, "dg_layers", "dg_layer.tif")
            if os.path.exists(path_dg) == False:
                raise QgsProcessingException("No degree of cover raster layer found:\n" + path_dg + "\ndoes not exist.")
            tbk_raster_datasets.append(os.path.join("dg_layers", "dg_layer.tif"))

        # if required add degree of cover layer for specific height ranges (relative to hdom) to list of raster datasets
        if all_dg:
            for i in ["ks", "us", "ms", "os", "ueb"]:
                path_dg_i = os.path.join(path_tbk_input, "dg_layers", "dg_layer_" + i + ".tif")
                if os.path.exists(path_dg_i) == False:
                    raise QgsProcessingException(
                        "For the " + i.upper() + " height range no degree of cover raster layer found:\n" + path_dg_i + "\ndoes not exist.")
                tbk_raster_datasets.append(os.path.join("dg_layers", "dg_layer_" + i + ".tif"))

        # if required add VHM with detail resolution to list of raster datasets
        if vhm_10m:
            path_vhm_10m = os.path.join(path_tbk_input, "..", "VHM_10m.tif")
            if os.path.exists(path_vhm_10m) == False:
                raise QgsProcessingException("No VHM with resolution 10m found:\n" + path_vhm_10m + "\ndoes not exist.")
            tbk_raster_datasets.append(os.path.join("..", "VHM_10m.tif"))

        # if required add VHM with 150cm resolution to list of raster datasets
        if vhm_150cm:
            path_vhm_150cm = os.path.join(path_tbk_input, "..", "VHM_150cm.tif")
            if os.path.exists(path_vhm_150cm) == False:
                raise QgsProcessingException("No VHM with resolution 150cm found:\n" + path_vhm_150cm + "\ndoes not exist.")
            tbk_raster_datasets.append(os.path.join("..", "VHM_150cm.tif"))

        # if required add detailed VHM to list of raster datasets
        if vhm_detail:
            path_vhm_detail = os.path.join(path_tbk_input, "..", "VHM_detail.tif")
            if os.path.exists(path_vhm_detail) == False:
                raise QgsProcessingException("No detailed VHM with original resolution found:\n" + path_vhm_detail + "\ndoes not exist.")
            tbk_raster_datasets.append(os.path.join("..", "VHM_detail.tif"))

        # if required add coniferous raster to list of raster datasets
        if mg_10m:
            path_mg_10m = os.path.join(path_tbk_input, "..", "MG_10m.tif")
            if os.path.exists(path_mg_10m) == False:
                raise QgsProcessingException("No coniferous raster found:\n" + path_mg_10m + "\ndoes not exist.")
            tbk_raster_datasets.append(os.path.join("..", "MG_10m.tif"))

        # if required add coniferous raster to list of raster datasets
        if mg_detail_binary:
            path_mg_detail_binary = os.path.join(path_tbk_input, "..", "MG_10m_binary.tif")
            if os.path.exists(path_mg_detail_binary) == False:
                raise QgsProcessingException("No binary coniferous raster found:\n" + path_mg_detail_binary + "\ndoes not exist.")
            tbk_raster_datasets.append(os.path.join("..", "MG_10m_binary.tif"))

        # if required add intermediate layers from TBk-processing to lists of vector resp. raster datasets
        # note: .csv & folder tmp are not extracted
        if bk_process:
            path_bk_process = os.path.join(path_tbk_input, "bk_process")
            if os.path.exists(path_bk_process) == False:
                raise QgsProcessingException(
                    "No folder with intermediate layers from TBk-processing found:\n" + path_bk_process + "\ndoes not exist.")
            file_list = os.listdir(path_bk_process)
            for file in file_list:
                if file.endswith(".gpkg"):
                    tbk_vector_datasets.append(os.path.join("bk_process", file))
                elif file.endswith(".tif"):
                    tbk_raster_datasets.append(os.path.join("bk_process", file))

        # if required add local densities to list of vector datasets
        if local_densities:
            path_local_densities = os.path.join(path_tbk_input, "local_densities")
            if os.path.exists(path_local_densities) == False:
                raise QgsProcessingException(
                    "No local densities' folder found:\n" + path_local_densities + "\ndoes not exist.")
            file_list = os.listdir(path_local_densities)
            for file in file_list:
                if file.endswith(".gpkg"):
                    tbk_vector_datasets.append(os.path.join("local_densities", file))

        # check gathered vector datatsets
        # for v in tbk_vector_datasets: print(v)
        # check gathered vector datatsets
        # for r in tbk_raster_datasets: print(r)

        # helper function to save intermediate vector data & tables
        def f_save_as_gpkg(input, name, path=path_output):
            if type(input) == str:
                input = QgsVectorLayer(input, '', 'ogr')
            path_ = os.path.join(path, name + ".gpkg")
            ctc = QgsProject.instance().transformContext()
            QgsVectorFileWriter.writeAsVectorFormatV3(input, path_, ctc, getVectorSaveOptions('GPKG', 'utf-8'))

        # check perimeter
        # f_save_as_gpkg(perimeter, "perimeter")

        # path to original main TBk layer
        path_tbk_main_in = os.path.join(path_tbk_input, "TBk_Bestandeskarte.gpkg")
        # path to extracted main TBb layer
        path_tbk_main_out = os.path.join(path_output, "TBk_Bestandeskarte.gpkg")

        # extract main TBk layer
        param = {
            'INPUT': path_tbk_main_in,
            'PREDICATE': [0], # intersect
            'INTERSECT': perimeter,
            'OUTPUT': path_tbk_main_out
        }
        algoOutput = processing.run("native:extractbylocation", param)
        algoOutput["OUTPUT"]

        # extract raster datatsets
        if len(tbk_raster_datasets) > 0:

            # dict for buffered extraction perimeters according to resolution of raster layer to be extracted
            extraction_perimeter_raster = {}

            for i, ds in enumerate(tbk_raster_datasets):
                # build input and output path
                dataset_in = os.path.join(path_tbk_input, ds)
                dataset_out = os.path.join(path_output, ds)

                # check if output(-folder) does not exist
                if not os.path.exists(dataset_out):
                    # create output folder if it doesn't exist
                    if not os.path.exists(os.path.dirname(dataset_out)):
                        os.makedirs(os.path.dirname(dataset_out))

                # get resolution of raster layer
                param =  {'INPUT': dataset_in, 'BAND': None}
                res_i = processing.run("native:rasterlayerproperties",param)['PIXEL_HEIGHT']

                # create extraction perimeter of raster dataset if it does not exist yet
                if not str(res_i) in extraction_perimeter_raster:
                    param = {
                        'INPUT': path_tbk_main_out,  # extracted main TBk layer
                        'DISTANCE': res_i,  # resolution of raster layer to be extracted as buffer distance
                        'SEGMENTS': 5,
                        'END_CAP_STYLE': 0,  # round
                        'JOIN_STYLE': 0,  # round
                        'MITER_LIMIT': 2,
                        'DISSOLVE': True,
                        'SEPARATE_DISJOINT': False,
                        'OUTPUT': 'TEMPORARY_OUTPUT'
                    }
                    algoOutput = processing.run("native:buffer", param)
                    extraction_perimeter_raster[str(res_i)] = algoOutput["OUTPUT"]
                    # check extraction perimeter for raster layer
                    # f_save_as_gpkg(extraction_perimeter_raster[str(res_i)], "extraction_perimeter_raster_" + str(res_i))

                # if coniferous rasters and required to clip by extent
                if ds[3:] in ["MG_10m.tif", "MG_10m_binary.tif"] and mg_clip_by_extent:
                    param = {
                        'INPUT': dataset_in,
                        'PROJWIN': extraction_perimeter_raster[str(res_i)].extent(),
                        'OVERCRS': False,
                        'NODATA': None,
                        'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                        'DATA_TYPE': 0, # use input layer data type
                        'EXTRA': '',
                        'OUTPUT': dataset_out
                    }
                    algoOutput = processing.run("gdal:cliprasterbyextent", param)
                    algoOutput["OUTPUT"]
                # else
                else:
                    param = {
                        'INPUT': dataset_in,
                        'MASK': extraction_perimeter_raster[str(res_i)],
                        'SOURCE_CRS': None,
                        'TARGET_CRS': None,
                        'TARGET_EXTENT': None,
                        'NODATA': None,
                        'ALPHA_BAND': False,
                        'CROP_TO_CUTLINE': True,
                        'KEEP_RESOLUTION': False,
                        'SET_RESOLUTION': False,
                        'X_RESOLUTION': None,
                        'Y_RESOLUTION': None,
                        'MULTITHREADING': True,
                        'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                        'DATA_TYPE': 0,  # use input layer data type
                        'EXTRA': '',
                        'OUTPUT': dataset_out
                    }
                    algoOutput = processing.run("gdal:cliprasterbymasklayer", param)
                    algoOutput["OUTPUT"]

        # extract vector datatsets
        if len(tbk_vector_datasets) > 0:

            # create extraction perimeter of vector datasets
            param = {
                'INPUT': path_tbk_main_out,   # extracted main TBk layer
                'DISTANCE': 0.0001,
                'SEGMENTS': 5,
                'END_CAP_STYLE': 0,  # round
                'JOIN_STYLE': 0,  # round
                'MITER_LIMIT': 2,
                'DISSOLVE': True,
                'SEPARATE_DISJOINT': False,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }
            algoOutput = processing.run("native:buffer", param)
            extraction_perimeter_vector = algoOutput["OUTPUT"]
            # check perimeter for vector layers
            # f_save_as_gpkg(extraction_perimeter_vector, "extraction_perimeter_vector")

            for i, ds in enumerate(tbk_vector_datasets):
                # build input and output path
                dataset_in = os.path.join(path_tbk_input, ds)
                dataset_out = os.path.join(path_output, ds)

                # check if output(-folder) does not exist
                if not os.path.exists(dataset_out):
                    # create output folder if it doesn't exist
                    if not os.path.exists(os.path.dirname(dataset_out)):
                        os.makedirs(os.path.dirname(dataset_out))

                # do the extraction
                param = {
                    'INPUT': dataset_in,
                    'PREDICATE': [6],  # within
                    'INTERSECT': extraction_perimeter_vector,
                    'OUTPUT': dataset_out
                }
                algoOutput = processing.run("native:extractbylocation", param)
                algoOutput["OUTPUT"]

        feedback.pushInfo("====================================================================")
        feedback.pushInfo("FINISHED")
        feedback.pushInfo("TOTAL PROCESSING TIME: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time))))
        feedback.pushInfo("====================================================================")

        return {self.OUTPUT: path_output}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk postprocess extract perimeter'

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
        return '2 TBk Postprocessing'

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'postproc'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TBkPostprocessExtractPerimeter()
