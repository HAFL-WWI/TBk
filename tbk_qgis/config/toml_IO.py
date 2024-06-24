from typing import Union, List, Dict, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class TOMLComment:
    comment: str


@dataclass
class TOMLKeyValue:
    key: str
    _value: Union[str, int, float, bool]  # Use _value as the private attribute to store the value
    comments: List['TOMLComment'] = field(default_factory=list)
    table: str = ""

    def __init__(self, key: str, value: Union[str, int, float, bool], comments: List['TOMLComment'] = None,
                 table: str = ""):
        self.key = key
        self._value = value
        self.comments = comments if comments is not None else []
        self.table = table
        self.__post_init__()

    def __post_init__(self):
        # Ensure value is the correct type
        self._value = self._convert_value(self._value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = self._convert_value(new_value)

    @staticmethod
    def _convert_value(value):
        if not value:
            return ''

        if isinstance(value, bool):
            return str(value).lower()

        if isinstance(value, str):
            if value.lower() in ("true", "false"):
                return value

            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            if value.isdigit():  # Check if value is an integer
                value = int(value)
            elif '.' in value and all(part.isdigit() for part in value.split('.')):  # Check if value is a float
                value = float(value)

        return value


@dataclass
class TOMLTable:
    name: str
    comments: List[TOMLComment] = field(default_factory=list)


@dataclass
class TOMLDocument:
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
            raise KeyError(f'Key "{key}" not found in the document.')

    def _split_key(self, key: str) -> Tuple[str, str]:
        """
        Splits the key into table_name and key_name.
        """
        if '.' in key:
            table_name, key_name = key.split('.', 1)
        else:
            table_name = ""
            key_name = key
        return table_name, key_name

    def get_key_value(self, key: str) -> Union[TOMLKeyValue, None]:
        """
        Retrieves the TOMLKeyValue object corresponding to the given key.
        """
        table_name, key_name = self._split_key(key)
        return self.key_values.get(key_name)

    def extract_key_values(self) -> Dict[str, Any]:
        """
        Extracts all key-value pairs from the TOMLDocument.
        """
        result = {}
        for key, key_value in self.key_values.items():
            result[key] = key_value.value
        return result


@dataclass
class TomlIO:
    @classmethod
    def _parse_toml_line(cls, line: str) -> Tuple[str, Union[str, Tuple[str, Any, str]]]:
        """
        Reads a TOML line, detect which element type it is and return the element type and values.
        """
        if line.startswith("#"):
            return "comment", line
        elif line.startswith("[") and line.endswith("]"):
            return "table", line[1:-1]
        else:
            parts = line.split("=", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = comment = None
                value_with_comment = parts[1].strip()

                if "#" in value_with_comment:
                    value, comment = value_with_comment.split("#", 1)
                    value = value.strip()
                    comment = f"# {comment.strip()}"
                else:
                    value = value_with_comment.strip()

                return "key_value", (key, value, comment)
            else:
                raise ValueError(f"Invalid line: {line}")

    @classmethod
    def toml_to_json(cls, toml_str: str) -> TOMLDocument:
        document = TOMLDocument()
        current_table = None
        comments = []

        for line in toml_str.splitlines():
            line = line.strip()
            if not line:
                continue

            line_type, content = cls._parse_toml_line(line)

            if line_type == "comment":
                comments.append(TOMLComment(content))
            elif line_type == "table":
                table_name = content
                if table_name not in document.tables:
                    document.tables[table_name] = TOMLTable(name=table_name)
                current_table = table_name

                if comments:
                    document.tables[table_name].comments.extend(comments)
                    comments = []
            elif line_type == "key_value":
                key, value, comment = content
                key_value = TOMLKeyValue(key=key, value=value, comments=comments,
                                         table=current_table)
                document.key_values[key] = key_value
                comments = []

        return document

    @classmethod
    def to_toml(cls, document: TOMLDocument, file_path: str):
        try:
            with open(file_path, 'w') as file:
                cls._write_key_values(document.key_values, file)
                for table_name, table in document.tables.items():
                    cls._write_comments(table.comments, file)
                    file.write(f'[{table_name}]\n')
                    for kv in document.key_values.values():
                        if kv.table == table_name:
                            cls._write_key_value(kv, file)
                    file.write('\n')
        except Exception as e:
            raise

    @classmethod
    def _write_comments(cls, comments: List[TOMLComment], file):
        for comment in comments:
            file.write(comment.comment + '\n')

    @classmethod
    def _write_key_values(cls, key_values: Dict[str, TOMLKeyValue], file):
        for kv in key_values.values():
            if not kv.table:
                cls._write_key_value(kv, file)

    @classmethod
    def _write_key_value(cls, kv: TOMLKeyValue, file):
        cls._write_comments(kv.comments, file)
        # Ensure that empty strings are handled properly when writing out to TOML
        value = kv.value
        if isinstance(value, str):
            if value not in ("true", "false"):
                value = f'"{value}"'
        file.write(f'{kv.key} = {value}\n')


# For testing purpose
if __name__ == "__main__":
    with open('default_input_config.toml', 'r') as toml_file:
        file_content = toml_file.read()

    doc = TomlIO.toml_to_json(file_content)
    print(doc)
    doc["vhm_10m"] = "test"
    doc["max_lh"] = 1
    doc["vMax"] = 1.0
    doc["reclassify_mg_values"] = True
    print(doc)

    TomlIO.to_toml(doc, 'output.toml')
