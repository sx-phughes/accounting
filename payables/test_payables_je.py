from PayablesJes import *
import pandas as pd
from datetime import datetime

payables_930 = JECreator(datetime(2024, 9, 30), 1391)

invoices, vendors, coa = payables_930.file_getter()

bill_df = payables_930.initiator(payables=invoices, vendor_mapping=vendors, account_mapping=coa)

bill_df.to_csv('C:/Users/phughes_simplextradi/Downloads/Test Trading JEs.csv', index=False)