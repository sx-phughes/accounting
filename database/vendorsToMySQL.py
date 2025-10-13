import pandas as pd
import pyodbc


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


def create_table():
    command = """CREATE TABLE vendors (
        vendor varchar(255),
        company varchar(255),
        exp_cat varchar(255),
        approver varchar(255),
        pmt_type varchar(255),
        qb_mapping varchar(255),
        acct_mapping mediumint,
        ach_aba char(9),
        ach_acct_no varchar(255),
        ach_vendor varchar(255),
        idb bit,
        contact varchar(255),
        email varchar(255),
        phone varchar(255),
        template varchar(255),
        ben_id varchar(255),
        ben_id_type varchar(255),
        ben_country varchar(255),
        ben_bank_id_type varchar(255),
        ben_bank_id varchar(255),
        ben_bank_name varchar(255),
        ben_bank_address_line_1 varchar(255),
        ben_bank_address_line_2 varchar(255),
        ben_bank_city_st_prov_zip varchar(255),
        ben_bank_country varchar(255),
        int_bank_id_type varchar(255),
        int_bank_id varchar(255),
        int_bank_name varchar(255),
        int_bank_address_line_1 varchar(255),
        int_bank_address_line_2 varchar(255),
        int_bank_city_st_prov_zip varchar(255),
        int_bank_country varchar(255)
        );"""

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
    con.execute(command)


def get_vendor_data() -> pd.DataFrame:
    path = (
        "C:/gdrive/Shared drives/accounting/patrick_data_files/"
        "ap/Vendors.xlsx"
    )
    sheet_name = "Vendors"
    data = pd.read_excel(io=path, sheet_name=sheet_name, dtype=str)
    global vendor_cols, dtypes
    dtypes = []
    vendor_cols = data.columns.values.tolist()

    for col in vendor_cols:
        if col == "Account Mapping":
            dtypes.append("int")
        elif col == "IDB Broker":
            dtypes.append("bit")
        else:
            dtypes.append("string")

    return data


def row_to_string(row: pd.Series) -> str:
    filled_na = row.fillna("")
    vals_list = filled_na.values.tolist()
    global vendor_cols, dtypes

    prelim = ""
    for i in range(len(vendor_cols)):
        formatted_val = vals_list[i].replace("'", "''")

        if vals_list[i] == "" and dtypes[i] != "bit":
            prelim = "".join([prelim, "NULL, "])
        elif dtypes[i] == "int":
            prelim = "".join([prelim, vals_list[i], ", "])
        elif dtypes[i] == "bit":
            if vals_list == "Yes":
                prelim = "".join([prelim, "b'1', "])
            else:
                prelim = "".join([prelim, "b'0', "])
        else:
            prelim = "".join([prelim, "'", formatted_val, "', "])

    result = prelim[:-2]

    return result


def insert_data():
    table = get_vendor_data()
    con = connect_to_accounting()

    insert_command = "INSERT INTO vendors VALUES ({vals});"

    for i, row in table.iterrows():
        if i == 0:
            continue
        row_str = row_to_string(row)
        cmd_formatted = insert_command.format(vals=row_str)
        print(cmd_formatted, "\n")
        con.execute(cmd_formatted)

    con.commit()
    con.close()


def test_stringification():
    data = get_vendor_data()
    for i, row in data.iterrows():
        out = row_to_string(row)
        print(out, "\n\n")
        if i > 3:
            break


def test_data(con: pyodbc.Connection = None):
    con = connect_to_accounting()

    query = "SELECT * FROM vendors WHERE company='Investments';"
    curs = con.execute(query)
    result = curs.fetchall()
    print(result)


if __name__ == "__main__":
    pass
