from datetime import datetime, timedelta
from collections.abc import Callable
import os
import pandas as pd
from zipfile import ZipFile


downloads = "/".join([os.environ["HOMEPATH"], "Downloads"])

def get_abn_file_with_pattern(pattern: str, date: str) -> pd.DataFrame:
    """Get abn file with a specific pattern. Pattern must be a formattable
    string with argument to substitute date."""

    formatted = pattern.format(date=date)
    path = "/".join([
        "C:/gdrive/Shared drives/Clearing Archive/ABN_Archive",
        date,
        formatted
    ])
    ext = get_extension(formatted)
    if ext == "csv":
        data = pd.read_csv(path, low_memory=False)
    elif ext == "zip":
        extract_path = downloads
        with ZipFile(path, "r") as zip:
            zip.extractall(extract_path)
        csv_name = formatted.replace(".zip", "")
        path = "/".join([extract_path, csv_name])
        data = pd.read_csv(path, low_memory=False)
    else:
        return None

    return data
        
def get_extension(file_name: str) -> str:
    """Gets extension from a given file type"""

    split_name = file_name.split(".")
    extension = split_name[-1]
    return extension

def generate_dates(date_list: list, year: int, month: int) -> None:
    """Generates the dates for all the days in a given month"""

    one_day = timedelta(days=1)
    
    date = datetime(year, month, 1)
    for i in range(0, 32):
        if date.month == month:
            date_list.append(date)
        else:
            break
        date += one_day
    
def get_monthly_files(pattern: str, 
                     year: int, month: int, 
                     filter_function: Callable[[pd.DataFrame], pd.DataFrame]
                     ) -> list[pd.DataFrame]:
    """Returns a monthly concatted file of data from daily files fitting
    the given pattern and filtered using the filter function.
    
    Pattern: a string with a formatting field with parameter 'date'
    Year, month: int
    filter_function: a function that takes a dataframe and returns a dataframe
    """

    dates = []
    generate_dates(date_list=dates, year=year, month=month)
    files = []
    for date in dates:
        date_str = date.strftime("%Y%m%d")
        try:
            data = get_abn_file_with_pattern(pattern=pattern, date=date_str)
            data = filter_function(data)
            if data.empty:
                print(f"File for date {date_str} has no SEC fee data.")
                continue
            files.append(data)
        except:
            continue
    
    return files

def filter_data_frame_by_col(df: pd.DataFrame, col: str,
                             val: str, contains: bool=False,
                             **kwargs) -> pd.DataFrame:
    """Filters a dataframe by col == val. If contains is true, filters by
    str.contains instead. Additional flags by kwargs"""

    filtered = df.loc[df[col] == val]
    if contains:
        case=False
        regex=True
        if kwargs:
            case = kwargs["case"]
            regex = kwargs["regex"]
        filtered = df.loc[df[col].str.contains(val, case=case, regex=regex)]

    return filtered.copy(deep=True)

def filter_cash_movement(df: pd.DataFrame) -> pd.DataFrame:
    """Filters the cash_movement file to only rows where Cash Title contains 
    'SEC'"""
    col = "Cash Title"
    val = "SEC"
    data = filter_data_frame_by_col(df=df, col=col, val=val, contains=True)
    return data

def concat_df_list(df_list: list[pd.DataFrame]) -> pd.DataFrame:
    """Concatenates a list of DataFrames into one DataFrame"""

    combined = df_list[0].copy(deep=True)
    for file_no in range(1, len(df_list)):
        if df_list[file_no].empty:
            continue
        combined = pd.concat([combined, df_list[file_no]])
        combined = combined.reset_index(drop=True)
    return combined

if __name__ == "__main__":
    pattern = "{date}-2518-C2518-Cash_Movement.csv.zip"
    year = 2025
    month = 6
    list_of_dfs = get_monthly_files(pattern, year, month, filter_cash_movement)
    data = concat_df_list(df_list=list_of_dfs)

    save_name = "june_cash_movement_sec_fees.csv"
    data.to_csv("/".join([downloads, save_name]), index=False)