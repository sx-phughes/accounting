import os
import re
import sys
import pandas as pd
import numpy as np


def parse_file() -> None:
    """Method for parsing the ridiculously formatted BofA Short Stock Rebate
    detail file.

    Command line arg will be the full path of the file in the clearing
    archive"""
    path = sys.argv[1]

    with open(path, "r") as f:
        text = f.read()

    text1 = text.replace("-", ",-")
    text2 = text1.replace("+", ",")
    text2 = re.sub(r" +(?![A-Z]{1,3} )", ",", text2)

    if "/" in path:
        f_name = path.split("/")[-1]
    else:
        f_name = path.split("\\")[-1]

    dest = os.getenv("HOMEPATH") + f"/Downloads/{f_name}_prelim.csv"

    with open(dest, "w") as f:
        f.write(text2)

    cols = [
        "GROUP ACCT",
        "ACCT",
        "SYMBOL/CUSIP/DESCRIPTION",
        "DATE",
        "POSITION",
        "PRICE",
        "SPEC ABS (Y) RATE EXC (*)",
        "SPEC SMV",
        "FD SMV",
        "REBATE",
    ]

    df = pd.read_csv(dest, skiprows=1, names=cols, index_col=False)

    all_data = df.copy()
    all_data["REBATE"] = all_data["REBATE"].str[:-1]

    decimal_cols = [
        "PRICE",
        "SPEC ABS (Y) RATE EXC (*)",
        "SPEC SMV",
        "FD SMV",
        "REBATE",
    ]

    for col in decimal_cols:
        all_data[col] = all_data[col].astype(np.float64).round(0) / 100

    all_data.to_csv(dest)


if __name__ == "__main__":
    parse_file()
