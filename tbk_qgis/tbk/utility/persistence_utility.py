import importlib
import os

from types import SimpleNamespace
from typing import Optional

import toml
import tomlkit
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
    if toml_file_path:
        toml_template_path = toml_file_path
    else:
        toml_template_path = _DEFAULT_CONFIG_PATH
    toml_data = read_toml_file(toml_template_path)

    # Iterate over the dict and replace the values in the toml template
    for key, value in dictionary.items():
        toml_data[key] = value

    file_path = os.path.join(output_folder_path, file_name)

    try:
        # Writing the file
        with open(file_path, "w") as outfile:
            outfile.write(toml_data.as_string())
    except (FileNotFoundError, PermissionError, OSError):
        print(f'Error writing file: {file_path}')


def read_dict_from_toml_file(file_path: str) -> Optional[SimpleNamespace]:
    """
    Read a dictionary from a TOML file
    """
    toml_document = read_toml_file(file_path)
    if toml_document:
        data = toml_document.unwrap()
        # Convert the TOML data to a namespace object
        return SimpleNamespace(**data)
    return None


def read_toml_file(file_path: str) -> TOMLDocument:
    """
    Read data contained in a TOML file
    """
    try:
        # Attempt to open the TOML file for reading
        with open(file_path, 'r') as toml_file:
            # Parse the TOML file and unwrap it to get a pure python object
            data = tomlkit.parse(toml_file.read())
            # Convert the TOML data to a namespace object
            return data
    except (FileNotFoundError, PermissionError, OSError):
        print(f'Error opening file: {file_path}')
