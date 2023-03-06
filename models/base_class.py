import json
from app_exceptions.exceptions import *


class BaseClass:
    """Base class for subclasses that use files and json for storing objects."""
    total_objects = None
    filename = ""

    @classmethod
    def read(cls, filename: str) -> dict:
        """
        Read the file and create dict object using json.
        Param filename: Name of the file, str.
        Return: dict.
        """
        try:
            with open(filename) as reader:
                records = json.loads(reader.read())
            return records
        except FileNotFoundError as exc:
            raise InitializeFileError(f"We cannot find file: {cls.filename}. Make sure you initialized files.") from exc

    @classmethod
    def write(cls, records: dict, filename: str) -> None:
        """
        Write to file, converting dict object to string using json.
        Param records: dict object, representing data from the file.
        Param filename: Name of the file, str.
        Return: None.
        """
        try:
            with open(filename, "w") as writer:
                writer.write(json.dumps(records, indent=4))
        except FileNotFoundError as exc:
            raise InitializeFileError(f"We cannot find file: {cls.filename}. Make sure you initialized files.") from exc

    def refresh_base(self) -> None:
        """
        Getting the number of records in a file to generate next ID number.
        :return: None.
        """
        try:
            records = self.read(self.filename)
            self.total_objects = len(records)
        except FileNotFoundError as exc:
            raise InitializeFileError(
                f"We cannot find file: {self.filename}. Make sure you initialized files."
            ) from exc
