import pyodbc
import pandas as pd


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
