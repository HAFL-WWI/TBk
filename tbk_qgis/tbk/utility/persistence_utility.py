import os
import traceback
from typing import Optional
import tomlkit
from PyQt5.QtCore import QVariant
from qgis.core import QgsProcessingAlgorithm, QgsProcessingContext
from tomlkit import TOMLDocument

import tbk_qgis

_CONFIG_FILE_NAME = "input_config.toml"
_DEFAULT_CONFIG_PATH = os.path.dirname(tbk_qgis.__file__) + '/' + 'config' + '/' + 'default_input_config.toml'


# The writing relies for the moment on an existing toml file. It implies that the Toml keys correspond to the algorithm
# parameter names. If not the writen file will contain the old and new key-value pair.
def write_dict_to_toml_file(toml_file_path: str,
                            output_folder_path: str,
                            dictionary: dict,
                            file_name: str = _CONFIG_FILE_NAME) -> None:
    """
        Write a dictionary to a TOML file.
    """

    # If a TOML file path is given, use it as template. Use otherwise the default toml file as template
    toml_template_path = toml_file_path if toml_file_path else _DEFAULT_CONFIG_PATH
    toml_data = read_toml_file(toml_template_path)

    # Iterate over the dict and replace the values in the toml template
    for key, value in dictionary.items():
        # todo: if the config file is not set, the parameter is somehow converted to a MULL QVariant before
        #  the algorithm is processed. This conditional statement solves the issue. Furthermore, if the config file
        #  is set, we still need to set the other parameters.
        #  Solution to investigate: use the preprocessParameters function

        # Handle NULL and None values since they are not accepted in TOML syntax
        if (isinstance(value, QVariant) and value.isNull()) or value is None:
            toml_data[key] = ''
        else:
            try:
                toml_data[key] = value
            except Exception:
                print(f'An error occurred when writing the toml file because of an Null or None value:')
                traceback.print_exc()
                # Re-raise the exception in order to inform the user
                raise

    file_path = os.path.join(output_folder_path, file_name)

    # Writing the file
    with open(file_path, "w") as outfile:
        outfile.write(toml_data.as_string())


# It is assumed that all the used algorithm parameter are set in the toml config file
def read_dict_from_toml_file(file_path: str) -> Optional[dict]:
    """
    Read a dictionary from a TOML file
    """
    toml_document = read_toml_file(file_path)
    if toml_document:
        data = toml_document.unwrap()
        return data


def read_toml_file(file_path: str) -> Optional[TOMLDocument]:
    """
    Read data contained in a TOML file
    """
    if file_path:
        # Attempt to open the TOML file for reading
        with open(file_path, 'r') as toml_file:
            # Parse the TOML file and unwrap it to get a pure python object
            data = tomlkit.parse(toml_file.read())
            return data


def to_params_with_layer_source(instance: QgsProcessingAlgorithm,
                                parameters: dict,
                                context:
                                QgsProcessingContext) -> dict:
    """
    Replace the layer parameter values with their source path
    """
    params = {}
    for key, value in parameters.items():
        params[key] = value

        if isinstance(value, str):
            param_as_layer = instance.parameterAsLayer(params, key, context)
            # Parameter is a layer if not None
            if param_as_layer is not None:
                # Use the layer source path
                params[key] = param_as_layer.source()

    return params
