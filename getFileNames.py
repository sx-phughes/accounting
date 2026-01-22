import pandas as pd
import os
import re

dir = "C:/gdrive/Shared drives/accounting/Simplex Trading/Audit/2025/2025 Planning/SURALINK 26 - Legal Invoices"
os.chdir(dir)

pattern = r"([\w\s]+) - (\d+)\.\w+"
invoices = {"vendor": [], "inv_num": []}

for i in os.listdir():
    result = re.match(pattern, i)
    if result is None:
        continue
    vendor = result.groups()[0]
    inv_num = result.groups()[1]
    invoices["vendor"].append(vendor)
    invoices["inv_num"].append(inv_num)

inv_data = pd.DataFrame(data=invoices).to_csv("./inv_file_info.csv")
