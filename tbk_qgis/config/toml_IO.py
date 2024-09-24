# ######################################################################
# Class for reading and writing custom TOML files.
#
# Note: This class does not fully comply with all TOML syntax (https://toml.io/en/)!
# It currently handles simple key-value pairs (without inline comments) and line comments,
# as seen in the provided default TOML file. Empty lines are ignored.
# The following syntax are partially implemented but not tested: TOML tables,
# multi-line comments, and inline comments.
#
# (C) David Coutrot, HAFL
#######################################################################
from typing import Union, List, Dict, Any, Tuple
from tbk_qgis.config.toml_document import TOMLDocument, TOMLComment, TOMLTable, TOMLKeyValue


class TomlIO:
    """
    Handles the reading and writing of TOML files.
    """

    @staticmethod
    def _parse_toml_line(line: str) -> Tuple[str, Union[str, Tuple[str, Any, str]]]:
        """
        Reads a line from a TOML file, detects its element type, and returns the element type, value, and inline comment
        """
        # Handle line-comments
        if line.startswith("#"):
            return "comment", line
        # Handle table names enclosed into single square brackets
        elif line.startswith("[") and line.endswith("]"):
            return "table", line[1:-1]
        else:
            # Handle lines containing a key-value pair
            parts = line.split("=", 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = comment = None
                value_with_comment = parts[1].strip()

                # Handle inline-comments
                if "#" in value_with_comment:
                    value, comment = value_with_comment.split("#", 1)
                    value = value.strip()
                    comment = f"# {comment.strip()}"
                else:
                    value = value_with_comment.strip()

                return "key_value", (key, value, comment)

        # Throw an error in all other cases.
        raise ValueError(f"Invalid line: {line}")

    @classmethod
    def read_toml(cls, toml_str: str) -> TOMLDocument:
        """
        Reads a TOML string, parses it, and returns a TOMLDocument object.
        """
        document = TOMLDocument()
        current_table = None
        comments = []

        # Iterate over each line in a string.
        for line in toml_str.splitlines():
            line = line.strip()
            # Discard empty lines
            if not line:
                continue

            line_type, content = cls._parse_toml_line(line)

            # Process each line according to its content type.
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
                key, value, inline_comment = content  # inline comment not used yet
                key_value = TOMLKeyValue(key=key, value=value, comments=comments, table=current_table)
                document.key_values[key] = key_value
                comments = []

        return document

    @classmethod
    def write_toml(cls, document: TOMLDocument, file_path: str) -> None:
        """
        Writes a TOML document to a file.
        """
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
        except Exception:
            raise

    @classmethod
    def _write_comments(cls, comments: List[TOMLComment], file):
        """
        Writes TOML comments
        """
        for comment in comments:
            file.write(comment.comment + '\n')

    @classmethod
    def _write_key_values(cls, key_values: Dict[str, TOMLKeyValue], file):
        """
        Writes TOML key-values
        """
        for kv in key_values.values():
            if not kv.table:
                cls._write_key_value(kv, file)

    @classmethod
    def _write_key_value(cls, kv: TOMLKeyValue, file):
        """
        Writes a TOML key-value
        """
        # First, write the comments linked to the key-value pair
        cls._write_comments(kv.comments, file)

        value = kv.value
        if isinstance(value, str):
            if value not in ("true", "false"):
                value = f'"{value}"'

        file.write(f'{kv.key} = {value}\n')


# For testing purpose
if __name__ == "__main__":
    with open('default_input_config.toml', 'r') as toml_file:
        file_content = toml_file.read()

    doc = TomlIO.read_toml(file_content)
    doc["vhm_10m"] = "test"
    doc["max_lh"] = 1
    doc["vMax"] = 1.0
    doc["reclassify_mg_values"] = True

    TomlIO.write_toml(doc, 'output.toml')
