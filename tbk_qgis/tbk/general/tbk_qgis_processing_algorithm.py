# #####################################################################
# Base class for TBk core sub-algorithms designed for inheritance to minimize code repetition across child algorithms,
# allowing them to leverage shared functions efficiently.
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
from tbk_qgis.tbk.general.persistence_utility import read_dict_from_toml_file
from tbk_qgis.tbk.general.tbk_utilities import dict_diff, ensure_dir


class TBkProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    A base class for the core TBk algorithms. It can be inherited, so that each child algorithm can use its functions.
    """

    def prepare(self, parameters, context, feedback):
        """
        todo
        """
        # get configuration file path
        config_path = str(self.parameterAsFile(parameters, self.CONFIG_FILE, context))
        if config_path:
            # Set input parameters from config file
            try:
                config = read_dict_from_toml_file(config_path)

                # compare config file parameters and tool parameters
                config_removed, config_added, config_changed = dict_diff(parameters, config)

                # apply config_file to parameters (overwrite values in parameters if they have an entry in
                # config_file values)
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
        return True

    @staticmethod
    def _get_result_dir(output_root):
        """
        Return the output directory path
        """
        # Set up directory with timestamp in output_root
        time = datetime.now().strftime("%Y%m%d-%H%M")
        result_directory = os.path.join(output_root, time)

        ensure_dir(result_directory)

        return result_directory

    @staticmethod
    def _get_bk_output_dir(result_directory):
        """
        Return the output folder for the data related to stand map processing
        """
        bk_output = os.path.join(result_directory, 'bk_process')
        ensure_dir(bk_output)

        return bk_output

    @staticmethod
    def _get_dg_output_dir(result_directory):
        """
        Return the output folder for the data related to crown coverage processing
        """
        dg_output = os.path.join(result_directory, 'dg_layers')
        ensure_dir(dg_output)

        return dg_output

    @staticmethod
    def _get_tmp_output_path(working_root):
        """
            Return the temporary output folder path
        """
        tmp_output_path = os.path.join(working_root, "tmp")
        return tmp_output_path

    @staticmethod
    def _configure_logging(output_folder_path, logfile_name):
        """
        Configure logging
        """
        # The output folder must exist
        logfile_tmp_path = str(os.path.join(output_folder_path, logfile_name))

        # Get the root logger
        logger = logging.getLogger()

        # Check if the logger already has handlers. If it does, return to avoid duplicated log messages
        if logger.hasHandlers():
            return

        # Set up logging to file
        log_format = '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
        date_format = '%H:%M:%S'
        file_handler_formatter = logging.Formatter(log_format, date_format)
        # The log is appended to the existing log or a new file is created if file does not exist (mode = 'a')
        file_handler = logging.FileHandler(logfile_tmp_path, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_handler_formatter)

        # Set up logging to console
        console_formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(console_formatter)

        # Create logger and add the handlers to it
        logger.setLevel(logging.DEBUG)
        logger.addHandler(console)
        logger.addHandler(file_handler)

        # todo: The QgisHandler messages are not displayed in the QGIS log.
        # # set up logging to QGIS feedback
        # qgis_console = QgisHandler(feedback)
        # qgis_console.setLevel(logging.DEBUG)
        # # add the handler to the root logger
        # logging.getLogger().addHandler(console)

    @staticmethod
    def _check_tif_extension(file, input_name):
        """
        Check if the file has a .tiff/tif extension.
        """
        if not file.endswith(('.tiff', '.tif')):
            raise QgsProcessingException(f"{input_name} must be a TIFF file")

    def _add_advanced_parameter(self, parameter):
        """
        Add an advanced parameter
        """
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced)
        return self.addParameter(parameter)

    def _add_hidden_parameter(self, parameter):
        """
        Add a hidden parameter
        """
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.Flag.FlagHidden)
        return self.addParameter(parameter)

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
        return 'TBk core'

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'tbkcore'
