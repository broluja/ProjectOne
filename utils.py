import json
import os
from app_exceptions.exceptions import FileAlreadyCreatedException

import pandas as pd


def mprint(*args, delimiter="*", end="\n", sep="\n") -> None:
    """
    Custom print function with two limit lines
    :param args: Message(s) for printing.
    :param delimiter: delimiter used for limit lines
    :param end: string appended after the last value, default a newline.
    :param sep: string inserted between values, default a new line.
    :return: None.
    """
    if len(args) == 1 and "\n" not in repr(args[0]):
        print(delimiter * 80, f"{args[0]:^80}", delimiter * 80, sep=sep, end=end)
    else:
        print(delimiter * 80, *args, delimiter * 80, sep=sep, end=end)


def init_file(file: str) -> None:
    """
    Initialize file for storing records.
    :param file: str, file name
    :return: None.
    """
    records = {}
    with open(file, "w") as writer:
        writer.write(json.dumps(records, indent=4))


def populate_items(filename: str, item) -> None:
    """
    Initial population of items file.
    :param filename: str
    :param item: class Item, cannot be imported here directly (circular Import)
    :return: None.
    """
    file = pd.read_csv(filename)
    for line in file.itertuples(index=False):
        item(line.item_name, line.price, line.quantity)


def create_excel_file(frame: list, order_id: str) -> None:
    """
    Create Excel file using pandas library.
    :param frame: data frame, list.
    :param order_id: ID of order used for file name.
    :return: None.
    """
    df = pd.DataFrame(frame, columns=["Item ID", "Item Name", "Price", "Quantity", "Total"])
    filename = f"my_order_{order_id}.xlsx"
    if filename in os.listdir():
        raise FileAlreadyCreatedException
    with pd.ExcelWriter(filename) as writer:
        df.to_excel(writer, sheet_name="my_order", index=False)
