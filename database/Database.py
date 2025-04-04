import sqlite3
import pyodbc
import pandas as pd

uid = input('DB Username: \n>\t')
pwd = input('DB Password: \n>\t')

conn_string = (
    'DRIVER=MySQL ODBC 9.1 ANSI Driver;'
    'SERVER=singlestore.s;'
    'DATABASE=orders;'
    f'UID={uid};'
    f'PWD={pwd};'
    'charset=utf8mb4'
)

con = pyodbc.connect(conn_string)

con.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
con.setencoding(encoding='utf-8')

params = [
    ['695C10S',	20240104],
    ['ARAP', 20240111],
    ['695CS00',	20240115],
    ['AVJ6', 20240207],
    ['695CS1U',	20240223],
    ['644-06', 20240301],
    ['644-40', 20240326],
    ['695CS1V',	20240411],
    ['695CS2M',	20240402],
    ['644-98', 20240508],
    ['6901SIMP3', 20240513],
    ['ARAT', 20240605],
    ['695CS2P',	20240610],
    ['695CS3S',	20240701],
    ['695CS5Q',	20240812],
    ['695CS6R',	20240916],
    ['AVKF', 20240926],
    ['695CS9S',	20241018],
    ['695CS9T',	20241022],
    ['695M526',	20241105]
]

for i in params:
    account = i[0]
    date = i[1]
    
    query = f'select * from trades where account_code LIKE \'{account}%\' AND trade_date = {date}'
    
    table = pd.read_sql_query(query, con)
    
    table.to_csv(f'C:/Users/phughes_simplextradi/Downloads/{date} - {account}.csv', index=False)