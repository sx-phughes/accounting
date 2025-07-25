import pandas as pd
from datetime import datetime, timedelta
import os, re

class PayablesWorkbook(pd.DataFrame):
    def __init__(self, path):
        super().__init__(pd.read_excel(path, 'Invoices'))

    def invoice_numbers(self):
        df = self['Vendor'] + self['Invoice #']

        return list(df.values)
    
def search_for_dupe_payments(curr_payables_batch_date: str, n_months: int, save_to_path: str = './'):
    '''
    Search for duplicate payments in n prior months\n
    Args:\n
    \tcurr_payables_batch_date: str, payables batch date formatted yyyy-mm-dd\n
    \tn_monts: int, number of months prior to search
    '''
    payables_root = 'C:/gdrive/Shared drives/accounting/Payables'



    # Get data related to current payables batch
    payables_dt = datetime.strptime(curr_payables_batch_date, '%Y-%m-%d')
    curr_payables_stem = f'{payables_dt.year}/{payables_dt.strftime('%Y%m')}/{payables_dt.strftime('%Y-%m-%d')}/{payables_dt.strftime('%Y-%m-%d')} Payables.xlsm'
    curr_payables_df = pd.read_excel(payables_root + '/' + curr_payables_stem, 'Invoices')
    curr_payables_df['Concat'] = curr_payables_df['Vendor'] + ',' + curr_payables_df['Invoice #'].astype(str)
    curr_invoices = tuple(curr_payables_df['Concat'].values)


    # Create a list of datetimes for each month to search in
    months_to_search = [payables_dt - timedelta(30 * i) for i in range(1, n_months + 1)] + [payables_dt]
    


    # Loop through the datetimes and grab the folders with payables batch data
    payables_folders = []

    for dt in months_to_search:
        stem = f'{dt.year}/{dt.strftime('%Y%m')}'

        dir_contents = os.listdir(payables_root + '/' + stem)

        # filter checks for items that fit the date pattern and are not equal to the current batch
        folders = list(filter(lambda x: re.match(r'\d{4}-\d{2}-\d{2}', x) and x != payables_dt.strftime('%Y-%m-%d'), dir_contents))

        payables_folders.append([stem, folders])
    


    # Create the file stems
    payables_file_stems = []

    for f_grp in payables_folders:
        # f_grp = [stem, list[folders]]
        for dt in f_grp[1]:
            payables_file_stems.append(f_grp[0] + '/' + dt + '/' + dt + ' Payables.xlsm')



    # Pull concatenated values of [Vendor],[Invoice #] and compile to a list
    old_invoices = []

    for stem in payables_file_stems:
        df = pd.read_excel(payables_root + '/' + stem, 'Invoices')

        vendor_invoice_df = df[['Vendor', 'Invoice #']].copy()
        vendor_invoice_df['Concat'] = vendor_invoice_df['Vendor'] + ',' + vendor_invoice_df['Invoice #'].astype(str)

        old_invoices.append([stem, list(vendor_invoice_df['Concat'].values)])



    # Check for duplicate values and append to a dupe list
    dupe_invoices = []

    for invoice in curr_invoices:
        for group in old_invoices:
            # group = [stem, list[invoices]]
            if invoice in group[1]:
                dupe_invoices.append([group[0], invoice])
            else:
                continue
    


    # Reparse the data
    dupe_invoice_stems, dupe_invoice_vendors, dupe_invoice_numbers = [], [], []
    
    for item in dupe_invoices:
        vendor, invoice_num = item[1].split(',')
        dupe_invoice_stems.append(item[0])
        dupe_invoice_vendors.append(vendor)
        dupe_invoice_numbers.append(invoice_num)



    # Format data to a dataframe and save to csv
    data = {
        'Stem': dupe_invoice_stems,
        'Vendor': dupe_invoice_vendors,
        'Invoice': dupe_invoice_numbers
    }

    dupe_df = pd.DataFrame(data)

    dupe_df.to_csv(save_to_path + '/Duplicate Invoices.csv', index=False)


def __main__():
    date = input('Input date of payables batch to check for dupes (yyyy-mm-dd):\n>\t')
    n_months = input('Input number of months to check back:\n>\t')
    save_path = input('Input save path for dupe invoice check (optional, defaults to pwd):\n>\t')

    search_for_dupe_payments(date, int(n_months), save_path)


__main__()