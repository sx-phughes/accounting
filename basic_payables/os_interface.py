# Standard Packages
import os
import numpy as np
import pandas as pd
from pynput.keyboard import Key, Listener

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
        input('Enter to initialize main...')
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
        try:
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
        except ValueError:
            return False
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

        try:
            while True:
                cls()

                invoice_data = self.get_invoice_data()
                if invoice_data == False:
                    break
                elif invoice_data[3] == True:
                    self.cc_invoice(invoice_data)
                else:
                    self.payables.insert_invoice(invoice_data[:-1])

                self.payables.save_workbook()

                add_more = input('Add another invoice (y/n)\n>\t')


                if add_more == 'n':
                    break
        except ValueError:
            self.payables.save_workbook()

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

    def view_invoices(self):
        pd.set_option('display.max_rows', None)        
        print(self.payables)

        input('\n\nPress enter to return to main menu\n')

    def remove_invoice(self):
        pd.set_option('display.max_rows', None)
        print(self.payables)

        index_to_remove = int(input('Input index of invoice to remove'))
        
        self.payables.remove_invoice(index_to_remove)
        self.payables.save_workbook()
        
        input('Invoice removed. Enter to return to main menu')

def __main__():
    OsInterface()

__main__()
