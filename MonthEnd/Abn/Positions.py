import pandas as pd
import numpy as np

from MonthEnd.Abn import FileGrabber
import Debug

positions_data_table = None


def process_positions_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Prepares a month-end positions file for use in the positions summary
    functions"""

    data = clean_positions_data()
    data["Unique Name"] = vector_unique_name(data.copy())
    return data


def clean_positions_data(positions: pd.DataFrame) -> pd.DataFrame:
    """Cleans up raw positions file, typing and filling in NA values"""

    Debug.dprint("Cleaning positions_data")
    positions["Strike Price"] = positions["Strike Price"].astype(np.float64)
    positions["Expiry Date"] = (
        positions["Expiry Date"].fillna(0).astype(np.int64)
    )
    cols = ["Expiry Date", "Put Call", "Strike Price"]
    positions[cols] = positions[cols].fillna("")
    return positions


def vector_unique_name(data: pd.DataFrame) -> pd.Series:
    """Vector function for creating a unique instrument name for each
    position line"""

    data["futures_temp"] = ""
    mask = data["Account Type"].isin(["BKDL", "XMAR"])
    data["futures_temp"] = data["futures_temp"].where(mask, "Futures")

    data["symbol_temp"] = data["Symbol"]
    data["strike_price_temp"] = data["Strike Price"]
    data["expiry_temp"] = data["Expiry Date"]
    data["put_call_temp"] = data["Put Call"]

    temp_cols_names = [
        "symbol_temp",
        "strike_price_temp",
        "expiry_temp",
        "put_call_temp",
    ]

    data["Unique Name"] = data["futures_temp"]

    for name in temp_cols_names:
        data[name] = data[name].astype(str)
        vals_to_match = ["", "0", "0.0", np.float64(0), np.int64(0), np.nan]
        mask = data[name].isin(vals_to_match)
        data[name] = data[name].mask(mask, "")
        data["Unique Name"] += data[name]

    return data["Unique Name"]


def pivot_positions(clean_positions: pd.DataFrame) -> pd.DataFrame:
    """Pivots the position data by instrument name and summarizes by
    Mark-to-Market value and OTE, as well as labels each by asset class."""

    pivot = clean_positions.pivot_table(
        values=["Mark To Market Value", "OTE"],
        index="Unique Name",
        aggfunc="sum",
    )
    pivot = pivot.reset_index(drop=False)
    pivot[["Mark To Market Value", "OTE"]] = pivot[
        ["Mark To Market Value", "OTE"]
    ].fillna(0)
    pivot["Category"] = pivot.apply(
        lambda row: get_category(row), axis=1, raw=False
    )
    pivot["Total Value"] = pivot["Mark To Market Value"] + pivot["OTE"]

    return pivot


def get_category(row: pd.Series) -> str:
    """Returns the asset category given a row of the position pivot"""

    if row["OTE"] != 0:
        return "OTE"

    asset = get_asset_class(row["Unique Name"])
    if row["Mark To Market Value"] > 0:
        return "Long " + asset
    elif row["Mark To Market Value"] < 0:
        return "Short " + asset


def get_asset_class(unique_name: str) -> str:
    """Get asset class given a unique instrument name."""

    if "Futures" in unique_name:
        if "Put" in unique_name or "Call" in unique_name:
            return "Futures Option"
        else:
            return "Futures"
    elif "Put" in unique_name or "Call" in unique_name:
        return "Option"
    else:
        return "Stock"


def summarize_by_category(positions_pivot: pd.DataFrame) -> pd.DataFrame:
    """Summarizes a pivoted position table by asset category for use in booking
    net positions to the GL"""

    categories = positions_pivot.pivot_table(
        values="Total Value", index="Category", aggfunc="sum"
    )
    categories = categories.reset_index(drop=False)
    drop_na_categories(categories)
    return categories


def drop_na_categories(data: pd.DataFrame) -> None:
    """Fills in 0 for NA values in the position pivot and drops rows where
    the total value is 0."""

    data.fillna(0, inplace=True)
    na_rows = data.loc[data["Total Value"] == 0].index
    data.drop(index=na_rows, inplace=True)


def me_get_positions_data() -> pd.DataFrame:
    """Month-end wrapper functino for process_positions_data."""

    raw_data = FileGrabber.cm_position
    data = process_positions_data(raw=raw_data)
    global positions_data_table
    positions_data_table = data
    return data


def me_get_positions_pivot() -> pd.DataFrame:
    """Month-end wrapper function for pivot_positions."""
    global positions_data_table, pivoted
    pivoted = pivot_positions(clean_positions=positions_data_table)
    return pivoted


def me_get_category_summary() -> pd.DataFrame:
    """Month-end wrapper function for summarize_by_category."""

    global pivoted
    return summarize_by_category(positions_pivot=pivoted)
