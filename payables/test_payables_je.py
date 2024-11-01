from PayablesJes import *
import pandas as pd
from datetime import datetime

year = int(input('Year:\n>\t'))
month = int(input('Month:\n>\t'))
day = int(input('Day:\n>\t'))

payables_1031 = JECreator(datetime(year, month, day))

invoices, vendors, coas = payables_1031.file_getter()

bill_dfs = payables_1031.initiator(payables=invoices, vendor_mapping=vendors, account_mappings=coas)

for i in bill_dfs.keys():
    bill_dfs[i].to_csv(f'C:/Users/phughes_simplextradi/Downloads/{i} Bills.csv', index=False)