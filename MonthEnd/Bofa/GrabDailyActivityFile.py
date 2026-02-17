import pandas as pd
import os, shutil


def grab_file_data(date: str) -> tuple[str, str]:
    """Grabs the BofA daily activty file for a given date

    Args:
        date (str): date in yyyymmdd format

    Returns:
        str: _description_
    """
    bofa_archive = "C:/gdrive/Shared drives/Clearing Archive/BOFA_Archive"
    f_name = f"WSC748T6.CS6E1YFL.TXT.{date}"
    path_to_file = "/".join(
        [
            bofa_archive,
            date,
            f_name,
        ]
    )

    file_data = ""
    with open(path_to_file, "r") as f:
        file_data = f.read()

    return (path_to_file, file_data)


def copy_daily_activity_to_path(date: str, path: str):
    src, data = grab_file_data(date)
    f_name = src.split("/")[-1]
    dest = "/".join(
        [
            path,
            f_name,
        ]
    )
    with open(dest, "w") as f:
        f.write(data)


if __name__ == "__main__":
    path_to_input_file = "C:/gdrive/Shared drives/accounting/Simplex Trading/Audit/2025/2025 Year End Fieldwork/1 - Purchase and Sales/purchase_sales_selections.csv"
    input_file = pd.read_csv(path_to_input_file)
    input_file["Trade Date"] = pd.to_datetime(
        input_file["Trade Date"], format="%m/%d/%Y"
    )
    bofa_only_input = input_file.loc[input_file["Broker"] == "BOFA"].copy()
    for i, row in bofa_only_input.iterrows():
        date = row["Trade Date"].strftime("%Y%m%d")
        copy_daily_activity_to_path(date, os.getenv("HOMEPATH") + "/Downloads")
