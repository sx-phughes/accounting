# Standard Packages
import os
import numpy as np
import pandas as pd

# Package Imports
from payables_wb import PayablesWorkbook
from functions import *

def cls():
    os.system('cls')

class OsInterface():
    payables_path = 'C:/gdrive/Shared drives/Accounting/Payables'

    def __init__(self):
        self.payables = PayablesWorkbook(date=self.ui_workbook_date())
        self.vendors = pd.read_excel('C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx', 'Vendors')
        self.main()

    @property
    def payables(self):
        return self._payables
    
    @payables.setter
    def payables(self, payables_wb: PayablesWorkbook):
        self._payables = payables_wb

    def main(self):
        while True:
            cls()

            print('Invoice Input Main Menu\n')
            options = {
                1: ['Add Invoices', self.add_invoices],
                2: ['View Invoices', self.view_invoices],
                3: ['Remove Invoices', self.remove_invoice],
                4: ['Exit']
            }

            for i in range(len(options.keys())):
                print(f'{str(i + 1)}: {options[list(options.keys())[i]][0]}')

            selected = int(input('\nPlease enter number of option:\n>\t'))

            if selected == list(options.keys())[-1]:
                break
            else:
                options[selected][1]()

    def ui_workbook_date(self):
        cls()
        
        while True:
            payables_date = input('Input Payables Workbook Date (yyyy-mm-dd)\n>\t')
            
            if check_date(payables_date):
                break
            else:
                print('Invalid date, try again')
        
        return payables_date

    def get_invoice_data(self):
        vendor = input('Vendor:\t')
        invoice_num = input('Invoice Number:\t')
        amount = np.float64(input('Invoice Amount:\t'))
        CC = input('Credit card (y/n):\t')
        if CC == 'y':
            CC = True
        else:
            CC = False

        invoice_data = [vendor, invoice_num, amount, CC]
        
        return invoice_data
    
    def insert_invoice(self, invoice_data: list):
        self.payables.loc[len(self.payables.index)] = invoice_data

        self.payables.move_files(invoice_data[0], invoice_data[1])
    
    def add_invoices(self):
        print('CLEAR DOWNLOADS FOLDER BEFORE BEGINNING')
        input()

        while True:
            cls()

            invoice_data = self.get_invoice_data()
            if invoice_data[3] == True:
                self.cc_invoice(invoice_data)
            else:
                self.payables.insert_invoice(invoice_data[:-1])

            add_more = input('Add another invoice (y/n)\n>\t')
            
            if add_more == 'n':
                break

        self.payables.save_workbook()

    def cc_invoice(self, invoice_data):
        cc_user = input('Enter initials of CC user:\t')
        vendor = cc_user + ' - ' + invoice_data[0]
        self.payables.move_files(vendor, invoice_data[1])

    def print_invoices(self):
        cls()

        field_lens = {
            'Index': 5,
            'Vendor': 20,
            'Invoice #': 20,
            'Amount': 10,
        }
        
        
        def print_headers():
            print(f'{self.turn_to_field(field_lens['Index'], 'Index')} {self.turn_to_field(field_lens['Vendor'], 'Vendor')} {self.turn_to_field(field_lens['Invoice #'], 'Invoice #')} {self.turn_to_field(field_lens['Amount'], 'Amount')}')
        
        count = 0
        for i, row in self.payables.iterrows():
            if count % 20 == 0:
                print_headers()

            fields = [
                self.turn_to_field(field_lens['Index'], str(i)),
                self.turn_to_field(field_lens['Vendor'], row['Vendor']),
                self.turn_to_field(field_lens['Invoice #'], row['Invoice #']),
                self.turn_to_field(field_lens['Amount'], str(row['Amount']))
            ]
            
            print(' '.join(fields))

            count += 1
    
    def turn_to_field(self, field_len, datum: str) -> str:
        spaces_len = field_len - len(datum)
        if spaces_len < 0:
            field = datum[0:(field_len + 1)]
        else:
            field = datum + spaces_len * ' '
        
        return field
    
    def view_invoices(self):
        pd.set_option('display.max_rows', None)        
        print(self.payables)
                  # self.print_invoices()

        input('\n\nPress enter to return to main menu\n')

    def remove_invoice(self):
        pd.set_option('display.max_rows', None)
        print(self.payables)
                  # self.print_invoices()

        index_to_remove = int(input('Input index of invoice to remove'))
        
        self.payables.remove_invoice(index_to_remove)
        self.payables.save_workbook()
        
        input('Invoice removed. Enter to return to main menu')

def __main__():
    OsInterface()

__main__()
