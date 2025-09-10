from payables.nacha.NachaConstructor import *
from payables.nacha.CheckDuplicates import check_duplicates
from payables.DupePayments import search_for_dupe_payments
from datetime import datetime
import pandas as pd
import os

def gui_inputs() -> tuple[datetime | bool]:
    vd_year = int(input('VD Year:\n>\t'))
    vd_month = int(input('VD Month:\n>\t'))
    vd_day = int(input('VD Day:\n>\t'))

    pb_year = int(input('Payables Year:\n>\t'))
    pb_month = int(input('Payables Month:\n>\t'))
    pb_day = int(input('Payables Day:\n>\t'))
    
    debug = input('Debug? y/n\n>\t')
    if debug == 'y':
        debug = True
    else:
        debug = False
    
    vd = datetime(vd_year, vd_month, vd_day)
    pb = datetime(pb_year, pb_month, pb_day)
    
    inputs = (vd, pb, debug)
    return inputs
    

def run_nacha_batch(payables_date, valuedate, debug):
    """UI Function for converting standard payables sheet into NACHA ACH batch
    files for import into JPM Access
    """
    data_types = {
        'Vendor': str,
        'Invoice #': str,
        'Vendor ABA': str,
        'Vendor Account': str,
        'Vendor Name': str,
        'Simplex2': str,
        'Expense Category': str,
        'Approved By': str,
        'Payment Type': str,
        'Amount': float
    }

    value_date = valuedate.strftime('%y%m%d')

    payables_path = "/".join([
        f'C:/gdrive/Shared drives/accounting/Payables/',
        f"{payables_date.strftime('%Y')}",
        f"{payables_date.strftime('%Y%m')}",
        f"{payables_date.strftime('%Y-%m-%d')}",
        f"{payables_date.strftime('%Y-%m-%d')} Payables.xlsm"
    ])

    pb_date_string = payables_date.strftime("%Y-%m-%d")

    dupes = search_for_dupe_payments(
        pb_date_string,
        4, 
        "C:\gdrive\My Drive\dupe_pmts"
    )
    if len(dupes.index) > 0:
        print("Dupe payments present; please correct and rerun payables.")
        input()
        quit()

    payables = pd.read_excel(payables_path, 'Invoices', dtype=data_types)
    payables = payables.loc[payables['Payment Type'] == 'ACH'].copy()
    payables = check_duplicates(payables)

    ### value date must be formatted "YYMMDD"
    nacha_file = NachaConstructor(payables, value_date, debug)
    files = nacha_file.main()
    counter = 0
    for i in files:
        with open(
            file="/".join([
                f"{os.environ['HOMEPATH'].replace('\\','/')}",
                "Downloads",
                f"{value_date}_ACHS_{
                    list(NachaConstructor.company_names.keys())[counter]
                }.txt"
            ]),
            mode='w'
        ) as file:
            file.write(i.__str__())
        counter += 1

def nacha_main():
    results = gui_inputs()
    run_nacha_batch(**results)