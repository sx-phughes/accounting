"""
Module containing base classes for the ABN Cash functions
"""

import os
import pandas as pd
from datetime import datetime

from MonthEnd.Abn.Base import get_archive_path

eqt_pattern = "EQTCASH_{folder}.CSV"
mics_pattern = "MICS_CASH_{folder}.csv"


def save_eqt_to_disk(
    year: int, month: int, annual: bool = False, ledgers: str = None
) -> None:

    if ledgers:
        int_ledgers = parse_ledgers(ledgers)
    if annual:
        data = annual_cash(year, "eqt", int_ledgers)
        fname = f"{year} eqt cash"
        if ledgers:
            fname += " ledgers_"
            fname += "_".join([str(x) for x in int_ledgers])
        fname += ".csv"
    else:
        data = get_eqt_cash_data(year, month)
        moyr = datetime(year, month, 1).strftime("%Y%m")
        fname = f"{moyr} eqt cash.csv"

    data.to_csv(
        "/".join(
            [
                "C:/gdrive/Shared drives/accounting/patrick_data_files/abn_cash_files",
                fname,
            ]
        ),
        index=False,
    )
    input("File generated, enter to continue")


def save_mics_to_disk(
    year: int, month: int, annual: bool = False, ledgers: str = None
) -> None:
    # data = get_mics_cash_data(year, month)
    # moyr = datetime(year, month, 1).strftime("%Y%m")

    if ledgers:
        int_ledgers = parse_ledgers(ledgers)
    if annual:
        data = annual_cash(year, "mics", int_ledgers)
        fname = f"{year} mics cash"
        if ledgers:
            fname += " ledgers_"
            fname += "_".join([str(x) for x in int_ledgers])
        fname += ".csv"
    else:
        data = get_mics_cash_data(year, month)
        moyr = datetime(year, month, 1).strftime("%Y%m")
        fname = f"{moyr} mics cash.csv"

    data.to_csv(
        "/".join(
            [
                "C:/gdrive/Shared drives/accounting/patrick_data_files/abn_cash_files",
                fname,
            ]
        ),
        index=False,
    )
    input("File generated, enter to continue")


def get_eqt_cash_data(year: int, month: int) -> pd.DataFrame:
    eqt_data = get_cash_data(year, month, eqt_pattern)
    return eqt_data


def get_mics_cash_data(year: int, month: int) -> pd.DataFrame:
    mics_data = get_cash_data(year, month, mics_pattern)
    return mics_data


def get_cash_data(year: int, month: int, file_pattern: str) -> pd.DataFrame:
    month_year = datetime(year, month, 1).strftime("%Y%m")
    filtered_folders = get_folders(month_year)
    concatted_data = concat_tables(file_pattern, filtered_folders)
    return concatted_data


def get_folders(moyr: str) -> list[str]:
    os.chdir(get_archive_path())
    folders = os.listdir()
    filtered_folders = list(filter(lambda x: moyr in x, folders))
    return filtered_folders


def format_path(pattern: str, folder: str) -> str:
    full_path = get_archive_path() + "/" + folder
    formatted_pattern = pattern.format(folder=folder)
    full_file_path = "/".join([full_path, formatted_pattern])
    return full_file_path


def concat_tables(pattern: str, folders: list[str]) -> pd.DataFrame:
    headers = [
        "DateEntered",
        "Account",
        "Subaccount",
        "Tag",
        "LedgerNumber",
        "Amount",
        "Description",
        "Product",
        "Currency",
    ]
    all_data = pd.DataFrame(columns=headers)

    for i in sorted(folders):
        unique_dates = all_data.DateEntered.unique().tolist()

        print(i)
        full_file_path = format_path(pattern, i)
        print(f"\t{full_file_path}")
        try:
            curr_file = pd.read_csv(full_file_path)
        except FileNotFoundError:
            curr_file = pd.DataFrame()
            print("File not found")

        if curr_file.empty:
            print("curr_file empty; continuing\n")
            continue
        elif all_data.empty:
            print(curr_file.head())
            all_data = curr_file.copy()
        elif curr_file.iloc[0, 0] in unique_dates:
            print("Dupe date found, continuing\n")
            continue
        else:
            print("Concatting below data to big df:")
            print(curr_file.head())
            all_data = pd.concat([all_data, curr_file])

        print("\n")
    if not all_data.empty:
        sorted_data = all_data.sort_values(by="DateEntered", axis=0)
        return sorted_data
    else:
        return all_data


def annual_cash(year: int, type: str, ledgers: list = None) -> pd.DataFrame:
    all_data = pd.DataFrame()
    for i in range(1, 13):
        if type == "eqt":
            file = get_eqt_cash_data(year, i)
        elif type == "mics":
            file = get_mics_cash_data(year, i)

        if ledgers:
            filtered = file.loc[file["LedgerNumber"].isin(ledgers)]
            final = filtered.copy(deep=True)
        else:
            final = file.copy(deep=True)

        if final.empty:
            continue
        elif all_data.empty:
            all_data = final.copy()
        else:
            all_data = pd.concat([all_data, final])

    sorted = all_data.sort_values(by="DateEntered", axis=0)
    return sorted


def parse_ledgers(ledgers: str) -> list[int]:
    ledgers_indiv = ledgers.split(",")
    trimmed = [str.strip(x) for x in ledgers_indiv]
    ledger_ints = [int(x) for x in trimmed]
    return ledger_ints
