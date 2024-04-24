import json
import os

_CONFIG_FILE_NAME = "input_config.json"


def write_dict_to_json_file(output_folder_path: str, dictionary: dict, file_name: str = _CONFIG_FILE_NAME) -> None:
    # Serializing json
    parameters_string = json.dumps(dictionary, indent=4)

    file_path = os.path.join(output_folder_path, file_name)

    # Writing the parameters to the tbk result folder
    with open(file_path, "w") as outfile:
        outfile.write(parameters_string)


def read_dict_from_json_file(file_path: str) -> dict:
    if os.path.exists(file_path):
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    else:
        return {}
