import pandas as pd
import numpy as np

from MonthEnd.Abn import FileGrabber
import Debug

positions_data_table = None

def get_positions_data() -> pd.DataFrame:
    data = clean_positions_data()
    data['Unique Name'] = vector_unique_name(data.copy())

    global positions_data_table
    positions_data_table = data

    return data

def clean_positions_data() -> pd.DataFrame:
    Debug.dprint("Cleaning positions_data")
    positions = FileGrabber.cm_position
    positions['Strike Price'] = positions['Strike Price'].astype(np.float64)
    positions['Expiry Date'] = positions['Expiry Date'].fillna(0).astype(
        np.int64)
    cols = ['Expiry Date', 'Put Call', 'Strike Price']
    positions[cols] = positions[cols].fillna('')
    return positions
    

def vector_unique_name(data: pd.DataFrame) -> pd.Series:
    data["futures_temp"] = ""
    mask = data["futures_temp"].isin(['BKDL', 'XMAR'])
    data["futures_temp"] = data["futures_temp"].where(mask, "Futures")

    data["symbol_temp"] = data["Symbol"]
    data["strike_price_temp"] = data["Strike Price"]
    data["expiry_temp"] = data["Expiry Date"]
    data["put_call_temp"] = data["Put Call"]

    temp_cols_names = [
        "symbol_temp",
        "strike_price_temp",
        "expiry_temp",
        "put_call_temp"
    ]

    data["Unique Name"] = data["futures_temp"]

    for name in temp_cols_names:
        data[name] = data[name].astype(str)
        vals_to_match = [
            "",
            "0",
            "0.0",
            np.float64(0),
            np.int64(0),
            np.nan
        ]
        mask = data[name].isin(vals_to_match)
        data[name] = data[name].mask(mask, "")
        data["Unique Name"] += data[name]

    return data["Unique Name"]

def get_positions_pivot() -> pd.DataFrame:
    global positions_data_table

    data = positions_data_table
    Debug.dprint(data.head(10))
    pivot = data.pivot_table(
        values=['Mark to Market Value', 'OTE'],
        index='Unique Name',
        aggfunc='sum'
    )
    pivot = pivot.reset_index(drop=False)
    pivot[['Mark to Market Value', 'OTE']] = pivot[
        ['Mark to Market Value', 'OTE']
    ].fillna(0)
    pivot['Category']= pivot.apply(
        lambda row: get_category(row),
        axis=0,
        raw=False
    )
    pivot['Total Category'] = pivot['Mark to Market Value'] + pivot['OTE']
    
    global positions_pivot
    positions_pivot = pivot

    return pivot

def get_category(row: pd.Series) -> str:
    if row['ote'] != 0:
        return 'OTE'

    asset = get_asset_class(row["Unique Name"])
    if row['Mark to Market Value'] > 0:
        return "Long " + asset
    elif row['Mark to Market Value'] < 0:
        return "Short " + asset
        
def get_asset_class(unique_name: str) -> str:
    if "Futures" in unique_name:
        if "Put" in unique_name or "Call" in unique_name:
            return "Futures Option"
        else:
            return "Futures"
    elif "Put" in unique_name or "Call" in unique_name:
        return "Option"
    else:
        return "Stock" 

def get_category_summary() -> pd.DataFrame:
    global positions_pivot

    pivot = positions_pivot
    categories = pivot.pivot_table(
        values='Total Value',
        index='Category',
        aggfunc='sum'
    )
    categories = categories.reset_index(drop=False)
    drop_na_categories(categories)
    return categories

def drop_na_categories(data: pd.DataFrame) -> None:
    data.fillna(0, inplace=True)
    na_rows = data.loc[data['Total Value'] == 0].index
    data.drop(index=na_rows, inplace=True)