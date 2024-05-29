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
        logging.basicConfig(filename=logfile_tmp_path,
                            level=logging.DEBUG,
                            format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                            datefmt='%H:%M:%S'
                            )

        # set up logging to console
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger().addHandler(console)

        # todo: The QgisHandler messages are not displayed in the QGIS log.
        # # set up logging to QGIS feedback
        # qgis_console = QgisHandler(feedback)
        # qgis_console.setLevel(logging.DEBUG)
        # # add the handler to the root logger
        # logging.getLogger().addHandler(console)

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

    def get_inputs(self, parameters, context):
        """
        Get the user inputs from the algorithm context
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
