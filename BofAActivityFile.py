import pandas as pd
import numpy as np
import sys
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="PosFile.log", filemode="w", encoding="utf-8", level=logging.DEBUG
)

field_spec = [
    ["record_type", 4, 6],
    ["firm_num", 6, 10],
    ["process_date", 10, 18],
    ["src_code", 18, 20],
    ["acct_acronym", 20, 30],
    ["origin_type", 30, 31],
    ["acct_group_code", 34, 37],
    ["tax_id", 44, 54],
    ["exp_day", 54, 56],
    ["opt_strike_decimal", 56, 60],
    ["activity_type", 60, 61],
    ["trade_type", 61, 63],
    ["trade_exch", 63, 64],
    ["activity_trx_tag", 64, 70],
    ["td", 70, 78],
    ["cusip", 94, 103],
    ["buy_sell", 103, 104],
    ["trading_symbol", 104, 114],
    ["base_symbol", 114, 124],
    ["exp_year", 124, 128],
    ["exp_month", 128, 130],
    ["opt_strike_dollar", 130, 134],
    ["call_put", 135, 136],
    ["quantity", 136, 145],
    ["shares_per_contract", 145, 150],
    ["opt_multiplier", 150, 157],
    ["unit_cost", 157, 168],
    ["stock_settle_indicator", 168, 169],
    ["stock_indicator", 169, 170],
    ["short_sale", 170, 171],
    ["exp_type", 171, 172],
    ["flex_indicator", 172, 173],
    ["commission", 174, 183],
    ["execution_fee", 183, 192],
    ["exch_fee", 192, 201],
    ["sec_fee", 201, 210],
    ["off_floor_comm", 210, 219],
    ["exec_broker", 219, 229],
    ["linkage", 229, 230],
    ["opt_strike_dollar_int", 230, 235],
    ["opposing_broker", 235, 239],
    ["opposing_firm", 239, 243],
    ["trader", 243, 247],
    ["cboe_trx_id", 247, 256],
    ["basket_name", 256, 261],
    ["exec_time", 261, 265],
    ["basket_tag_no", 265, 268],
    ["closing_price", 268, 281],
    ["exercise_assn_ref", 281, 289],
    ["opt_basket_symbol", 289, 294],
    ["opra_code", 294, 296],
]


def line_to_fields(line: str) -> list[str]:
    """Splits a line of the BofA file to parsed fields"""

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
            logging.info(f"adding {line_data[i]} to field {field_names[i]}")
            parsed[field_names[i]].append(line_data[i])

    for key in parsed.keys():
        logging.info(f"{key}: {len(parsed[key])} items")

    df = pd.DataFrame(parsed)
    return df


def get_text_file(date: str) -> str:
    """Gets the raw pnl text file from specific date"""

    clearing_archive = "C:/gdrive/Shared drives/Clearing Archive"
    date_folder = f"BOFA_Archive/{date}"
    file_name = f"WSC748T6.CS6E1YFL.TXT.{date}"

    path = "/".join([clearing_archive, date_folder, file_name])

    with open(path, "r") as file:
        text = file.read()

    return text


def clean_activity_file(data: pd.DataFrame) -> pd.DataFrame:
    """Cleans up and formats the activity file data"""

    data["closing_price"] = (
        data["closing_price"].astype(np.float64) / 100000000
    )
    data["unit_cost"] = data["unit_cost"].astype(np.float64) / 1000000

    return data


def get_activity_file_from_date(date: str) -> pd.DataFrame:
    text = get_text_file(date)
    raw = convert_text_to_df(text)
    clean = clean_activity_file(raw)

    return clean


def save_activity_to_downloads():
    date = sys.argv[1]
    df = get_activity_file_from_date(date)

    downloads = os.getenv("HOMEPATH") + "/Downloads"
    df.to_csv(downloads + f"/BOFA_Activity_{date}.csv")


if __name__ == "__main__":
    save_activity_to_downloads()
