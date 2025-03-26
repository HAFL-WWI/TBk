# todo
import logging
import os

from qgis.core import (QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessing,
                       QgsProcessingParameterString)
from tbk_qgis.tbk.general.tbk_utilities import ensure_dir
from tbk_qgis.tbk.tools.D_postproc_geom.clip_to_perimeter import clip_to_perimeter, eliminate_gaps
from tbk_qgis.tbk.tools.D_postproc_geom.tbk_qgis_processing_algorithm_toolsD import TBkProcessingAlgorithmToolD


# todo: split in 2 algorithms?
class TBkClipToPerimeterAndEliminateGapsAlgorithm(TBkProcessingAlgorithmToolD):
    """
    todo
    """
    # ------- Define Constants -------#
    # Constants used to refer to parameters and outputs.

    # These constants will be used when calling the algorithm from another algorithm,
    # or when calling from the QGIS console.

    # Folder for storing all input files and saving output files
    WORKING_ROOT = "working_root"
    # File storing configuration parameters
    CONFIG_FILE = "config_file"
    # Perimeter shapefile to clip final result
    PERIMETER = "perimeter"
    # Default log file name
    LOGFILE_NAME = "logfile_name"

    # Input layer to process
    INPUT_TO_CLIP = "input_to_clip"
    # Processed output layer
    OUTPUT_CLIPPED = "output_clipped"

    # Additional parameters
    # Delete temporary files and fields
    DEL_TMP = "del_tmp"

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

        # --- Main parameters

        # Not needed in a modular context; can use the previous algorithm's output directly
        if is_standalone_context:
            self.addParameter(QgsProcessingParameterFile(self.WORKING_ROOT,
                                                         "Working root folder. This folder must contain the outputs "
                                                         "from previous steps.",
                                                         behavior=QgsProcessingParameterFile.Folder))

            # Input stand map to be merged
            self.addParameter(
                QgsProcessingParameterFeatureSource(self.INPUT_TO_CLIP, "Input layer to be clipped",
                                                    [QgsProcessing.TypeVectorPolygon],
                                                    optional=True))

            # Add the parameter only if running as a standalone tool to avoid multiple outputs in modularized mode.
            self.addParameter(
                QgsProcessingParameterFileDestination(self.OUTPUT_CLIPPED, "Clip and Eliminate Output (GeoPackage)",
                                                      "GPKG files (*.gpkg)",
                                                      optional=True))

        # Perimeter shapefile to clip final result
        self.addParameter(
            QgsProcessingParameterFeatureSource(self.PERIMETER, "Perimeter shapefile to clip final result",
                                                [QgsProcessing.TypeVectorPolygon]))

        # --- Advanced Parameters

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
        # Adapt the parameters if modular mode
        if "invoker_params" in parameters:
            input_name = parameters['invoker_params']["input_to_clip_name"]  # name of the parameter to use as input

            output_file_name = parameters['invoker_params']["output_name"] + ".gpkg"
            output_simplified_path = os.path.join(parameters["working_root"], output_file_name)

            invoker_params = {
                "input_to_clip": parameters[input_name],
                "output_clipped": output_simplified_path
            }
            parameters.update(invoker_params)

        # --- Get input parameters

        params = self._extract_context_params(parameters, context)

        # Handle the working root and temp output folders
        working_root = params.working_root
        ensure_dir(working_root)
        tmp_output_folder = self._get_tmp_output_path(params.working_root)
        ensure_dir(tmp_output_folder)

        # Set the logger
        self._configure_logging(params.working_root, params.logfile_name)
        log = logging.getLogger('Clip to perimeter and eliminate gaps')  # todo: use self.name()?

        # ---  Clip
        log.info('Starting')
        # run clip function
        tmp_clipped_file_path = clip_to_perimeter(working_root, params.input_to_clip,
                                      os.path.join(tmp_output_folder, "stands_clip_tmp.gpkg"),
                                      tmp_output_folder, params.perimeter, del_tmp=params.del_tmp)

        # run gaps function
        output_clipped = eliminate_gaps(working_root, tmp_clipped_file_path, params.output_clipped, tmp_output_folder,
                                    params.perimeter, del_tmp=params.del_tmp)

        return {'output_clipped': output_clipped}

    def createInstance(self):
        """
        Returns a new algorithm instance
        """
        return TBkClipToPerimeterAndEliminateGapsAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '4 Clip to perimeter and eliminate gaps'

    # todo
    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('')
