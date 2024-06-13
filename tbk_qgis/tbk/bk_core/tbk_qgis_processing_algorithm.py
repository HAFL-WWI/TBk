# #####################################################################
# Base class for the core TBk algorithms. It is
# aimed be inherited to reduce code repetition in each child algorithm can use its functions.
# 30.05.2024
# (C) Dominique Weber, Christoph Schaller, David Coutrot, HAFL
# #####################################################################

import logging
import os
from datetime import datetime
from types import SimpleNamespace
from qgis.core import (QgsProcessingAlgorithm,
                       QgsProcessingParameterDefinition,
                       QgsProcessingException)
from tbk_qgis.tbk.utility.persistence_utility import read_dict_from_toml_file


class TBkProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    A base class for the core TBk algorithms. It can be inherited, so that each child algorithm can use its functions.
    """

    @staticmethod
    def get_working_root_path(output_root):
        """
        Return the working root folder path
        """
        # Set up directory with timestamp in working_root
        output_directory = datetime.now().strftime("%Y%m%d-%H%M")
        working_root = os.path.join(output_root, output_directory, 'bk_process')

        return working_root

    @staticmethod
    def get_tmp_output_path(working_root):
        """
            Return the temporary output folder path
        """
        tmp_output_path = os.path.join(working_root, "tmp")
        return tmp_output_path

    @staticmethod
    def configure_logging(output_folder_path, logfile_name):
        """
        Configure logging
        """
        # the output folder must exist
        logfile_tmp_path = str(os.path.join(output_folder_path, logfile_name))

        # set up logging to file
        file_handler_formatter = logging.Formatter('[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s', '%H:%M:%S')
        # The log is appended to the existing log or a new file is created if file does not exist (mode = 'a')
        file_handler = logging.FileHandler(logfile_tmp_path, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_handler_formatter)

        # set up logging to console
        console_formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(console_formatter)

        # create logger and the handler to the logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(console)
        logger.addHandler(file_handler)

        # todo: The QgisHandler messages are not displayed in the QGIS log.
        # # set up logging to QGIS feedback
        # qgis_console = QgisHandler(feedback)
        # qgis_console.setLevel(logging.DEBUG)
        # # add the handler to the root logger
        # logging.getLogger().addHandler(console)

        return logger

    @staticmethod
    def check_tif_extension(file, input_name):
        """
        Check if the file has a .tiff/tif extension.
        """
        if not file.endswith(('.tiff', '.tif')):
            raise QgsProcessingException(f"{input_name} must be a TIFF file")

    def add_advanced_parameter(self, parameter):
        """
        Add an advanced parameter
        """
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        return self.addParameter(parameter)

    def add_hidden_parameter(self, parameter):
        """
        Add a hidden parameter
        """
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagHidden)
        return self.addParameter(parameter)

    def _get_input_or_config_params(self, parameters, context):
        inputs_params = self._extract_context_params(parameters, context)
        used_params = inputs_params
        config_path = used_params.config_file
        try:
            config_params_dict = read_dict_from_toml_file(config_path)
            if config_params_dict:
                used_params = SimpleNamespace(**config_params_dict)
        except FileNotFoundError:
            raise QgsProcessingException(f"The configuration file was not found at this location: {config_path}")

        return inputs_params

    def _extract_context_params(self, parameters, context):
        """
        Get the user inputs from the algorithm context. The parameters dict contains layer in-memory values but not
        their source path. This function allows to get usable parameters (i.e. with layer source path).
        """
        inputs_dict = self.asMap(parameters, context)['inputs']
        return SimpleNamespace(**inputs_dict)

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.name()

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
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
