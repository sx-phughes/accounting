from typing import Any
from datetime import datetime
import pyodbc
import pandas as pd
import asyncio


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

    con = pyodbc.connect(conn_string)
    con.setdecoding(pyodbc.SQL_WCHAR, encoding="utf-8")
    con.setencoding(encoding="utf-8")
    return con


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


def view_invoices(conn: pyodbc.Connection) -> pd.DataFrame:
    sql = "select * from invoices where paid = FALSE;"
    results = pd.read_sql(sql, conn)
    return results


def construct_sql_query(table: str, **kwargs) -> str:
    """Constructs a sql query that pulls all data from table matching the
    criteria submitted.

    Criteria submitted as keyword args, each col as the arg name and the
    parameter as the value desired.

    If wildcards are included in the parameter, the query will use a LIKE clause
    for that column.
    """

    base = "select * from " + table
    if kwargs:
        base += " where"
        cols = list(kwargs.keys())
        for col in cols:
            val = kwargs[col]
            if isinstance(val, str):
                clause = " ".join([col, parse_col_param_to_sql(val)])
            elif isinstance(val, int) or isinstance(val, float):
                clause = f"{col} = {str(val)}"
            elif isinstance(val, bool):
                clause = f"{col} = {"1" if val else "0"}"
            base = " ".join([base, clause])


def parse_col_param_to_sql(param: Any) -> str:
    if "%" in param or "_" in param:
        clause = "like '" + param + "'"
    elif "<" in param or ">" in param:
        clause = param
    else:
        clause = "= '" + param + "'"

    return clause
