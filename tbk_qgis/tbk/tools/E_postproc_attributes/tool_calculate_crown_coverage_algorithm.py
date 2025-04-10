#todo
import logging
import os

from qgis.core import (QgsProcessing,
                       QgsProcessingOutputFile,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterString)
from tbk_qgis.tbk.general.tbk_utilities import ensure_dir
from tbk_qgis.tbk.tools.E_postproc_attributes.calculate_dg import calculate_dg
from tbk_qgis.tbk.tools.E_postproc_attributes.tbk_qgis_processing_algorithm_toolsE import TBkProcessingAlgorithmToolE

class TBkCalculateCrownCoverageAlgorithm(TBkProcessingAlgorithmToolE):
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
    # VHM 150cm to calculate DG
    VHM_150CM = "vhm_150cm"
    # Default log file name
    LOGFILE_NAME = "logfile_name"

    # Input layer used for the calculation
    STANDS_INPUT = "stands_input"
    # Stands output with supplementary crown coverage fields
    OUTPUT_STANDS_WITH_DG = "stands_with_dg"

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

        # VHM 150cm to calculate DG
        self.addParameter(QgsProcessingParameterRasterLayer(self.VHM_150CM,
                                                            "VHM 150cm to calculate DG (.tif)"))

        # Not needed in a modular context; can use the previous algorithm's output directly
        if is_standalone_context:
            # Input stand map to be merged
            self.addParameter(
                QgsProcessingParameterFeatureSource(self.STANDS_INPUT, "Input layer used for the calculation",
                                                    [QgsProcessing.TypeVectorPolygon],
                                                    optional=True))

            self.addParameter(QgsProcessingParameterFile(self.RESULT_DIR,
                                                         "Directory containing all TBk output folders and files. This "
                                                         "folder must contain the previous generated data",
                                                         behavior=QgsProcessingParameterFile.Folder))

            # --- Add output definition, so that they can be used in model designer
            # Stands output with crown coverage fields
            self.addOutput(QgsProcessingOutputFile(self.OUTPUT_STANDS_WITH_DG,
                                                   "Stand Output file with crown coverage fields"))

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
        # --- Get input parameters

        params = self._extract_context_params(parameters, context)

        # Get input layer parameter
        input_for_calcul = params.stands_input

        # Handle the working root and temp output folders
        bk_dir = self._get_bk_output_dir(params.result_dir)
        tmp_output_folder = self._get_tmp_output_path(params.result_dir)
        ensure_dir(tmp_output_folder)

        # Set crown coverage output folder
        dg_dir = self._get_dg_output_dir(params.result_dir)

        # Set the logger
        self._configure_logging(params.result_dir, params.logfile_name)
        log = logging.getLogger('Calculate crown coverage')  # todo: use self.name()?

        # check tif files extension
        self._check_tif_extension(params.vhm_150cm, self.VHM_150CM)

        # --- Calculate DG
        log.info('Starting')
        results = calculate_dg(bk_dir, input_for_calcul, tmp_output_folder,  dg_dir, params.vhm_150cm, del_tmp=params.del_tmp)

        return results

    def createInstance(self):
        """
        Returns a new algorithm instance
        """
        return TBkCalculateCrownCoverageAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '5 Calculate crown coverage'

    #todo
    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('')
