from PayablesJes import *
import pandas as pd
from datetime import datetime

payables_1031 = JECreator(datetime(2024, 10, 31), 1392)

invoices, vendors, coas = payables_1031.file_getter()

bill_dfs = payables_1031.initiator(payables=invoices, vendor_mapping=vendors, account_mappings=coas)

for i in bill_dfs.keys():
    bill_dfs[i].to_csv(f'C:/Users/phughes_simplextradi/Downloads/{i} Bills.csv', index=False)