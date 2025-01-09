# -*- coding: utf-8 -*-
# *************************************************************************** #
# Extract perimeter from TBk project (multiple files).
#
# (C) Attilio Benini (BFH-HAFL)
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
from shutil import copyfile

from qgis.PyQt.QtCore import QCoreApplication
import processing

from tbk_qgis.tbk.general.tbk_utilities import *
from tbk_qgis.tbk.tools.G_utility.tbk_qgis_processing_algorithm_toolsG import TBkProcessingAlgorithmToolG

class TBkPostprocessExtractPerimeter(TBkProcessingAlgorithmToolG):

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

    # copy TBk-qgis-project-file (boolean)
    TBK_QGIS_PROJ = "tbk_qgis_proj"
    # relative path to TBk-qgis-project-file (string)
    TBK_QGIS_PROJ_PATH = "tbk_qgis_proj_path"
    # relative path to TBk input file (string)
    TBK_INPUT_FILE_PATH = "tbk_input_file_path"
    # degree of cover raster layer (boolean)
    DG = "dg"
    # relative path to degree of cover raster layer (string)
    DG_PATH = "dg_path"
    # degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB)
    # relative to dominant tree height of stand (boolean)
    ALL_DG = "all_dg"
    # relative path to folder with degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB) (string)
    ALL_DG_PATH = "all_dg_path"
    # VHM with 10m resolution, main input to generate TBk-stand-map (boolean)
    VHM_10M = "vhm_10m"
    # relative path to VHM 10m resolution (string)
    VHM_10M_PATH = "vhm_10m_path"
    # VHM 150cm resolution, used to genrate DG-raster layers (boolean)
    VHM_150CM = "vhm_150cm"
    # relative path to VHM 150cm resolution (string)
    VHM_150CM_PATH = "vhm_150cm_path"
    # detailed VHM raster with original resolution (boolean)
    VHM_DETAIL = "vhm_detail"
    # relative path to detailed VHM (string)
    VHM_DETAIL_PATH = "vhm_detail_path"
    # clip 3 VHM raster layers by extent, else by mask (boolean)
    VHM_CLIP_BY_EXTENT = "vhm_clip_by_extent"
    # coniferous raster (boolean)
    MG_10M = "mg_10m"
    # relative path to coniferous raster (string)
    MG_10M_PATH = "mg_10m_path"
    # binary coniferous raster, used for stand delineation (boolean)
    MG_10M_BINARY = "mg_10m_binary"
    # relative path to binary coniferous raster (string)
    MG_10M_BINARY_PATH = "mg_10m_binary_path"
    # clip both coniferous raster and binary coniferous raster by extent, else by mask (boolean)
    MG_CLIP_BY_EXTENT = "mg_clip_by_extent"
    # intermediate layers from TBk-proecessing  (boolean)
    BK_PROCESS = "bk_process"
    # relative path to folder with intermediate layers (string)
    BK_PROCESS_PATH = "bk_process_path"
    # local densities within TBk-stands (post-process output) (boolean)
    LOCAL_DENSITIES = "local_densities"
    # relative path to folder local densities (string)
    LOCAL_DENSITIES_PATH = "local_densities_path"
    # list of relative paths to additional material (matrix as one-dimensional list)
    ADDITIONAL_MATERIAL_PATHS = "additional_material_paths"

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

        # TBk input file name (string)
        parameter = QgsProcessingParameterString(
            self.TBK_INPUT_FILE_PATH,
            self.tr("Relative path to TBk-map-file (.gpkg)"),
            defaultValue='TBk_Bestandeskarte.gpkg'  # output of Generate TBk
        )
        self.addAdvancedParameter(parameter)

        # TBk-qgis-project-file (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.TBK_QGIS_PROJ,
            self.tr("Copy TBk-QGIS-project-file"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # relative path to TBk-qgis-project-file (string)
        parameter = QgsProcessingParameterString(
            self.TBK_QGIS_PROJ_PATH,
            self.tr("Relative path to TBk-QGIS-project-file (.qgz / .qgs)"),
            defaultValue='TBk_Project.qgz'  # output of Generate TBk
        )
        self.addAdvancedParameter(parameter)

        # degree of cover raster layer (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.DG,
            self.tr("Degree of cover raster layer"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # relative path to degree of cover raster layer (string)
        parameter = QgsProcessingParameterString(
            self.DG_PATH,
            self.tr("Relative path to degree of cover raster layer"),
            defaultValue=os.path.join("dg_layers", "dg_layer.tif")  # output of Generate TBk
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

        # relative path to folder with degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB) (string)
        parameter = QgsProcessingParameterString(
            self.ALL_DG_PATH,
            self.tr("Relative path to folder with degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB)"),
            defaultValue="dg_layers"  # output of Generate TBk
        )
        self.addAdvancedParameter(parameter)

        # VHM with 10m resolution, main input to generate TBk-stand-map (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.VHM_10M,
            self.tr("VHM with 10m resolution, main input to generate TBk-stand-map"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # relative path to VHM 10m resolution (string)
        parameter = QgsProcessingParameterString(
            self.VHM_10M_PATH,
            self.tr("Relative path VHM 10m layer"),
            defaultValue=os.path.join("../..", "VHM_10m.tif")  # input of Generate TBk
        )
        self.addAdvancedParameter(parameter)

        # VHM 150cm with resolution, used to genrate DG-raster layers (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.VHM_150CM,
            self.tr("VHM with 150cm resolution, used to genrate degree of cover raster layers"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # relative path to VHM 150cm resolution (string)
        parameter = QgsProcessingParameterString(
            self.VHM_150CM_PATH,
            self.tr("Relative path VHM 150cm layer"),
            defaultValue=os.path.join("../..", "VHM_150cm.tif")  # input of Generate TBk
        )
        self.addAdvancedParameter(parameter)

        # detailed VHM raster with original resolution (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.VHM_DETAIL,
            self.tr("Detailed VHM raster with original resolution"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # relative path to detailed VHM (string)
        parameter = QgsProcessingParameterString(
            self.VHM_DETAIL_PATH,
            self.tr("Relative path to detailed VHM layer"),
            defaultValue=os.path.join("../..", "VHM_detail.tif")  # input of Generate TBk
        )
        self.addAdvancedParameter(parameter)

        # clip 3 VHM raster layers by extent, else by mask (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.VHM_CLIP_BY_EXTENT,
            self.tr("Clip VHM 10m, VHM 150cm and VHM detail by extent, else by mask"),
            defaultValue=False
        )
        self.addAdvancedParameter(parameter)

        # coniferous raster (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.MG_10M,
            self.tr("Coniferous raster / forest mixture degree with 10m resolution"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # relative path to coniferous raster (string)
        parameter = QgsProcessingParameterString(
            self.MG_10M_PATH,
            self.tr("Relative path to coniferous raster"),
            defaultValue=os.path.join("../..", "MG_10m.tif")  # input of Generate TBk
        )
        self.addAdvancedParameter(parameter)

        # binary coniferous raster, used for stand delineation (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.MG_10M_BINARY,
            self.tr("Binary coniferous raster with 10m resolution, used for stand delineation"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # relative path to coniferous raster (string)
        parameter = QgsProcessingParameterString(
            self.MG_10M_BINARY_PATH,
            self.tr("Relative path to binary coniferous raster"),
            defaultValue=os.path.join("../..", "MG_10m_binary.tif")  # input of Generate TBk
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
            self.tr("Intermediate layers from TBk-proecessing"),
            defaultValue=False
        )
        self.addAdvancedParameter(parameter)

        # relative path to folder with intermediate layers (string)
        parameter = QgsProcessingParameterString(
            self.BK_PROCESS_PATH,
            self.tr("Relative path to folder with intermediate layers"),
            defaultValue="bk_process"  # output of Generate TBk
        )
        self.addAdvancedParameter(parameter)

        # local densities within TBk-stands (post-process output) (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.LOCAL_DENSITIES,
            self.tr("Local densities within TBk-stands (post-process output)"),
            defaultValue=False
        )
        self.addAdvancedParameter(parameter)

        # relative path to folder local density (string)
        parameter = QgsProcessingParameterString(
            self.LOCAL_DENSITIES_PATH,
            self.tr("Relative path to folder with local densities"),
            defaultValue="local_densities"  # output of TBk Postprocess Local Density
        )
        self.addAdvancedParameter(parameter)

        # list of relative paths to additional material (matrix as one-dimensional list)
        parameter = QgsProcessingParameterMatrix(
            self.ADDITIONAL_MATERIAL_PATHS,
            self.tr(
                "List relative* paths to additional materials"
                "\n- single vector layers / .gpkg files,"
                "\n- single raster layers / .tif files or"
                "\n- folders containing vector and/or raster layers"
                "\ncan be listed."
                '\n* relative to "Folder with TBk project to extract from"'
            ),
            hasFixedNumberRows=False,
            headers=['relative path'],
            defaultValue=[],
            optional=True
        )
        self.addAdvancedParameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # get and check perimeter file
        perimeter = str(self.parameterAsVectorLayer(parameters, self.PERIMETER, context).source())

        # path to folder with TBk-input
        path_tbk_input = self.parameterAsString(parameters, self.PATH_TBk_INPUT, context)
        # name to folder with TBk-input
        tbk_folder = os.path.basename(os.path.normpath(path_tbk_input))
        # print(tbk_folder)

        # folder where output goes
        output_root = self.parameterAsString(parameters, self.OUTPUT_ROOT, context)
        # print(output_root)
        # folder same-named as folder with TBk-input placed within output-folder
        path_output = os.path.join(output_root, tbk_folder)
        ensure_dir(path_output)
        # print(path_output)

        # relative path to TBk-map-file (string)
        tbk_input_file_path = self.parameterAsString(parameters, self.TBK_INPUT_FILE_PATH, context)

        # TBk-qgis-project-file (boolean)
        tbk_qgis_proj = self.parameterAsBool(parameters, self.TBK_QGIS_PROJ, context)
        # relative path to TBk-qgis-project-file (string)
        tbk_qgis_proj_path = self.parameterAsString(parameters, self.TBK_QGIS_PROJ_PATH, context)

        # degree of cover raster layer (boolean)
        dg = self.parameterAsBool(parameters, self.DG, context)
        # relative path to degree of cover raster layer (string)
        dg_path = self.parameterAsString(parameters, self.DG_PATH, context)

        # degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB)
        # relative to dominant tree height of stand (boolean)
        all_dg = self.parameterAsBool(parameters, self.ALL_DG, context)
        # relative path to folder with degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB) (string)
        all_dg_path = self.parameterAsString(parameters, self.ALL_DG_PATH, context)

        # VHM with 10m resolution, main input to generate TBk-stand-map (boolean)
        vhm_10m = self.parameterAsBool(parameters, self.VHM_10M, context)
        # relative path to VHM 10m resolution (string)
        vhm_10m_path = self.parameterAsString(parameters, self.VHM_10M_PATH, context)

        # VHM 150cm resolution, used to genrate DG-raster layers (boolean)
        vhm_150cm = self.parameterAsBool(parameters, self.VHM_150CM, context)
        # relative path to VHM 150cm resolution (string)
        vhm_150cm_path = self.parameterAsString(parameters, self.VHM_150CM_PATH, context)

        # detailed VHM raster with original resolution (boolean)
        vhm_detail = self.parameterAsBool(parameters, self.VHM_DETAIL, context)
        # relative path to detailed VHM (string)
        vhm_detail_path = self.parameterAsString(parameters, self.VHM_DETAIL_PATH, context)

        # clip 3 VHM raster layers by extent, else by mask (boolean)
        vhm_clip_by_extent = self.parameterAsBool(parameters, self.VHM_CLIP_BY_EXTENT, context)

        # coniferous raster (boolean)
        mg_10m = self.parameterAsBool(parameters, self.MG_10M, context)
        # relative path to coniferous raster (string)
        mg_10m_path = self.parameterAsString(parameters, self.MG_10M_PATH, context)

        # binary coniferous raster, used for stand delineation (boolean)
        mg_10m_binary = self.parameterAsBool(parameters, self.MG_10M_BINARY, context)
        # relative path to coniferous raster (string)
        mg_10m_binary_path = self.parameterAsString(parameters, self.MG_10M_BINARY_PATH, context)

        # clip both coniferous raster and binary coniferous raster by extent, else by mask (boolean)
        mg_clip_by_extent = self.parameterAsBool(parameters, self.MG_CLIP_BY_EXTENT, context)

        # intermediate layers from TBk-proecessing  (boolean)
        bk_process = self.parameterAsBool(parameters, self.BK_PROCESS, context)
        # relative path to folder with intermediate layers (string)
        bk_process_path = self.parameterAsString(parameters, self.BK_PROCESS_PATH, context)

        # local densities within TBk-stands (post-process output) (boolean)
        local_densities = self.parameterAsBool(parameters, self.LOCAL_DENSITIES, context)
        # relative path to folder with local densities (string)
        local_densities_path = self.parameterAsString(parameters, self.LOCAL_DENSITIES_PATH, context)

        # list of relative paths to additional material (matrix as one-dimensional list)
        additional_material_paths = self.parameterAsMatrix(parameters, self.ADDITIONAL_MATERIAL_PATHS, context)
        # make sure paths to additional material are unique strings with length >= 0
        if len(additional_material_paths) > 0:
            # make strings
            for i in range(len(additional_material_paths)):
                additional_material_paths[i] = str(additional_material_paths[i])
            # check string length
            if True in (path == '' for path in additional_material_paths):
                raise QgsProcessingException(
                    "List with relative paths to additional materials includes at least one string with length 0" +
                    " / an empty string. Make sure to include only valid paths."
                )
            # stop if duplicates among paths
            dup = [path for path in set(additional_material_paths) if additional_material_paths.count(path) > 1]
            message_end = ' more than once in list with relative paths to additional materials. But no duplicates are allowed.'
            if len(dup) == 1: message_dup = dup[0] + ' appears' + message_end
            if len(dup) > 1: message_dup = "{} and {}".format(', '.join(dup[:-1]), dup[-1]) + ' appear' + message_end
            if len(dup) > 0: raise QgsProcessingException(message_dup)

        start_time = time.time()

        if tbk_qgis_proj:
            path_tbk_qgis_proj = os.path.join(path_tbk_input, tbk_qgis_proj_path)
            if os.path.exists(path_tbk_qgis_proj) == False:
                raise QgsProcessingException(
                    "No TBk-QGIS-project-file found:\n" + path_tbk_qgis_proj + "\ndoes not exist.")

        # dictionary to gather vector layers for extraction (as key) and corresponding feedback message (as value),
        # TBk main dataset / TBk-stand-map not included
        tbk_vector_datasets = {}
        # dictionary to gather raster layers for extraction (as key) and corresponding feedback message (as value)
        tbk_raster_datasets = {}

        # if required add degree of cover to list of raster datasets
        if dg:
            path_dg = os.path.join(path_tbk_input, dg_path)
            if os.path.exists(path_dg) == False:
                raise QgsProcessingException("No degree of cover raster layer found:\n" + path_dg + "\ndoes not exist.")
            tbk_raster_datasets[dg_path] = "extract degree of cover raster layer ..."

        # if required add degree of cover layer for specific height ranges (relative to hdom) to list of raster datasets
        if all_dg:
            for i in ["ks", "us", "ms", "os", "ueb"]:
                path_dg_i = os.path.join(path_tbk_input, all_dg_path, "dg_layer_" + i + ".tif")
                if os.path.exists(path_dg_i) == False:
                    raise QgsProcessingException(
                        "For the " + i.upper() + " height range no degree of cover raster layer found:\n" + path_dg_i + "\ndoes not exist.")
                tbk_raster_datasets[os.path.join(all_dg_path, "dg_layer_" + i + ".tif")] = "extract 5 degree of cover raster layers specific to height ranges relative to hdom ... "

        # if required add VHM with detail resolution to list of raster datasets
        if vhm_10m:
            path_vhm_10m = os.path.join(path_tbk_input, vhm_10m_path)
            if os.path.exists(path_vhm_10m) == False:
                raise QgsProcessingException("No VHM with resolution 10m found:\n" + path_vhm_10m + "\ndoes not exist.")
            tbk_raster_datasets[vhm_10m_path] = "extract VHM with resolution 10m ..."

        # if required add VHM with 150cm resolution to list of raster datasets
        if vhm_150cm:
            path_vhm_150cm = os.path.join(path_tbk_input, vhm_150cm_path)
            if os.path.exists(path_vhm_150cm) == False:
                raise QgsProcessingException("No VHM with resolution 150cm found:\n" + path_vhm_150cm + "\ndoes not exist.")
            tbk_raster_datasets[vhm_150cm_path] = "extract VHM with resolution 150cm ..."

        # if required add detailed VHM to list of raster datasets
        if vhm_detail:
            path_vhm_detail = os.path.join(path_tbk_input, vhm_detail_path)
            if os.path.exists(path_vhm_detail) == False:
                raise QgsProcessingException("No detailed VHM with original resolution found:\n" + path_vhm_detail + "\ndoes not exist.")
            tbk_raster_datasets[vhm_detail_path] = "extract detailed VHM with with original resolution ..."

        # if required add coniferous raster to list of raster datasets
        if mg_10m:
            path_mg_10m = os.path.join(path_tbk_input, mg_10m_path)
            if os.path.exists(path_mg_10m) == False:
                raise QgsProcessingException("No coniferous raster found:\n" + path_mg_10m + "\ndoes not exist.")
            tbk_raster_datasets[mg_10m_path] = "extract coniferous raster ..."

        # if required add coniferous raster to list of raster datasets
        if mg_10m_binary:
            path_mg_10m_binary = os.path.join(path_tbk_input, mg_10m_binary_path)
            if os.path.exists(path_mg_10m_binary) == False:
                raise QgsProcessingException("No binary coniferous raster found:\n" + path_mg_10m_binary + "\ndoes not exist.")
            tbk_raster_datasets[mg_10m_binary_path] = "extract binary coniferous raster ..."

        # if required add intermediate layers from TBk-processing to lists of vector resp. raster datasets
        # note: .csv & folder tmp are not extracted
        if bk_process:
            path_bk_process = os.path.join(path_tbk_input, bk_process_path)
            if os.path.exists(path_bk_process) == False:
                raise QgsProcessingException(
                    "No folder with intermediate layers from TBk-processing found:\n" + path_bk_process + "\ndoes not exist.")
            file_list = os.listdir(path_bk_process)
            n_gpkg = sum(1 for file in file_list if file.endswith(".gpkg"))
            plural = ""
            if n_gpkg > 1: plural = "s"
            message_gpkg = ("extract " + str(n_gpkg) + " vector layer" + plural +
                            " (.gpkg) from folder holding intermediates from TBk-processing ...")
            n_tif = sum(1 for file in file_list if file.endswith(".tif"))
            plural = ""
            if n_tif > 1: plural = "s"
            message_tif = ("extract " + str(n_tif) + " raster layer" + plural +
                           " (.tif) from folder holding intermediates from TBk-processing ...")
            for file in file_list:
                if file.endswith(".gpkg"):
                    tbk_vector_datasets[os.path.join(bk_process_path, file)] = message_gpkg
                elif file.endswith(".tif"):
                    tbk_raster_datasets[os.path.join(bk_process_path, file)] = message_tif

        # if required add local densities to list of vector datasets
        if local_densities:
            path_local_densities = os.path.join(path_tbk_input, local_densities_path)
            if os.path.exists(path_local_densities) == False:
                raise QgsProcessingException(
                    "No local densities' folder found:\n" + path_local_densities + "\ndoes not exist.")
            file_list = os.listdir(path_local_densities)
            n_gpkg = sum(1 for file in file_list if file.endswith(".gpkg"))
            plural = ""
            if n_gpkg > 1: plural = "s"
            message_gpkg = ("extract " + str(n_gpkg) + " vector layer" + plural + " (.gpkg) from local densities folder ...")
            for file in file_list:
                if file.endswith(".gpkg"):
                    tbk_vector_datasets[os.path.join(local_densities_path, file)] = message_gpkg

        # if required add additional materials via relative paths to
        # - single raster layers,
        # - single vector layer and/or
        # - folder containing raster and/or vector layers
        if len(additional_material_paths) > 0:
            for path in additional_material_paths:
                path_complete = os.path.join(path_tbk_input, path)
                if os.path.exists(path_complete) == False:
                    raise QgsProcessingException(
                        path +
                        " is listed among addition materials to extract from, but " +
                        "\n" + path_complete +
                        "\ndoes not exist."
                    )
                if path.endswith(".gpkg"):
                    tbk_vector_datasets[path] = "extract " + path + " (additional material) ..."
                elif path.endswith(".tif"):
                    tbk_raster_datasets[path] = "extract " + path + " (additional material) ..."
                elif os.path.isdir(path_complete):
                    file_list = os.listdir(path_complete)
                    if (not True in (file.endswith(".gpkg") or file.endswith(".tif") for file in file_list)):
                        raise QgsProcessingException(
                            path +
                            " is listed among addition materials to extract from, and " +
                            "\n" + path_complete +
                            "\ndoes exist. But this folder does not contain any .gpkg nor any .tif file. So there's no geodata to extract."
                        )
                    n_gpkg = sum(1 for file in file_list if file.endswith(".gpkg"))
                    plural = ""
                    if n_gpkg > 1: plural = "s"
                    message_gpkg = "extract " + str(n_gpkg) + " vector layer" + plural + " (.gpkg) from folder " + path + " (additional material) ..."
                    n_tif = sum(1 for file in file_list if file.endswith(".tif"))
                    plural = ""
                    if n_tif > 1: plural = "s"
                    message_tif = "extract " + str(n_tif) + " raster layer" + plural + " (.tif) from folder " + path + " (additional material) ..."
                    for file in file_list:
                        if file.endswith(".gpkg"):
                            tbk_vector_datasets[os.path.join(path, file)] = message_gpkg
                        elif file.endswith(".tif"):
                            tbk_raster_datasets[os.path.join(path, file)] = message_tif
                else:
                    raise QgsProcessingException(
                        path +
                        " is listed among addition materials to extract from, and " +
                        "\n" + path_complete +
                        "\ndoes exist. But it is not a .gpgk, a .tif nor a directory (potentially holding .gpkg and/or .tif files)."
                    )

        # check gathered vector datatsets + corresponding feedback massages
        # for key, value in tbk_vector_datasets.items(): print(f"{key}: {value}")
        # check gathered vector datatsets + corresponding feedback massages
        # for key, value in tbk_raster_datasets.items(): print(f"{key}: {value}")

        # helper function to save intermediate vector data & tables
        def f_save_as_gpkg(input, name, path=path_output):
            if type(input) == str:
                input = QgsVectorLayer(input, '', 'ogr')
            path_ = os.path.join(path, name + ".gpkg")
            ctc = QgsProject.instance().transformContext()
            QgsVectorFileWriter.writeAsVectorFormatV3(input, path_, ctc, getVectorSaveOptions('GPKG', 'utf-8'))

        # check perimeter
        # f_save_as_gpkg(perimeter, "perimeter")

        # print("extract TBk-stand-map by intersecting perimeter ... ")
        feedback.pushInfo("extract TBk-stand-map by intersecting perimeter ... ")

        # path to original main TBk layer
        path_tbk_main_in = os.path.join(path_tbk_input, tbk_input_file_path)
        # path to extracted main TBb layer
        path_tbk_main_out = os.path.join(path_output, tbk_input_file_path)

        # extract main TBk layer
        param = {
            'INPUT': path_tbk_main_in,
            'PREDICATE': [0], # intersect
            'INTERSECT': perimeter,
            'OUTPUT': path_tbk_main_out
        }
        algoOutput = processing.run("native:extractbylocation", param)
        algoOutput["OUTPUT"]

        if tbk_qgis_proj:
            # print("copy TBk-QGIS-project-file ... ")
            feedback.pushInfo("copy TBk-QGIS-project-file ... ")
            path_tbk_qgis_proj_in = os.path.join(path_tbk_input, tbk_qgis_proj_path)
            path_tbk_qgis_proj_out = os.path.join(path_output, tbk_qgis_proj_path)
            copyfile(path_tbk_qgis_proj_in, path_tbk_qgis_proj_out)

        # extract raster datatsets
        if len(tbk_raster_datasets) > 0:

            # dict for buffered extraction perimeters according to resolution of raster layer to be extracted
            extraction_perimeter_raster = {}

            # something to compare feedback message to and ...
            # ... which is different from feedback message of 1st raster layer to be extracted
            feedback_message = ""

            for i, ds in enumerate(tbk_raster_datasets):
                # if raster layers have a common feedback message, that message is shown only once
                feedback_message_i = tbk_raster_datasets[ds]
                if feedback_message_i != feedback_message:
                    # print(feedback_message_i)
                    feedback.pushInfo(feedback_message_i)
                feedback_message = feedback_message_i # update feedback message for comparison

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
                if ((ds in [mg_10m_path, mg_10m_binary_path] and mg_clip_by_extent) or
                        (ds in [vhm_10m_path, vhm_150cm_path, vhm_detail_path] and vhm_clip_by_extent)):
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

            # something to compare feedback message to and ...
            # ... which is different from feedback message of 1st vector layer to be extracted
            feedback_message = ""

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
                # if vector layers have a common feedback message, that message is shown only once
                feedback_message_i = tbk_vector_datasets[ds]
                if feedback_message_i != feedback_message:
                    # print(feedback_message_i)
                    feedback.pushInfo(feedback_message_i)
                feedback_message = feedback_message_i  # update feedback message for comparison

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

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Extracts all polygons from a TBk stands map intersecting with a perimeter. The extracted stands are saved in a .gpkg having the same name as the .gpkg holding the original stand map. Furthermore, the .gpkg with the extracted stands is placed within the user-defined output folder in a folder inheriting its name from the folder harboring the original .gpkg. Thus, file naming and folder architecture of original TBk-project is cloned.

Extraction of further layers included in the original TBk-project is possible by setting the advanced parameters. Geometries from vector layers are extracted if being fully within the area covering the extracted stands. While raster layers are extracted by a mask, which equates to the area covering the extracted stands buffered with the very raster layer’s pixel resolution. By default, two coniferous raster layers are not extracted by their specific buffer-mask itself but by its extent. This default setting mimics the TBk-preprocessing, which generates coniferous raster layers for the whole extent of the input-perimeter. TBk-preprocessing can also return unmasked VHM-derivates, which is not its default behavior. By ticking the corresponding checkbox <i><b>Clip VHM 10m, VHM 150cm and VHM detail by extent, … </i></b> this alternative outcome of preprocessing can by mimicked.

Copying the TBk-QGIS-project-file is also feasible via advanced parameters.</p></body></html></p>

<h2>Input parameters</h2>
<h3>Perimeter of extraction (polygon(s) and/or mutlipolygon(s)</h3>
<p>Layer of extraction perimeter</p>
<h3>Folder with TBk project to extract from</h3>
<p>Path to folder including a .gpkg-file holding a TBk-stand-map.</p>
<h3>Folder where the extracted material will be stored</h3>
<p>Path to output folder.</p>

<h2>Advanced parameters</h2>
<h3>Relative path to TBk-map-file (.gpkg)</h3>
<p>File name of the TBk stand map kept in the <i><b>Folder with TBk project to extract from</i></b>. By default <i>TBk_Bestandeskarte.gpkg</i>, which is what <b><i>Generate BK</i></b> returns. The default can be replaced by aternatives like <i>TBk_Bestandeskarte_clean.gpkg</i>.</p>

<h3>Copy TBk-QGIS-project-file</h3>
<p>Check box: default True.</p>
<h3>Relative path to TBk-QGIS-project-file (.qgz / .qgs)</h3>
<p>File path relative to <i><b>Folder with TBk project to extract from</i></b>. By default <i>TBk_Project.qgz</i>, which is what <b><i>Generate BK</i></b> returns.</p>

<h3>Degree of cover raster layer</h3>
<p>Check box: default True.</p>
<h3>Relative path to degree of cover raster layer</h3>
<p>File path relative to <b><i>Folder with TBk project to extract from</i></b>. By default <i>dg_layers</i>\<i>dg_layer.tif</i>, which is what <b><i>Generate BK</i></b> returns.</p>

<h3>Degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB)</h3>
<p>Check box: default True.</p>
<h3>Relative path to folder with degree of cover raster layers of single height-ranges (KS, US, MS, OS, UEB)</h3>
<p>Folder path relative to <b><i>Folder with TBk project to extract from</i></b>. By default <i>dg_layers</i>, which is what <b><i>Generate BK</i></b> returns populates with the five DG-layers.</p>

<h3>VHM with 10m resolution, main input to generate TBk-stand-map</h3>
<p>Check box: default True.</p>
<h3>Relative path VHM 10m layer</h3>
<p>File path relative to <b><i>Folder with TBk project to extract from</i></b>. By default ..\<i>VHM_10m.tif</i>, which is where <b><i>Generate BK</i></b> mostly gets this input (preprocessing return) form.</p>

<h3>VHM with 150cm resolution, main input to generate TBk-stand-map</h3>
<p>Check box: default True.</p>
<h3>Relative path VHM 150cm layer</h3>
<p>File path relative to <b><i>Folder with TBk project to extract from</i></b>. By default ..\<i>VHM_150cm.tif</i>, which is where <b><i>Generate BK</i></b> mostly gets this input (preprocessing return) form.</p>

<h3>Detailed VHM raster with original resolution</h3>
<p>Check box: default True.</p>
<h3>Relative path to detailed VHM layer</h3>
<p>File path relative to <b><i>Folder with TBk project to extract from</i></b>. By default ..\<i>VHM_detail.tif</i>, which is where <b><i>Generate BK</i></b> mostly gets this input (preprocessing return) form.</p>

<h3>Clip VHM 10m, VHM 150cm and VHM detail by extent, else by mask</h3>
<p>Check box: default False.</p>

<h3>Coniferous raster / forest mixture degree with 10m resolution</h3>
<p>Check box: default True.</p>
<h3>Relative path to coniferous raster</h3>
<p>File path relative to <b><i>Folder with TBk project to extract from</i></b>. By default ..\<i>MG_10m.tif</i>, which is where <b><i>Generate BK</i></b> mostly gets this input (preprocessing return) form.</p>

<h3>Binary coniferous raster with 10m resolution, used for stand delineation</h3>
<p>Check box: default True.</p>
<h3>Relative path to binary coniferous raster</h3>
<p>File path relative to <b><i>Folder with TBk project to extract from</i></b>. By default ..\<i>MG_10m_binary.tif</i>, which is where <b><i>Generate BK</i></b> mostly gets this input (preprocessing return) form.</p>

<h3>Clip both coniferous raster and binary coniferous raster by extent, else by mask</h3>
<p>Check box: default True.</p>

<h3>Intermediate layers from TBk-proecessing</h3>
<p>Check box: default False. If True extracts all raster (.tif) and vector (.gpkg) layers held in folder with intermediate layers, but not any content held there in subfolders or .cvs-files.</p>
<h3>Relative path to folder with intermediate layers</h3>
<p>Folder path relative to <b><i>Folder with TBk project to extract from</i></b>. By default <i>bk_process</i>, which is what <b><i>Generate BK</i></b> returns populates with intermediate material.</p>

<h3>Local densities within TBk-stands (post-process output)</h3>
<p>Check box: default False. If True extracts all vector layers (.gpkg) held in local densities' folder.</p>
<h3>Relative path to folder with local densities</h3>
<p>Folder path relative to <i><b>Folder with TBk project to extract from</i></b>. By default <i>local_densities</i>, which where <b><i>TBk Postprocess Local Density</i></b> drops its outputs.</p>

<h3>List relative* paths to additional material</h3>
<p>Matrix with 1 columns to list paths relative <i><b>Folder with TBk project to extract from</i></b>. By default no path is listed.
- single vector layers / .gpkg files,
- single raster layers / .tif files or
- folders containing vector and/or raster layers
can be listed.</p>

<h2>Outputs</h2>
<p>Output folder containing extracted material (<i><b>Folder where the extracted material will be stored</i></b> s. above). File naming and achitectur inherited form inputs (s. above).</p>
<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html></p><br><p align="right">Algorithm author: Attilio Benini @ BFH-HAFL (2024)</p></body></html>"""

    def createInstance(self):
        return TBkPostprocessExtractPerimeter()
