from typing import Any
from datetime import datetime
import pyodbc
import pandas as pd
import numpy as np
import re

invoices_cols = (
    "id",
    "date_added",
    "vendor",
    "inv_num",
    "amount",
    "ym",
    "cc",
    "cc_user",
    "approved",
    "paid",
    "date_paid",
)

invoices_int_cols = (
    "id",
    "amount",
    "ym",
    "cc",
    "approved",
    "paid",
)

vendors_cols = (
    "vendor",
    "company",
    "exp_cat",
    "approver",
    "pmt_type",
    "qb_mapping",
    "acct_mapping",
    "ach_aba",
    "ach_acct_no",
    "ach_vendor",
    "idb",
    "contact",
    "email",
    "phone",
    "template",
    "ben_id",
    "ben_id_type",
    "ben_country",
    "ben_bank_id_type",
    "ben_bank_id",
    "ben_bank_name",
    "ben_bank_address_line_1",
    "ben_bank_address_line_2",
    "ben_bank_city_st_prov_zip",
    "ben_bank_country",
    "int_bank_id_type",
    "int_bank_id",
    "int_bank_name",
    "int_bank_address_line_1",
    "int_bank_address_line_2",
    "int_bank_city_st_prov_zip",
    "int_bank_country",
)

col_to_table_map = {}
for i in vendors_cols:
    col_to_table_map.update({i: "vendors"})
for i in invoices_cols:
    col_to_table_map.update({i: "invoices"})


def establish_db_connection(uid, pwd) -> pyodbc.Connection:
    """Returns a connection object linked to the accounting database."""

    conn_string = (
        "DRIVER=MySQL ODBC 9.1 ANSI Driver;"
        "SERVER=simplex.s;"
        "DATABASE=accounting;"
        f"UID={uid};"
        f"PWD={pwd};"
        "charset=utf8mb4"
    )

    try:
        con = pyodbc.connect(conn_string)
    except pyodbc.InterfaceError:
        con = pyodbc.connect(conn_string.replace("9.1", "9.4"))

    con.setdecoding(pyodbc.SQL_WCHAR, encoding="utf-8")
    con.setencoding(encoding="utf-8")
    return con


def get_main_menu_summary_data(con: pyodbc.Connection) -> pd.DataFrame:
    """Retrieves summary data for unpaid invoices."""

    query = """select 
        vendors.company, 
        sum(invoices.amount) as total
    from invoices
    left join vendors on invoices.vendor = vendors.vendor
    where invoices.paid = FALSE
    and invoices.cc = FALSE
    group by vendors.company;"""

    data = pd.read_sql(query, con)
    if data.iloc[0]["company"] is None:
        return pd.DataFrame()
    else:
        return data


def get_unpaid_invoices(connection: pyodbc.Connection) -> pd.DataFrame:
    sql = "select * from invoices where paid = FALSE;"
    unpaid_invoices = pd.read_sql(sql, connection)
    return unpaid_invoices


def get_accounts_payable_status(connection: pyodbc.Connection) -> pd.DataFrame:
    unpaids = get_unpaid_invoices(connection)


def add_invoice(
    invoice_data: list[Any], connection: pyodbc.Connection
) -> None:
    """Adds an invoice to the invoice table in the db.

    invoice_data: [vendor, inv_num, amount, cc, cc_user]
    """
    date_added = datetime.now()
    str_date_added = date_added.strftime("%Y-%m-%d")
    ym = date_added.strftime("%Y%m")
    cc = 1 if invoice_data[3] else 0
    cc_user = invoice_data[4] if invoice_data[4] else "NULL"
    if cc_user != "NULL":
        cc_user = "'" + cc_user + "'"

    statement = f"""INSERT INTO invoices (
    date_added, vendor, inv_num, amount, ym, cc, cc_user
    )
    VALUES (
        '{str_date_added}',
        '{invoice_data[0]}',
        '{invoice_data[1]}', 
        {invoice_data[2]},
        {ym},
        {cc},
        {cc_user}
    );"""

    connection.execute(statement)
    connection.commit()


def check_vendor(vendor: str, conn: pyodbc.Connection) -> bool:
    sql = f"SELECT * FROM vendors WHERE vendor = '{vendor}';"
    curs = conn.execute(sql)
    if curs.fetchone():
        return True
    else:
        return False


def search_possible_vendors(
    vendor: str, conn: pyodbc.Connection
) -> pd.DataFrame:
    sql = f"SELECT * FROM vendors WHERE vendor LIKE '%{vendor}%';"
    results = pd.read_sql(sql, conn)
    return results


def view_unpaid_invoices(conn: pyodbc.Connection) -> pd.DataFrame:
    sql = "select * from invoices where paid = FALSE;"
    results = pd.read_sql(sql, conn)
    return results


def construct_sql_query(table: str, cols: list[str] = None, **kwargs) -> str:
    """Constructs a sql query that pulls all data from table matching the
    criteria submitted.

    Criteria submitted as keyword args, each col as the arg name and the
    parameter as the value desired.

    If wildcards are included in the parameter, the query will use a LIKE clause
    for that column.
    """

    sql_cols = "*"
    two_tables = False
    if cols:
        two_tables = check_for_two_tables(cols)
        sql_cols = parse_cols_to_sql(cols, two_tables)

    base = f"select {sql_cols} from " + table

    if two_tables:
        join_clause = "left join vendors on invoices.vendor = vendors.vendor"
        base = " ".join([base, join_clause])

    if kwargs:
        base += " where"
        cols = list(kwargs.keys())
        for col in cols:
            detailed_col_str = f"{col_to_table_map[col]}.{col}"
            use_col = col
            if two_tables:
                use_col = detailed_col_str

            clause = get_clause_from_param(kwargs[col], use_col)
            base = " ".join([base, clause])

            if len(cols) >= 2 and cols.index(col) != len(cols) - 1:
                base = "".join([base, " and"])

    base = "".join([base, ";"])
    return base


def parse_cols_to_sql(cols: list[str], two_tables=False) -> str:
    """Formats a list of cols to be selected from sql table to sql string."""
    if two_tables:
        detailed_cols = []
        for col in cols:
            col_str = f"{col_to_table_map[col]}.{col}"
            detailed_cols.append(col_str)
        sql_cols = ", ".join(detailed_cols)
    else:
        sql_cols = ", ".join(cols)

    return sql_cols


def get_clause_from_param(val: Any, col: str) -> str:
    if isinstance(val, str):
        clause = " ".join([col, parse_col_param_to_sql(val)])
    elif isinstance(val, int) or isinstance(val, float):
        clause = f"{col} = {str(val)}"
    elif isinstance(val, bool):
        clause = f"{col} = {"1" if val else "0"}"
    elif isinstance(val, tuple):
        clause = ""
        for i in range(len(val)):
            clause_i = get_clause_from_param(val[i], col)
            clause = "".join([clause, clause_i])

            if len(val) >= 2 and i != len(val) - 1:
                clause = " ".join([clause, "and "])

    return clause


def parse_col_param_to_sql(param: Any) -> str:
    if "%" in param or "_" in param:
        clause = "like '" + param + "'"
    elif "<" in param or ">" in param:
        regex = re.match(r"(?P<op>[<>=]+)(?P<num>\d+)", param)
        operator = regex.group("op")
        num = regex.group("num")
        clause = operator + " " + num
    else:
        clause = "= '" + param + "'"

    return clause


def check_for_two_tables(cols: list[str]) -> bool:
    """Returns True if columns span both invoices and vendors tables, false
    otherwise"""

    count_invoices = 0
    count_vendors = 0
    for col in cols:
        if col == "vendor":
            continue
        elif col in invoices_cols:
            count_invoices += 1
        else:
            count_vendors += 1

    if count_vendors > 0 and count_invoices > 0:
        return True
    else:
        return False


def parse_user_response(
    user_response: str,
    table: str,
    table_cols: list[str],
    con: pyodbc.Connection,
) -> np.int8:
    """Parses user response and starts relevant routine."""

    if user_response == "":
        return np.int8(1)

    try:
        regex = re.match(r"(\w+):?\s?([\w\.\s\_\(\)&]+)?", user_response)
        command = regex.group(1)
        param = regex.group(2)
    except:
        return np.int8(1)

    if command in table_cols:
        return filter_table(
            table=table, cols=table_cols, **{command: param}, con=con
        )
    elif re.match(r"\d+", command):
        return invoice_details(int(command), con)
    elif command == "export":
        return (np.int8(3), param)
    elif command == "IDB":
        return filter_table(table=table, cols=table_cols, idb=True, con=con)
    elif command == "mark":
        return (np.int8(4), param)

    return np.int8(0)


def filter_table(
    table: str, cols: list[str], con: pyodbc.Connection, **kwargs
):
    sql = construct_sql_query(table=table, cols=cols, paid=False, **kwargs)
    new_data = pd.read_sql(sql, con=con, index_col="id")
    return new_data


def check_for_duplicate_entry(
    vendor: str, inv_num: str, con: pyodbc.Connection
) -> bool:

    query = f"""select vendor,
    inv_num
    from invoices
    where vendor = '{vendor}'
    and inv_num = '{inv_num}';
    """

    cursor = con.execute(query)
    if cursor.fetchone():
        return True
    else:
        return False


def invoice_details(id: int, con: pyodbc.Connection):
    sql = construct_sql_query("invoices", id=id)
    invoice_data = pd.read_sql(sql=sql, con=con, index_col="id")
    return (np.int8(2), invoice_data)


def get_pmt_file_data(pmt_type: str, con: pyodbc.Connection) -> pd.DataFrame:
    cols = [
        "id",
        "vendor",
        "inv_num",
        "amount",
        "ach_aba",
        "ach_acct_no",
        "ach_vendor",
        "template",
        "approved",
        "company",
        "pmt_type",
        "cc",
        "paid",
    ]
    sql = construct_sql_query(
        "invoices",
        cols=cols,
        pmt_type=pmt_type,
        cc=False,
        paid=False,
        approved=True,
    )
    data = pd.read_sql(sql, con, "id")
    return data


def update_value(
    id: int, column: str, value: str, connection: pyodbc.Connection
) -> None:
    if column in invoices_int_cols:
        update_statement = f"""update invoices
        set {column} = {value} where id = {id};"""
    else:
        update_statement = f"""update invoices
        set {column} = '{value}' where id = {id};"""

    connection.execute(update_statement)
    connection.commit()


def remove_item(id: int, connection: pyodbc.Connection) -> None:
    delete_statement = f"""delete from invoices
    where id = {id};"""
    connection.execute(delete_statement)
    connection.commit()


def add_vendor(
    fields: list[str], values: list[str], conn: pyodbc.Connection
) -> None:
    fields_query_str = ", ".join(fields)
    vals_query_str = ""
    for i in range(len(values)):
        if i in [6, 7]:
            vals_query_str = "".join([vals_query_str, str(values[i]), ", "])
        else:
            vals_query_str = "".join([vals_query_str, "'", values[i], "', "])

    vals_query_str = vals_query_str[:-2]
    print(fields_query_str)
    print(vals_query_str)
    query = (
        f"insert into vendors ({fields_query_str}) values ({vals_query_str});"
    )
    print(query)
    conn.execute(query)
    conn.commit()


def mark_invoices_approved(invoices: pd.Index, conn: pyodbc.Connection):
    index_str = ", ".join([str(i) for i in invoices])
    print(index_str)
    sql = f"update invoices set approved = TRUE where id in ({index_str});"
    conn.execute(sql)
    conn.commit()


def get_summary_data(con: pyodbc.Connection) -> pd.DataFrame:

    sql = """select invoices.id,
    invoices.vendor,
    vendors.qb_mapping,
    invoices.inv_num,
    invoices.amount,
    vendors.company,
    vendors.approver,
    vendors.exp_cat,
    vendors.pmt_type
    from invoices
    left join vendors on invoices.vendor = vendors.vendor
    where invoices.paid = FALSE
    and invoices.cc = FALSE
    order by vendor;"""

    data = pd.read_sql(sql, con, index_col="id")
    return data
