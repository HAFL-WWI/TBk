import json
import os
from types import SimpleNamespace
from typing import Any

_CONFIG_FILE_NAME = "input_config.json"


# todo: make use of a toml config file?
def write_dict_to_json_file(output_folder_path: str, dictionary: dict, file_name: str = _CONFIG_FILE_NAME) -> None:
    """
        Write a dictionary to a JSON file.
    """
    # Serializing json with indentation for readability
    parameters_string = json.dumps(dictionary, indent=4)

    file_path = os.path.join(output_folder_path, file_name)

    # Writing the file
    with open(file_path, "w") as outfile:
        outfile.write(parameters_string)


def read_dict_from_json_file(file_path: str) -> SimpleNamespace:
    """
    Read a dictionary from a JSON file.
    """
    try:
        # Attempt to open the JSON file for reading
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            # Convert the JSON data to a namespace object
            return SimpleNamespace(**data)
    except FileNotFoundError:
        print(f'file {file_path} not found')
