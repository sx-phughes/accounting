# Standard imports
import numpy as np
import re
from datetime import datetime
import os
from typing import Any
import shutil
import pyodbc
import pandas as pd
from collections import Counter
from copy import deepcopy

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


def print_table_horiz_line(line_len):
    print("+", "-" * (line_len + 2), "+", sep="")


def print_to_ascii_table(*lines: str, total_line: bool = False) -> None:
    """Prints to a table strings with data point separated by tabs"""

    ascii_lines = get_ascii_table_lines(*lines, total_line=total_line)
    print(*ascii_lines, sep="\n")


def get_ascii_table_lines(*lines: str, total_line: bool) -> list[str]:
    "Returns a list of strings containing data formatted for ascii table"

    rows = len(lines)
    cols = lines[0].count("\t") + 1
    col_data = {i: [] for i in range(cols)}
    for row in lines:
        row_vals = row.split("\t")
        for i in range(cols):
            col_data[i].append(row_vals[i])

    col_widths = []
    for i in range(cols):
        i_col_vals = col_data[i]
        val_lengths = [len(x) for x in i_col_vals]
        max_len = max(val_lengths)
        col_widths.append(max_len)

    ascii_lines = []
    for line in lines:
        ascii_lines.append(construct_row(line, col_widths))

    border_line = construct_border_line(col_widths)
    ascii_lines.insert(0, border_line)
    if rows > 1:
        ascii_lines.insert(2, border_line)
    if rows > 1 and total_line:
        ascii_lines.insert(len(ascii_lines) - 1, border_line)
    ascii_lines.append(border_line)
    return ascii_lines


def construct_row(row: str, col_widths: list[int]) -> str:
    row_vals = row.split("\t")
    tr = "|"
    for i in range(len(row_vals)):
        val_len = len(row_vals[i])
        padded_row_val = row_vals[i] + " " * (col_widths[i] - val_len)
        tr = " ".join([tr, padded_row_val, "|"])
    return tr


def construct_border_line(col_widths: list[int]) -> str:
    total_len = sum(col_widths) + 3 * len(col_widths) + 1
    border = ["-" for i in range(total_len)]
    border[0] = "+"
    border[-1] = "+"
    running_sum = 0
    for i in col_widths:
        running_sum += i + 3
        border[running_sum] = "+"

    border_str = "".join(border)
    return border_str


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


def move_invoice_files(vendor: str, invoice_num: str) -> None:
    """Moves files related to current invoice to appropriate folder in AP
    directory."""

    ap_path = get_ap_path()
    downloads = os.environ["HOMEPATH"] + "/Downloads"

    clean_inv_num = invoice_num.replace("/", "_").replace("\\", "_")
    new_name_base = f"{vendor} - {clean_inv_num}"

    files_to_move = os.listdir(downloads)
    new_file_names = create_new_inv_file_names(
        old_fnames=files_to_move, new_name=new_name_base
    )

    for old, new in zip(files_to_move, new_file_names):
        shutil.move(src=(downloads + "/" + old), dst=(ap_path + "/" + new))


def get_ap_path() -> str:
    """Returns path for AP for the current month and year."""

    now = datetime.now()
    ap_path = "/".join(
        [
            "C:/gdrive/Shared drives/accounting/Payables",
            f"{now.year:s}",
            now.strftime("%Y%m"),
        ]
    )
    return ap_path


def create_new_inv_file_names(
    old_fnames: list[str], new_name: str
) -> list[str]:

    extensions = [file.split(".")[-1] for file in old_fnames]
    count_of_extensions = Counter(extensions)
    new_file_names = []
    for i in range(len(old_fnames)):
        i_ext = extensions[i]
        new_fname = new_name + i_ext
        if count_of_extensions[i_ext] > 1:
            count = 0
            for name in new_file_names:
                if i_ext in name:
                    count += 1
            if count > 0:
                new_fname = new_fname + f"_{count:s}"
        new_file_names.append(new_fname)


def parse_inv_dets_response(response: str, id: int, con: pyodbc.Connection):
    pattern = r"([,]?[\s]?[\w\s#]+: [\d\w\s\(\)\.\&\-]+)+"
    matched_phrase = re.match(pattern, response)
    ret_val = handle_invoice_details_input(id, matched_phrase, response, con)
    return ret_val


def handle_invoice_details_input(
    index: int, match: re.Match | None, update: str, con: pyodbc.Connection
) -> None:
    if match:
        groups = match.groups()
        update_values(index, groups, con)
    elif update == "":
        return
    elif update == "delete":
        remove_invoice(index, con)
    # elif update == "open":
    #     open_invoice(index)
    else:
        print("Invalid inputs!")


def update_values(index: int, groups: tuple[str], con: pyodbc.Connection):
    valid_updates = []

    for group in groups:
        if group is None:
            continue

        split_text = group.split(":")
        col = split_text[0].replace(", ", "")
        val = split_text[1].strip()
        if validate_invoice_update(col, val):
            # adjust boolean value to 0 or 1
            if col in ["cc", "paid", "approved"]:
                bool_val = "0" if val == "False" else "1"
                valid_updates.append([col, bool_val])

            valid_updates.append([col, val])
        else:
            valid_updates = False
            break

    if not valid_updates:
        return
    else:
        for col, val in valid_updates:
            APDatabase.update_value(
                id=index, column=col, value=val, connection=con
            )


def validate_invoice_update(col: str, val: str) -> bool:
    read_only_cols = [
        "id",
        "date_added",
    ]
    if col not in APDatabase.invoices_cols:
        print("Invalid column name")
        return False
    elif col in read_only_cols:
        print("Invalid update: read-only field")
        return False

    regex_mapping = {
        "vendor": r"[\w\-']+",
        "inv_num": r"[\w\s\-'\(\)/\.\&\-]+",
        "amount": r"\d+\.?\d{0,2}",
        "ym": r"\d{6}",
        "cc": r"(?i)False|True",
        "cc_user": r"[A-Z]{2}",
        "approved": r"(?i)False|True",
        "paid": r"(?i)False|True",
        "date_paid": r"\d{4}-\d{2}-\d{2}",
    }

    if not re.match(regex_mapping[col], val):
        print(
            f"Invalid update: new value '{val}' for column"
            f"'{col}' does not conform to acceptable input pattern",
            "\n",
        )
        input("Update cancelled, no changes will be made.\nEnter to continue")
        return False

    return True


def remove_invoice(id: int, connection: pyodbc.Connection) -> None:
    print("")
    print("Are you sure you want to remove this invoice?")
    print("This cannot be undone.\n")
    answer = input("yes/no: ")
    if answer == "yes":
        APDatabase.remove_item(id=id, connection=connection)
