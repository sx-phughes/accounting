import pandas as pd
import sys
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="PosFile.log", encoding="utf-8", level=logging.DEBUG
)


field_spec = [
    ["firm_num", 4, 8],
    ["account", 8, 18],
    ["call_put", 18, 19],
    ["base_sym", 19, 29],
    ["exp_year", 29, 33],
    ["exp_month", 33, 35],
    ["opt_strike_dollar", 35, 40],
    ["long_short", 42, 43],
    ["security_type", 43, 44],
    ["close_price", 44, 54],
    ["num_biz_days_to_exp", 54, 58],
    ["td_pos", 61, 71],
    ["cusip", 71, 80],
    ["exp_type", 80, 81],
    ["trade_sym", 86, 96],
    ["exp_day", 96, 98],
    ["opt_strike_decimal", 98, 107],
    ["exp_multip", 107, 112],
    ["flex", 132, 133],
    ["origin", 135, 136],
    ["opra_code", 136, 138],
    ["opt_basket_sym", 138, 143],
    ["acct_group", 243, 246],
    ["underlying_price", 246, 256],
    ["volatility", 256, 264],
    ["theoretical_val", 264, 272],
    ["delta", 272, 279],
    ["delta_sign", 279, 280],
    ["gamma", 280, 287],
    ["gamma_sign", 287, 288],
    ["theta", 288, 295],
    ["theta_sign", 295, 296],
    ["vega", 296, 303],
    ["vega_sign", 303, 304],
    ["at_the_money_volatility", 304, 311],
    ["risk_free_rate", 311, 318],
    ["volatility", 317, 322],
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

    for key in parsed.keys():
        print(key, len(parsed[key]))

    df = pd.DataFrame(parsed)
    return df


def get_text_file(date: str) -> str:
    """Gets the raw pnl text file from specific date"""

    clearing_archive = "C:/gdrive/Shared drives/Clearing Archive"
    date_folder = f"BOFA_Archive/{date}"
    file_name = f"WSC734TK.E7YPOS11.TXT.{date}"

    path = "/".join([clearing_archive, date_folder, file_name])

    with open(path, "r") as file:
        text = file.read()

    return text


def get_pos_file_from_date(date: str) -> pd.DataFrame:
    text = get_text_file(date)
    raw = convert_text_to_df(text)
    # clean = clean_pnl_data(raw)

    return raw


def save_pnl_to_downloads():
    date = sys.argv[1]
    df = get_pos_file_from_date(date)

    downloads = os.getenv("HOMEPATH") + "/Downloads"
    df.to_csv(downloads + f"/BOFA_POS_{date}.csv")


if __name__ == "__main__":
    save_pnl_to_downloads()
