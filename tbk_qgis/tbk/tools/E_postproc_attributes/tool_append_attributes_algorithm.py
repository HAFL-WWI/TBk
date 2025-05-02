# todo
import logging
import os

import processing
from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString)
from tbk_qgis.tbk.general.tbk_utilities import ensure_dir
from tbk_qgis.tbk.tools.E_postproc_attributes.tbk_qgis_processing_algorithm_toolsE import TBkProcessingAlgorithmToolE


class TBkAppendStandAttributesAlgorithm(TBkProcessingAlgorithmToolE):
    """
    todo
    """
    # ------- Define Constants -------#
    # Constants used to refer to parameters and outputs.

    # These constants will be used when calling the algorithm from another algorithm,
    # or when calling from the QGIS console.

    # Folder for storing all input files and saving output files
    RESULT_DIR = "result_dir"
    # File storing configuration parameters
    CONFIG_FILE = "config_file"

    # Default log file name
    LOGFILE_NAME = "logfile_name"

    INPUT_TO_ATTRIBUTE = "input_to_attribute"
    OUTPUT_ATTRIBUTED = "output_attributed"

    # Additional parameters
    # Delete temporary files and fields
    DEL_TMP = "del_tmp"

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

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along with some other properties.
        """
        # --- Handle config argument
        # Indicates whether the tool is running in standalone or modularized mode, and adjusts the GUI/behavior if needed.
        is_standalone_context = config.get('is_standalone_context') if config else True

        # --- Parameters

        # Config file containing all parameter key-value pairs
        self.addParameter(QgsProcessingParameterFile(self.CONFIG_FILE,
                                                     'Configuration file to set the algorithm parameters. The bellow '
                                                     'non-optional parameters must still be set but will not be used.',
                                                     extension='toml',
                                                     optional=True))

        # Not needed in a modular context; can use the previous algorithm's output directly
        if is_standalone_context:
            self.addParameter(QgsProcessingParameterFile(self.RESULT_DIR,
                                                         "Directory containing all TBk output folders and files. This "
                                                         "folder must contain the previous generated data",
                                                         behavior=QgsProcessingParameterFile.Folder))

        # Input stand map to be merged
        self.addParameter(
            QgsProcessingParameterFeatureSource(self.INPUT_TO_ATTRIBUTE, "Input layer to join to",
                                                [QgsProcessing.TypeVectorPolygon],
                                                optional=True))
        # Output
        self.addParameter(
            QgsProcessingParameterFileDestination(self.OUTPUT_ATTRIBUTED, "Output",
                                                  "GPKG files (*.gpkg)",
                                                  optional=True))

        # --- Advanced Parameters

        # Fields for Vegetation Zone
        self._add_advanced_parameter(QgsProcessingParameterNumber(self.VEGZONE_DEFAULT, self.tr(
            "Vegetation Zone default (Code). Will be applied if no vegetation zone can be assigned from VegZone layer."
            "\n1 - hyperinsubric, 2/3 - colline /with beech, 4 - submontane, "
            "\n5 - lower montane, 6 - upper montane, 8 - high montane, 9 - sub alpine"
        ), type=QgsProcessingParameterNumber.Integer, defaultValue=2))

        self._add_advanced_parameter(
            QgsProcessingParameterFeatureSource(self.VEGZONE_LAYER, self.tr("Vegetation Zone layer"),
                                                [QgsProcessing.TypeVectorPolygon], optional=True))

        self._add_advanced_parameter(
            QgsProcessingParameterField(self.VEGZONE_LAYER_FIELD, 'Vegetation Zone Code field (in layer)',
                                        type=QgsProcessingParameterField.Numeric,
                                        parentLayerParameterName=self.VEGZONE_LAYER, allowMultiple=False,
                                        defaultValue='Code', optional=True))

        # Fields for Forest Site Category
        self._add_advanced_parameter(
            QgsProcessingParameterString(self.FORESTSITE_DEFAULT, self.tr("Forest Site Category (Code, e.g. 7a)"),
                                         optional=True))

        self._add_advanced_parameter(
            QgsProcessingParameterFeatureSource(self.FORESTSITE_LAYER, self.tr("Forest Site Category layer"),
                                                [QgsProcessing.TypeVectorPolygon], optional=True))

        self._add_advanced_parameter(
            QgsProcessingParameterField(self.FORESTSITE_LAYER_FIELD, 'Forest Site Category field (in layer)',
                                        type=QgsProcessingParameterField.Any,
                                        parentLayerParameterName=self.FORESTSITE_LAYER, allowMultiple=False,
                                        optional=True))

        # Additional parameters
        parameter = QgsProcessingParameterString(self.LOGFILE_NAME, "Log File Name (.log)",
                                                 defaultValue="tbk_processing.log")
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.DEL_TMP, "Delete temporary files and fields",
                                                  defaultValue=True)
        self._add_advanced_parameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        print("--------------------------------------------")
        print("START Appending attributes...")

        # --- Get input parameters
        params = self._extract_context_params(parameters, context)

        # Handle the working root and temp output folders
        # todo: do the same for the other algorithms:
        bk_dir = self._get_bk_output_dir(params.result_dir)
        # todo: use this instead of tbk_result_dir in calculate_dg()
        dg_dir = self._get_dg_output_dir(params.result_dir)
        tmp_output_folder = self._get_tmp_output_path(os.path.join(params.result_dir, 'bk_process'))
        ensure_dir(tmp_output_folder)

        # Set the logger
        self._configure_logging(params.result_dir, params.logfile_name)
        log = logging.getLogger(self.name())

        # Check that the necessary files are provided
        if params.vegZoneLayer and not params.vegZoneLayerField:
            raise QgsProcessingException("vegZoneLayer provided but no vegZoneLayerField for join")

        if params.forestSiteLayer and not params.forestSiteLayerField:
            raise QgsProcessingException("forestSiteLayer provided but no forestSiteLayerField for join")

        stands_file_join = params.input_to_attribute

        # --- Append attributes from join layers
        log.info('Append attributes from join layers')
        # join VegZone if layer is provided
        if params.vegZoneLayer:
            joined_path = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_VegZone1_joined.gpkg")
            renamed_path = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_VegZone2_renamed.gpkg")
            stands_file_join = self.join_and_rename(joined_path,
                                                    renamed_path,
                                                    params.input_to_attribute,
                                                    params.vegZoneLayer,
                                                    params.vegZoneLayerField,
                                                    'VegZone',
                                                    'VegZone_Code')

        # create field VegZone_Code (if not already existent through join) and fill (NULL values) with default
        stands_file_appended = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_VegZone3.gpkg")
        formula = f'if("VegZone_Code","VegZone_Code", {params.vegZoneDefault})'
        processing.run("native:fieldcalculator", {
            'INPUT': stands_file_join,
            'FIELD_NAME': 'VegZone_Code', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
            'FORMULA': formula, 'OUTPUT': stands_file_appended})

        # join forestSite if layer is provided
        if params.forestSiteLayer:
            joined_path = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_ForestSite1_joined.gpkg")
            renamed_path = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_ForestSite2_renamed.gpkg")
            stands_file_join = self.join_and_rename(joined_path,
                                                    renamed_path,
                                                    stands_file_appended,
                                                    params.forestSiteLayer,
                                                    params.forestSiteLayerField,
                                                    'ForestSite',
                                                    'ForestSite')

        if (params.forestSiteDefault is not None) and not (params.forestSiteDefault == ""):
            # create field ForestSite_Code (if not already existent through join) and fill (NULL values) with default
            stands_file_forestSite = os.path.join(tmp_output_folder, "TBk_Bestandeskarte_ForestSite3.gpkg")
            formula = f'if("ForestSite","ForestSite", \'{params.forestSiteDefault}\')'
            processing.run("native:fieldcalculator", {
                'INPUT': stands_file_appended,
                'FIELD_NAME': 'ForestSite', 'FIELD_TYPE': 2, 'FIELD_LENGTH': 80, 'FIELD_PRECISION': 0,
                'FORMULA': formula, 'OUTPUT': stands_file_forestSite})
            stands_file_join = stands_file_forestSite

            # todo: return stands_dg_nh_vegZone
        return {self.OUTPUT_ATTRIBUTED: stands_file_forestSite}

    def join_and_rename(self,
                        joined_path: str,
                        renamed_path: str,
                        input_layer: str,
                        join_layer: str,
                        join_field: str,
                        prefix: str,
                        renamed_field: str) -> str:

        param = {'layer_to_join_attribute_on': input_layer,
                 'attribute_layer': join_layer,
                 'fields_to_join': [join_field], 'joined_attributes_prefix': f"{prefix}_",
                 'output_with_attribute': joined_path}
        processing.run("TBk:Optimized Spatial Join", param)

        # If the field has already the correct name, it is not necessary to rename it
        joined_field = f"{prefix}_{join_field}"
        if joined_field == renamed_field:
            return joined_path

        processing.run("native:renametablefield", {
            'INPUT': joined_path,
            'FIELD': joined_field, 'NEW_NAME': renamed_field,
            'OUTPUT': renamed_path})

        return renamed_path

    def createInstance(self):
        """
        Returns a new algorithm instance
        """
        return TBkAppendStandAttributesAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Append stand attributes'

    #todo
    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('')

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
