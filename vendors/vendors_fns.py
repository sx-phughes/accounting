import pandas as pd
import numpy as np

vendor_path = "C:/gdrive/Shared drives/accounting/patrick_data_files/ap"
vendor_f = "Vendors.xlsx"
path = "/".join([vendor_path, vendor_f])
sheet_name = "Vendors"


def open_df() -> pd.DataFrame:
    t = pd.read_excel(io=path, sheet_name=sheet_name)
    return t


def save_df(t: pd.DataFrame) -> None:
    t.to_excel(path, sheet_name=sheet_name)


def get_vendor_info(name: str, t: pd.DataFrame) -> np.ndarray:
    vendor = t.loc[t["Vendor"] == name].values
    return vendor


def change_vendor_info(vendor: str, col: str, new_val: str, t: pd.DataFrame) -> None:
    t.loc[t["Vendor"] == vendor, col] = new_val


def filter_table(col: str, val: str, t: pd.DataFrame) -> pd.DataFrame:
    return t[t[col] == val]
