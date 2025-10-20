# Standard imports
import numpy as np
import re
from datetime import datetime
import os
from typing import Any
import shutil
import pyodbc
import pandas as pd

from APgui import ApGui
import APDatabase
from payables.nacha.NachaConstructor import NachaConstructor
from payables.nacha.NachaFile import NachaFile
from wires import PayablesWires


def cls():
    """Clears the terminal screen."""

    os.system("cls")


def check_date(date: str):
    """Check that date matches YYYY-MM-DD format"""

    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", date)

    if match:
        if (
            int(match.group(1)) in range(2020, 2040)
            and int(match.group(2)) in range(1, 13)
            and int(match.group(3)) in range(1, 32)
        ):
            return True
    return False


def set_type(obj: Any, dest_type: str) -> Any:
    """Allows for programmatic type setting."""

    if dest_type == "str":
        return str(obj)
    elif dest_type == "int":
        return int(obj)
    elif dest_type == "float":
        return float(obj)
    elif dest_type == "float64":
        return np.float64(obj)
    elif dest_type == "bool":
        return bool(obj)
    else:
        raise TypeError(f"Unprogrammed type: {dest_type}")


def debug(text: str) -> None:
    """Outputs text to a log file."""

    with open("debug.log", "+a") as file:
        file.write(text)


def string_to_int(string: str) -> int:
    """Converts a string to an integer based on its unicode value."""

    sum = 0
    for char in string:
        sum += ord(char)
    return sum


def is_blank_list(data: list) -> bool:
    """Checks if a list is blank or not."""

    no_data = True
    i = 0
    while no_data and i in range(len(data)):
        if data[i]:
            no_data = False
        i += 1
    return no_data


def str_list_to_int(n: list[str]) -> list[int]:
    """Converts a list of strings to a list of integers"""

    n_copy = n.copy()
    list_len = len(n)
    for i in range(list_len):
        val = n[i]
        if isinstance(val, int) or isinstance(val, np.float64):
            continue

        str_as_int = string_to_int(n[i])
        n_copy[i] = str_as_int
    return n_copy


def get_valid_input(prompt: str, pattern: str) -> str:
    """Returns a user input string fitting the pattern given."""

    while True:
        val = input(prompt)
        if re.match(pattern, val):
            return val
        else:
            print(f"Bad input! Must match pattern '{pattern}'")
            input("Enter to continue")
            for i in range(4):
                print("\x1b[2K", end="", flush=True)
                print("\x1b[A", end="", flush=True)


def ui_get_date(dt: bool = True) -> datetime | tuple[int]:
    """Gets date from user. Returns datetime object if dt == True."""

    year = int(get_valid_input("Year:  ", r"\d{4}"))
    month = int(get_valid_input("Month: ", r"\d{1,2}"))
    day = int(get_valid_input("Day:   ", r"\d{1,2}"))
    vd_dt = datetime(year, month, day)
    vd_str = vd_dt.strftime("%y%m%d")
    if dt:
        return vd_dt
    else:
        return (year, month, day)


def pad_string(string: str, pad_len: int, char: str = " ") -> str:
    """Pad a string to a given length with char

    Args:
        string (str): string to pad
        pad_len (int): length to pad to
        char (str, optional): char to pad with. Defaults to " " (space).

    Returns:
        str: padded string
    """
    pad_len = pad_len - len(string)
    if pad_len < 0:
        return string[0 : (pad_len - 1)]
    elif pad_len > 0:
        pad = "".join([char for i in range(pad_len)])
        padded_string = "".join([string, pad])
        return padded_string
    else:
        return string


def print_header(text: str, border_char: str = "#") -> None:
    border_len = len(text) + 4
    border = border_char * border_len
    header = "".join([border, "\n", "# ", text, " #\n", border])
    print(header)


def preserve_downloads() -> None:
    """Preserves downloads contents by moving to temp folder"""

    try:
        os.mkdir("/".join([os.environ["HOMEPATH"], ".tempdownloads"]))
    except FileExistsError:
        pass

    move_all_files(
        "/".join([os.environ["HOMEPATH"], "Downloads"]),
        "/".join([os.environ["HOMEPATH"], ".tempdownloads/"]),
    )


def restore_downloads() -> None:
    """Restores downloads from temp folder"""

    move_all_files(
        "/".join([os.environ["HOMEPATH"], ".tempdownloads/"]),
        "/".join([os.environ["HOMEPATH"], "Downloads"]),
    )
    shutil.rmtree("/".join([os.environ["HOMEPATH"], ".tempdownloads/"]))


def move_all_files(source: str, dest: str) -> None:
    """Moves all files from a source folder to a destination folder."""

    files = os.listdir(source)
    for file in files:
        shutil.move(src=source + f"/{file}", dst=dest + f"/{file}")


def get_input_index(col: str) -> int:
    """Gets the index of the prompt corresponding to the desired column
    header."""

    with_stub = col + ":"
    return ApGui.invoice_prompts.index(with_stub)


def fix_cc_input(inputs: list[str | int]) -> None:
    """Standardizes cc response to 'y' or ''."""

    cc_index = get_input_index("Credit card")
    cc_input = inputs[cc_index]
    inputs[cc_index] = swap_cc_input(cc_input)


def swap_cc_input(cc_val: str) -> str:
    """Returns 'y' if user response was 'y', else returns ''"""

    new_val = ""
    if cc_val == "y":
        new_val = cc_val
    return new_val


def make_nacha_files(
    value_date: str, con: pyodbc.Connection, debug: bool = False
) -> None:
    data = APDatabase.get_pmt_file_data(pmt_type="ACH", con=con)
    file_constructor = NachaConstructor(data, value_date, debug)
    files = file_constructor.main()
    for i in files:
        write_payment_file(i, value_date)


def write_payment_file(company_data: NachaFile, value_date: str) -> None:
    """Writes NACHA files to Downloads on disk"""

    with open(
        file="/".join(
            [
                os.environ["HOMEPATH"].replace("\\", "/"),
                "Downloads",
                f"{value_date}_ACHS_{company_data.company}.txt",
            ]
        ),
        mode="w",
    ) as file:
        file.write(company_data.__str__())


def make_wire_pmt_files(value_date: datetime, con: pyodbc.Connection) -> None:
    wire_data = APDatabase.get_pmt_file_data(pmt_type="Wire", con=con)
    PayablesWires.os_interface_wire_wrapper(wire_data, valuedate=value_date)
