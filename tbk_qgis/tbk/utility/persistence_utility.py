import os
from typing import Optional
import tomlkit
from PyQt5.QtCore import QVariant
from tomlkit import TOMLDocument

import tbk_qgis

_CONFIG_FILE_NAME = "input_config.toml"
_DEFAULT_CONFIG_PATH = os.path.dirname(tbk_qgis.__file__) + '/' + 'config' + '/' + 'default_input_config.toml'


def write_dict_to_toml_file(toml_file_path: str, output_folder_path: str, dictionary: dict,
                            file_name: str = _CONFIG_FILE_NAME) -> None:
    """
        Write a dictionary to a TOML file.
    """

    # If a TOML file path is given, store the corresponding file to keep the file comments
    toml_template_path = toml_file_path if toml_file_path else _DEFAULT_CONFIG_PATH
    toml_data = read_toml_file(toml_template_path)

    # Iterate over the dict and replace the values in the toml template
    for key, value in dictionary.items():
        # todo: if the config file is not set, the parameter is somehow converted to a QVariant before the algorithm
        #  is processed. This conditional statement solve the issue. Furthermore, if the config file is set,
        #  we still need to set the other parameters.
        #  Solution to investigate: use the preprocessParameters function
        if isinstance(value, QVariant) and value.isNull():
            toml_data[key] = ''
        else:
            toml_data[key] = value
    file_path = os.path.join(output_folder_path, file_name)

    # Writing the file
    with open(file_path, "w") as outfile:
        outfile.write(toml_data.as_string())


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
