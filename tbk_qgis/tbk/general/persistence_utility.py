import os
from pathlib import Path
from typing import Optional
import tbk_qgis
from tbk_qgis.config.toml_IO import TomlIO, TOMLDocument

# Since a custom and partial TOML parser is implemented, the default writing format is TXT to reduce the risk of
# using non-implemented TOML features.
_CONFIG_FILE_NAME = "input_config.txt"
_DEFAULT_CONFIG_PATH: str = os.path.join(os.path.dirname(tbk_qgis.__file__), 'config', 'default_input_config.toml')


# The writing relies for the moment on an existing toml file. It implies that the Toml keys correspond to the
# algorithm parameter names. If not the writen file will contain the old and new key-value pair.
def write_dict_to_toml_file(dictionary: dict,
                            output_folder_path: str,
                            toml_template_path: str = _DEFAULT_CONFIG_PATH,
                            file_name: str = _CONFIG_FILE_NAME) -> None:
    """
        Write a dictionary to a TOML file.
        If a TOML file path is given, use it as template. Use otherwise the default toml file as template
    """
    document = read_toml_file(toml_template_path)

    # todo: [Hannes: I am unsure whether this comment (from David)
    #  is unnecessary after the rework of the TOML file handling done on the other branch.
    #  needs to be revised:
    #  for loop not needed anymore with the modularize core tbk algorithm. This implementation can be
    #  adapted after the legacy algorithm has been deleted and the prepare algorithms adapted:
    #  It can probably be replaced with toml_data = dictionary
    # Iterate over the dict and replace the values in the toml template
    for key, value in dictionary.items():
        document[key] = value

    file_path = os.path.join(output_folder_path, file_name)

    # Writing the file
    TomlIO.write_toml(document, file_path)


# It is assumed that all the used algorithm parameter are set in the toml config file
def read_dict_from_toml_file(file_path: str) -> Optional[dict]:
    """
    Read a dictionary from a TOML file
    """
    toml_document = read_toml_file(file_path)
    if toml_document:
        data = toml_document.extract_key_values()
        return data


def read_toml_file(file_path: str) -> Optional[TOMLDocument]:
    """
    Read data contained in a TOML file
    """
    toml = Path(file_path).read_text()
    document = TomlIO.read_toml(toml)
    return document
