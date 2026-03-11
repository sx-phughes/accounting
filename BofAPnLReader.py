import pandas as pd
from datetime import datetime
import numpy as np
import sys
import os

field_spec = [
    ["firm_number", 2, 6],
    ["account", 6, 16],
    ["expiration_day", 16, 18],
    ["option_type", 18, 19],
    ["put_call", 19, 20],
    ["symbol", 20, 30],
    ["exp_month", 30, 32],
    ["exp_year", 32, 36],
    ["opt_strike_price_dollar", 36, 40],
    ["opt_strike_price_decimal", 40, 44],
    ["opra_code", 44, 46],
    ["security_type", 46, 47],
    ["contract_multiplier", 48, 54],
    ["origin", 54, 55],
    ["quantity_sign", 55, 56],
    ["quantity", 56, 71],
    ["pl_type", 71, 72],
    ["option_basket_symbol", 73, 77],
    ["option_strike_price_dollar", 77, 82],
    ["pl_sign", 89, 90],
    ["pl_amount", 90, 105],
    ["base_symbol", 105, 115],
    ["cusip", 115, 124],
]

num_fields = [
    "firm_number",
    "expiration_day",
    "exp_month",
    "exp_year",
    "opt_strike_price_dollar",
    "opt_strike_price_decimal",
    "contract_multiplier",
    "quantity",
    "pl_type",
    "option_strike_price_dollar",
    "pl_amount",
]


def line_to_fields(line: str) -> list[str]:
    """Converts a line of the BofA PnL file to code"""

    data = []
    for field in field_spec:
        start = field[1]
        end = field[2]
        data.append(line[start:end])

    return data


def convert_text_to_df(text: str) -> pd.DataFrame:
    """Converts text stream of file to dataframe filled with parsed data"""

    lines = text.split("\n")
    lines.pop(0)  # pop the header
    lines.pop(-1)  # pop blank last row
    lines.pop(-1)  # pop the trailer

    parsed = {field[0]: [] for field in field_spec}

    field_names = [item[0] for item in field_spec]
    for line in lines:
        line_data = line_to_fields(line)
        for i in range(len(line_data)):
            parsed[field_names[i]].append(line_data[i])

    df = pd.DataFrame(parsed)
    return df


def clean_pnl_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the pnl data and returns it in a usable state"""

    # Casting num cols as num types
    for col in num_fields:
        raw_df[col] = raw_df[col].mask(raw_df[col].str.match(r"\s+"), "0")
    raw_df[num_fields] = raw_df[num_fields].astype(np.float64)

    # Combining the strike price dollar and decimal fields
    raw_df["opt_strike_price_decimal"] = (
        raw_df["opt_strike_price_decimal"] / 10000
    )
    raw_df["opt_strike_price"] = (
        raw_df["opt_strike_price_dollar"] + raw_df["opt_strike_price_decimal"]
    )
    cols = raw_df.columns.tolist()
    opt_price_index = cols.index("opt_strike_price_dollar")
    cols.remove("opt_strike_price")
    cols.insert(opt_price_index, "opt_strike_price")
    clean_df = raw_df[cols].copy()

    final = clean_df.drop(
        columns=["opt_strike_price_dollar", "opt_strike_price_decimal"]
    )

    # converting pl and quantity to signed numbers
    final["pl_amount"] = final["pl_amount"] / 100
    signed_cols = [["pl_amount", "pl_sign"], ["quantity", "quantity_sign"]]
    for amt_col, sign_col in signed_cols:
        final[sign_col] = final[sign_col].mask(final[sign_col] == "-", -1)
        final[sign_col] = final[sign_col].mask(final[sign_col] == "+", 1)
        final[amt_col] = final[amt_col] * final[sign_col].astype(np.int64)
        final = final.drop(columns=sign_col)

    return final


def get_text_file(date: str) -> str:
    """Gets the raw pnl text file from specific date"""

    clearing_archive = "C:/gdrive/Shared drives/Clearing Archive"
    date_folder = f"BOFA_Archive/{date}"
    file_name = f"WSC722TG.CLNTGPNL.TXT.{date}"

    path = "/".join([clearing_archive, date_folder, file_name])

    with open(path, "r") as file:
        text = file.read()

    return text


def get_pnl_file_from_date(date: str) -> pd.DataFrame:
    text = get_text_file(date)
    raw = convert_text_to_df(text)
    clean = clean_pnl_data(raw)

    return clean


def get_month_pl(year: int, month: int) -> pd.DataFrame:
    bofa_archive = "C:/gdrive/Shared drives/Clearing Archive/BOFA_Archive"
    ym = datetime(year, month, 1).strftime("%Y%m")
    folders = list(filter(lambda x: ym in x, os.listdir(bofa_archive)))
    data = {"date": [], "pnl": []}
    for date in folders:
        try:
            pnl_file = get_pnl_file_from_date(date)
        except:
            continue
        pnl = pnl_file["pl_amount"].sum()
        data["date"].append(date)
        data["pnl"].append(pnl)

    df = pd.DataFrame(data)
    return df


def save_pnl_to_downloads():
    date = sys.argv[1]
    df = get_pnl_file_from_date(date)

    downloads = os.getenv("HOMEPATH") + "/Downloads"
    df.to_csv(downloads + f"/BOFA_PNL_{date}.csv")
    print(df["pl_amount"].sum())


if __name__ == "__main__":
    year = int(sys.argv[1])
    month = int(sys.argv[2])
    month_pl = get_month_pl(year, month)

    downloads = os.getenv("HOMEPATH") + "/Downloads"
    month_pl.to_csv(downloads + f"/BOFA_PNL_{year}{month}.csv")
