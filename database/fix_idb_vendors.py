import pandas as pd
import pyodbc
from InvoicesToMySQL import connect_to_accounting


con = connect_to_accounting()
old_vendors = pd.read_excel(
    io="C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx",
    sheet_name="Vendors",
)

idb_brokers = old_vendors.loc[
    old_vendors["IDB Broker"] == "Yes", "Vendor"
].values

vendor_str = "'" + "', '".join(idb_brokers) + "'"

sql = f"update vendors set idb = TRUE where vendor in ({vendor_str});"

con.execute(sql)
con.commit()
