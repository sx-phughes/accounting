import os
import re
import pandas as pd


def get_table_sums(data: pd.DataFrame) -> tuple[int]:
    data["abs_quantity"] = data["quantity"].abs()
    stock_size = data.loc[data["TYPE"] == "S", "abs_quantity"].sum()
    option_size = data.loc[data["TYPE"] != "S", "abs_quantity"].sum()
    return (stock_size, option_size)


def get_yearly_quantities(year: int) -> tuple[int, int]:
    abn_archive = "C:/gdrive/Shared drives/Clearing Archive/ABN_Archive"
    year_folders = list(
        filter(lambda x: str(year) in x, os.listdir(abn_archive))
    )

    file_pattern = r"EQTTRADE_V7_\d{8}\.CSV"
    # for folder in year_folders:
