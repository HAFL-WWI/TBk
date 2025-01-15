#######################################################################
# Custom TOML document class.
#
# This class does not fully comply with all TOML syntax (https://toml.io/en/).
# It is designed as a model class with custom getter and setter rules for TOML documents.
#
# (C) David Coutrot, HAFL
#######################################################################
from dataclasses import dataclass, field
from typing import Union, List, Any, Tuple, Dict


@dataclass
class TOMLComment:
    """
    A comment
    """
    comment: str


@dataclass
class TOMLKeyValue:
    """
    This class represents a key-value pair that can include comments (only tested with single-line comments)
    and be associated with a TOML table (association not tested).
    The value can be of type string, boolean, integer, or float.
    """

    def __init__(self,
                 key: str,
                 value: Union[str, int, float, bool],
                 comments: List['TOMLComment'] = None,
                 table: str = ""):
        self.key = key
        self._value = value
        self.comments = comments if comments is not None else []
        self.table = table
        self.__post_init__()

    def __post_init__(self):
        self._value = self._check_value_to_add(self._value)

    # The property decorator is used to enable the implementation of a custom setter.
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = self._check_value_to_edit(new_value)

    @staticmethod
    def _check_value_to_edit(value):
        """
        Ensure that the value to be edited has the correct type.
        TOML requires lower case booleans, so these have to be ensured explicitely.
        Natively they would print with capital first letter.
        """
        # Convert a Python boolean to a TOML boolean (without uppercase)
        if isinstance(value, bool):
            value = str(value).lower()
        return value

    @staticmethod
    def _check_value_to_add(value):
        """
        Ensure that the value to be added has the correct type.
        """

        # Check if value is string for parsing, otherwise pass unchanged value.
        if isinstance(value, str):
            # If the string is surrounded by double quotes or single quotes, remove them.
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            # Handle boolean values ('true' or 'false', case insensitive).
            elif value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            # Check if the value is of integer type.
            elif value.isdigit():
                value = int(value)
            # Check if the value is of float type.
            elif '.' in value and all(part.isdigit() for part in value.split('.')):
                value = float(value)

        return value

@dataclass
class TOMLTable:
    """
    A TOML table
    """
    name: str
    comments: List[TOMLComment] = field(default_factory=list)


@dataclass
class TOMLDocument:
    """
    A TOML Document. The document contains a collection of TOML key-value pairs and TOML tables.
    """
    key_values: Dict[str, TOMLKeyValue] = field(default_factory=dict)
    tables: Dict[str, TOMLTable] = field(default_factory=dict)

    def __setitem__(self, key: str, value: Any):
        """
        Allows dictionary-style item assignment for easy key-value modification.
        If the key exists, updates the value. If it doesn't exist, creates a new TOMLKeyValue.
        """
        table_name, key_name = self._split_key(key)
        if key_name in self.key_values:
            self.key_values[key_name].value = value

    def __getitem__(self, key: str) -> Any:
        """
        Allows dictionary-style item access for easy key-value retrieval.
        """
        table_name, key_name = self._split_key(key)
        if key_name in self.key_values:
            return self.key_values[key_name].value
        else:
            raise KeyError(f'Key "{key}" not found in the toml document.')

    # This method has not been tested with TOML dotted key notation.
    @staticmethod
    def _split_key(key: str) -> Tuple[str, str]:
        """
        Splits the key into table_name and key_name.
        """
        if '.' in key:
            table_name, key_name = key.split('.', 1)
        else:
            table_name = ""
            key_name = key
        return table_name, key_name

    # Not used yet, but it may be necessary for handling other TOML configurations, such as those for logging.
    # def get_key_value(self, key: str) -> Union[TOMLKeyValue, None]:
    #     """
    #     Retrieves the TOMLKeyValue object corresponding to the given key.
    #     """
    #     table_name, key_name = self._split_key(key)
    #     return self.key_values.get(key_name)

    def extract_key_values(self) -> Dict[str, Any]:
        """
        Extracts all key-value pairs from the TOMLDocument.
        """
        result = {}
        for key, key_value in self.key_values.items():
            result[key] = key_value.value
        return result
