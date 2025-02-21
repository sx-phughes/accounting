import os, shutil
import numpy as np
import pandas as pd
from datetime import datetime

def cls():
    os.system('cls')

class PayablesWorkbook(pd.DataFrame):
    def __init__(self, path):
        super().__init__(pd.read_excel(path, 'Invoices'))

class OsInterface():
    payables_path = 'C:/gdrive/Shared drives/Accounting/Payables'

    def __init__(self):
        self.get_workbook_date()
        self.get_workbook_stem()
        self.wb_path = OsInterface.payables_path + self.stem + self.f_name
        self.df = PayablesWorkbook(self.wb_path.replace('.xlsx', '.xlsm'))
        self.main()

    def main(self):
        cls()

        print('Invoice Input Main Menu\n')
        options = {
            1: ['Add Invoices', self.add_invoices],
            2: ['View Invoices', self.view_invoices],
            3: ['Remove Invoices', self.remove_invoice],
            4: ['Exit', quit]
        }

        for i in range(len(options.keys())):
            print(f'{str(i + 1)}: {options[list(options.keys())[i]][0]}')

        selected = int(input('\nPlease enter number of option:\n>\t'))

        options[selected][1]()

    def get_workbook_date(self):
        cls()
        payables_date = input('Input Payables Workbook Date (yyyy-mm-dd)\n>\t')
        self.payables_date = payables_date

    def get_workbook_stem(self):
        payables_dt = datetime.strptime(self.payables_date, '%Y-%m-%d')
        year = payables_dt.strftime('%Y')
        month = payables_dt.strftime('%m')

        self.stem = f'/{year}/{year}{month}/{self.payables_date}'
        self.f_name = f'/{self.payables_date} Payables.xlsx'
        
        return self.stem

    def get_invoice_data(self):
        vendor = input('Vendor:\t')
        invoice_num = input('Invoice Number:\t')
        amount = np.float64(input('Invoice Amount:\t'))
        invoice_data = [vendor, invoice_num, amount]
        
        return invoice_data
    
    def insert_invoice(self, invoice_data: list):
        fields = ('Vendor', 'Invoice #', 'Simplex2', 'Expense Category', 'Approved By', 'Payment Type', 'Amount', 'QB Mapping Check', 'Pennies', 'In JPM?', 'In QB?', 'Other Notes', 'Vendor ABA', 'Vendor Account', 'Vendor Name')
        data = ['' for i in fields]
        data[fields.index('Vendor')] = invoice_data[0]
        data[fields.index('Invoice #')] = invoice_data[1]
        data[fields.index('Amount')] = invoice_data[2]

        self.df.loc[len(self.df.index)] = data

        self.move_files(invoice_data[0], invoice_data[1])
    
    def add_invoices(self):
        more = True
        print('CLEAR DOWNLOADS FOLDER BEFORE BEGINNING')
        input()

        while more:
            cls()

            self.insert_invoice(self.get_invoice_data())

            add_more = input('Add another invoice (y/n)\n>\t')

            more = True if add_more == 'y' else False

        self.save_workbook()
        self.df = PayablesWorkbook(self.wb_path)
        self.main()

    def print_invoices(self):
        cls()

        def print_headers():
            print('Index\tVendor\tInvoice #\tAmount')
        
        count = 0
        for i, row in self.df.iterrows():
            if count % 20 == 0:
                print_headers()

            print(f'{str(i)}: {row['Vendor']}\t{row['Invoice #']}\t{row['Amount']}')

            count += 1
    
    def view_invoices(self):
        self.print_invoices()

        input('\n\nPress enter to return to main menu\n')

        self.main()

    def remove_invoice(self):
        self.print_invoices()

        index_to_remove = int(input('Input index of invoice to remove'))
        
        self.df = self.df.drop(index=index_to_remove)
        self.df = self.df.reset_index(drop=True)
        self.save_workbook()
        input('Invoice removed. Enter to return to main menu')

        self.main()

    def save_workbook(self):
        with pd.ExcelWriter(self.wb_path, 'xlsxwriter') as writer:
            self.df.to_excel(writer, 'Invoices', index=False)

    def move_files(self, vendor: str, invoice_num: str):
        # get files in downloads
        downloads = 'C:/Users/phugh/Downloads'
        files = os.listdir(downloads)

        # remove ini files from move
        files = list(filter(lambda x: '.ini' not in x, files))

        # clean invoice num
        invoice_num = invoice_num.replace('/', '_')

        # sort by date added
        #   not doing this for now - be sure to have downloads folder cleared

        # take last files added
        # rename files
        new_f_names = [f'{vendor} - {invoice_num}' + '.' + f_name.split('.')[-1] for f_name in files]

        # move to payables folder
        new_paths = [OsInterface.payables_path + self.stem.replace('/' + self.payables_date, '') + f_name for f_name in new_f_names]
        
        for old, new in zip(files, new_paths):
            shutil.move(downloads + '/' + old, new)

def __main__():
    OsInterface()

__main__()