from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import re
import calendar
import getpass
import logging
import os
import pyodbc
from collections import Counter


payables_root = "C:/gdrive/Shared drives/accounting/Payables"

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="InvoicesToMySQL.log",
    encoding="utf-8",
    level=logging.DEBUG,
    filemode="w",
)


def connect_to_accounting():
    uid = input("userid: ")
    pwd = getpass.getpass("pwd: ")

    conn_string = (
        "DRIVER=MySQL ODBC 9.1 ANSI Driver;"
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


def check_good_files(filename: str) -> bool:
    bad_names = [
        "December Payables Final Accrual.xlsm",
        "December Payables Batch 1 Final Accrual.xlsm",
    ]
    if (
        ".xlsm" in filename or ".xlsx" in filename
    ) and filename not in bad_names:
        return True
    else:
        return False


def get_ap_files_for_month(month: str) -> list[list[str]]:
    month_path = "/".join(
        ["C:/gdrive/Shared drives/accounting/Payables", month[:4], month]
    )

    ls_result = os.listdir(month_path)
    xlsm_files = list(filter(lambda x: check_good_files(x), ls_result))
    xlsms_with_paths = [[file, month_path, month] for file in xlsm_files]
    folders = list(filter(lambda x: "." not in x, ls_result))

    if len(folders) > 0:
        for folder in folders:
            sub_dir = month_path + "/" + folder
            try:
                contents = os.listdir(sub_dir)
            except NotADirectoryError:
                continue

            sub_xlsm_files = list(
                filter(lambda x: check_good_files(x), contents)
            )
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

        # extract pay date from file name here
        pay_date = get_pay_date(filename=file[0])

        sub_table = pd.read_excel(io=full_path, sheet_name="Invoices")
        if sub_table.empty:
            continue

        sub_table["ym"] = file[2]
        # sub_table["date_paid"] = pay_date.strftime("%Y-%m-%d")
        sub_table["date_added"] = get_date_added(pay_date).strftime("%Y-%m-%d")
        empty_rows = sub_table.loc[sub_table["Amount"].isna()].index
        sub_table = sub_table.drop(index=empty_rows).reset_index(drop=True)

        if master_table.empty:
            master_table = sub_table
        else:
            master_table = pd.concat([master_table, sub_table])

    master_table = master_table[
        [
            "date_added",
            "Vendor",
            "Invoice #",
            # "Simplex2",
            # "Expense Category",
            # "Approved By",
            # "Payment Type",
            "Amount",
            "ym",
            # "date_paid",
        ]
    ].copy(deep=True)

    return master_table


def get_date_added(pay_date: datetime) -> datetime:
    date_added = datetime(pay_date.year, pay_date.month, 1)

    if date_added == pay_date or pay_date.day < 3:
        ref_date = date_added - timedelta(days=20)
        date_added = datetime(ref_date.year, ref_date.month, 1)

    return date_added


def get_pay_date(filename: str) -> datetime:
    logging.debug(filename)
    date_patterns = (
        r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})",
        r"^(?P<year>\d{4})(?P<month>\d{2})(?=\s)",
        r"^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})",
    )

    pattern_match = len(date_patterns) + 5
    for i in range(len(date_patterns)):
        match = re.search(date_patterns[i], filename)
        if match:
            pattern_match = i
            break

    if pattern_match > len(date_patterns) - 1:
        raise ValueError(
            f"Unable to find date pattern in file name {filename}"
        )

    strp_patterns = ("%Y-%m-%d", "%Y%m", "%Y%m%d")
    logging.debug(match.group())
    logging.debug(strp_patterns[pattern_match])

    if pattern_match == 1:
        year = int(match.group("year"))
        month = int(match.group("month"))
        eom_day = calendar.monthrange(year, month)[1]
        pay_date = datetime(year, month, eom_day)
    else:
        pay_date = datetime.strptime(
            match.group(), strp_patterns[pattern_match]
        )
    return pay_date


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
    # dates = get_ym_list()
    # files = get_ap_files_for_all(months=dates)
    files = [
        [
            "2025-09-30 Payables.xlsx",
            "C:/gdrive/Shared drives/accounting/Payables/2025/202509/2025-09-30",
            "202509",
        ]
    ]
    print(files)
    invoices = create_payables_master_table(files)
    while True:
        try:
            invoices.to_csv(
                os.environ["HOMEPATH"] + "/Downloads/Master_Invoices.csv",
                index=False,
            )
            break
        except PermissionError:
            input("Please close the file...")


def get_raw_data_from_disk() -> pd.DataFrame:
    path = os.environ["HOMEPATH"] + "/Downloads/Master_Invoices.csv"
    data = pd.read_csv(path)
    return data


def get_clean_data_from_disk() -> pd.DataFrame:
    path = os.environ["HOMEPATH"] + "/Downloads/Cleaned_Master_Invoices.csv"
    data = pd.read_csv(path)
    return data


def check_dupe_invoices(invoice_table: pd.DataFrame) -> pd.DataFrame:
    invoice_table["Concat"] = (
        invoice_table["Vendor"]
        + invoice_table["Invoice #"]
        + invoice_table["Amount"].astype(str)
    )

    no_dupes = invoice_table.drop_duplicates("Concat").reset_index(drop=True)
    return no_dupes

    # concats = invoice_table["Concat"].values.tolist()
    # dupe_invoices = pd.DataFrame(columns=invoice_table.columns)
    # dupe_counter = Counter(concats)
    # for i in dupe_counter.keys():
    #     if dupe_counter[i] > 1:
    #         dupe_rows = invoice_table.loc[invoice_table["Concat"] == i]
    #         dupe_invoices = pd.concat([dupe_invoices, dupe_rows])

    # dupe_invoices.to_csv(
    #     path_or_buf=os.environ["HOMEPATH"]
    #     + "/Downloads/Duplicate Invoices.csv"
    # )


def make_fresh_clean_data_file() -> None:
    invoices = get_raw_data_from_disk()
    cleaned_invoices = replace_unmatched_vendors(invoices)
    no_dupes = check_dupe_invoices(cleaned_invoices)
    dropped_concat = no_dupes.drop(columns="Concat")
    while True:
        try:
            dropped_concat.to_csv(
                os.environ["HOMEPATH"]
                + "/Downloads/Cleaned_Master_Invoices.csv"
            )
            break
        except PermissionError:
            input("Close the file")

    return dropped_concat


def finalize_table_for_db(clean_data: pd.DataFrame) -> pd.DataFrame:
    clean_data["cc"] = False
    clean_data["cc_user"] = ""
    clean_data["approved"] = False
    clean_data["paid"] = False

    cols = [
        "date_added",
        "Vendor",
        "Invoice #",
        "Amount",
        "ym",
        "cc",
        "cc_user",
    ]
    with_final_cols = clean_data[cols].copy(deep=True)

    new_names = ["vendor", "inv_num", "amount"]
    old = cols[1:4]

    renamer = {old[i]: new_names[i] for i in range(len(new_names))}
    renamed_cols = with_final_cols.rename(columns=renamer)
    return renamed_cols


def row_to_string(row_data: pd.Series, col_names: list[str]) -> str:
    chars = ""
    for i in col_names:
        logging.debug(f"col '{i}': val: '{row_data[i]}'")
        if i == "amount" or i == "ym":
            formatted = f"{row_data[i]}"
        elif i in ["cc", "approved", "paid"]:
            formatted = f"TRUE" if row_data[i] else "FALSE"
        else:
            if row_data[i]:
                use_data = row_data[i]
                try:
                    if "'" in row_data[i]:
                        use_data = row_data[i].replace("'", "''")
                    formatted = f"'{use_data}'"
                except TypeError:
                    if np.isnan(row_data[i]):
                        formatted = f"NULL"
                    else:
                        raise TypeError(f"Cannot parse value {row_data[i]}")
            else:
                formatted = "NULL"

        if i == col_names[-1]:
            chars = "".join([chars, formatted])
        else:
            chars = "".join([chars, formatted, ", "])

    return chars


def construct_insert_statement(
    row_data: pd.Series, col_names: list[str]
) -> str:
    vals_string = row_to_string(row_data=row_data, col_names=col_names)

    statement = f"INSERT INTO invoices (date_added, vendor, inv_num, amount, ym, cc, cc_user, approved, paid, date_paid) VALUES ({vals_string});"

    statement = f"INSERT INTO invoices (date_added, vendor, inv_num, amount, ym, cc, cc_user) VALUES ({vals_string});"

    return statement


def add_invoices_to_db(
    invoices_table: pd.DataFrame, cxn: pyodbc.Connection
) -> None:
    inv_table_cols = invoices_table.columns
    print(*inv_table_cols, sep="\n")
    for i, row in invoices_table.iterrows():
        statement = construct_insert_statement(row, inv_table_cols)
        print(statement)
        cxn.execute(statement)


def create_invoices_table(connection: pyodbc.Connection) -> None:
    command = """CREATE TABLE invoices (
        id int unsigned primary key auto_increment,
        date_added date,
        vendor varchar(255),
        inv_num varchar(255),
        amount float,
        ym int,
        cc tinyint(1),
        cc_user char(2),
        approved tinyint(1),
        paid tinyint(1),
        date_paid date
        );"""
    try:
        connection.execute(command)
    except pyodbc.ProgrammingError as e:
        if "Table 'invoices' already exists" not in str(e):
            raise e


if __name__ == "__main__":
    save_raw_data_to_disk()
    make_fresh_clean_data_file()

    data = get_clean_data_from_disk()
    final_table = finalize_table_for_db(clean_data=data)

    con = connect_to_accounting()
    create_invoices_table(connection=con)
    add_invoices_to_db(invoices_table=final_table, cxn=con)
    con.commit()
    con.close()
