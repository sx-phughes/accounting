from datetime import datetime, timedelta
import pandas as pd
import os
import pyodbc


payables_root = "C:/gdrive/Shared drives/accounting/Payables"


def connect_to_accounting():
    uid = input("userid:")
    pwd = input("pwd:")

    conn_string = (
        "DRIVER=MySQL ODBC 9.4 ANSI Driver;"
        "SERVER=simplex.s;"
        "DATABASE=accounting;"
        f"UID={uid};"
        f"PWD={pwd};"
        "charset=utf8mb4"
    )

    con = pyodbc.connect(conn_string)

    con.setdecoding(pyodbc.SQL_WCHAR, encoding="utf-8")
    con.setencoding(encoding="utf-8")

    return con


def get_ym_list() -> list[str]:
    start = datetime(2023, 1, 1)
    increment = timedelta(days=31)
    months = []
    current = start
    end = datetime(2025, 9, 30)

    while current <= end:
        date_str = current.strftime("%Y%m")
        months.append(date_str)
        current += increment

    return months


def get_ap_files_for_month(month: str) -> list[list[str]]:
    month_path = "/".join(
        ["C:/gdrive/Shared drives/accounting/Payables", month[:4], month]
    )

    ls_result = os.listdir(month_path)
    xlsm_files = list(filter(lambda x: ".xlsm" in x, ls_result))
    xlsms_with_paths = [[file, month_path, month] for file in xlsm_files]
    folders = list(filter(lambda x: "." not in x, ls_result))

    if len(folders) > 0:
        for folder in folders:
            sub_dir = month_path + "/" + folder
            try:
                contents = os.listdir(sub_dir)
            except NotADirectoryError:
                continue

            sub_xlsm_files = list(filter(lambda x: ".xlsm" in x, contents))
            if len(sub_xlsm_files) > 0:
                for file in sub_xlsm_files:
                    item = [file, sub_dir, month]
                    xlsms_with_paths.append(item)

    return xlsms_with_paths


def get_ap_files_for_all(months: list[str]) -> list[list[str]]:
    all_files = []
    for month in months:
        month_files = get_ap_files_for_month(month)
        if len(month_files) > 0:
            all_files = all_files + month_files
        else:
            continue

    return all_files


def create_payables_master_table(files_list: list[list[str]]):
    master_table = pd.DataFrame()
    for file in files_list:
        full_path = file[1] + "/" + file[0]
        sub_table = pd.read_excel(io=full_path, sheet_name="Invoices")
        if sub_table.empty:
            continue

        sub_table["ym"] = file[2]
        empty_rows = sub_table.loc[sub_table["Amount"].isna()].index
        sub_table = sub_table.drop(index=empty_rows).reset_index(drop=True)

        if master_table.empty:
            master_table = sub_table
        else:
            master_table = pd.concat([master_table, sub_table])

    master_table = master_table[
        [
            "Vendor",
            "Invoice #",
            "Simplex2",
            "Expense Category",
            "Approved By",
            "Payment Type",
            "Amount",
            "ym",
        ]
    ].copy(deep=True)

    return master_table


def get_vendor_match(con: pyodbc.Connection, vendor: str) -> str | None:
    if "'" in vendor:
        formatted_vendor = vendor.replace("'", "''")
    else:
        formatted_vendor = vendor

    query = f"select * from vendors where vendor = '{formatted_vendor}';"
    curs = con.execute(query)
    result = curs.fetchone()
    if result:
        return result[0]
    else:
        return None


def fix_unmatched_vendors(invoice_table: pd.DataFrame) -> None:
    vendors = invoice_table["Vendor"].unique()

    con = connect_to_accounting()

    unmatched_vendors = []
    for i in vendors:
        if not get_vendor_match(con, i):
            unmatched_vendors.append(i)

    unmatched_table = pd.DataFrame(
        data={
            "original": unmatched_vendors,
            "new": ["" for vendor in unmatched_vendors],
        }
    )

    for i, row in unmatched_table.iterrows():
        print(f"Old Vendor: {row["original"]}")
        new_vendor = input("New Vendor: ")
        unmatched_table.loc[i, "new"] = new_vendor

    unmatched_table.to_csv(
        os.environ["HOMEPATH"] + "/Downloads/Unmatched.csv", index=False
    )


def open_unmatched_vendors_table() -> pd.DataFrame:
    table = pd.read_csv(os.environ["HOMEPATH"] + "/Downloads/Unmatched.csv")
    return table


def replace_unmatched_vendors(invoice_table: pd.DataFrame):
    unmatched_table = open_unmatched_vendors_table()

    replacements = unmatched_table.to_dict(orient="records")
    mapping = {}
    for row in replacements:
        mapping.update({row["original"]: row["new"]})

    new_table = invoice_table.copy(deep=True)
    for key, value in mapping.items():
        vendor_index = new_table.loc[new_table["Vendor"] == key].index
        new_table.loc[vendor_index, "Vendor"] = value

    return new_table


def save_raw_data_to_disk() -> None:
    dates = get_ym_list()
    files = get_ap_files_for_all(months=dates)
    invoices = create_payables_master_table(files)
    invoices.to_csv(
        os.environ["HOMEPATH"] + "/Downloads/Master_Invoices.csv", index=False
    )


def get_raw_data_from_disk() -> pd.DataFrame:
    path = os.environ["HOMEPATH"] + "/Downloads/Master_Invoices.csv"
    data = pd.read_csv(path)
    return data


def get_clean_data_from_disk() -> pd.DataFrame:
    path = os.environ["HOMEPATH"] + "/Downloads/Cleaned_Master_Invoices.csv"
    data = pd.read_csv(path)
    return data


def make_fresh_clean_data_file() -> None:
    invoices = get_raw_data_from_disk()
    cleaned_invoices = replace_unmatched_vendors(invoices)
    cleaned_invoices.to_csv(
        os.environ["HOMEPATH"] + "/Downloads/Cleaned_Master_Invoices.csv"
    )


def do_the_data_thing():
    data = get_clean_data_from_disk()
    data["CC"] = False
    data["CC User"] = ""
    data["Approved"] = True
    data["Paid"] = True


def create_invoices_table() -> None:
    con = connect_to_accounting()
    command = """CREATE TABLE invoices (
        vendor varchar(255),
        inv_num varchar(255),
        amount float,
        ym int,
        cc tinyint(1),
        cc_user char(2),
        approved tinyint(1),
        paid tinyint(1)
        );"""
    con.execute(command)
    con.close()


if __name__ == "__main__":
    do_the_data_thing()
