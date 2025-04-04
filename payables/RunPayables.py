from payables.PayablesJes import *
from datetime import datetime
import os


def run_payables():
    year = int(input('Year:\n>\t'))
    month = int(input('Month:\n>\t'))
    day = int(input('Day:\n>\t'))

    batch_date = datetime(year, month, day)

    payables = JECreator(batch_date)

    invoices, vendors, coas = payables.file_getter()

    bill_dfs = payables.initiator(payables=invoices, vendor_mapping=vendors, account_mappings=coas)

    for i in bill_dfs.keys():
        bill_dfs[i].to_csv(f'{os.environ['HOMEPATH'].replace('\\','/')}/Downloads/{i} {batch_date.strftime('%Y-%m-%d')} Bills.csv', index=False)