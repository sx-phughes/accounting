# Standard Packages
import os
import numpy as np
import pandas as pd
import sys
import time

# Package Imports
from basic_payables.payables_wb import PayablesWorkbook
from basic_payables.functions import *
from basic_payables.test_gui import cursor_up, cursor_down

def cls():
    os.system('cls')

class OsInterface():
    payables_path = 'C:/gdrive/Shared drives/Accounting/Payables'

    # initialization
    def __init__(self):
        self.payables = PayablesWorkbook(date=self.ui_workbook_date())
        self.vendors = pd.read_excel('C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx', 'Vendors')
        self.main()

    def ui_workbook_date(self):
        """User interface for getting payables date"""
        cls()
        
        while True:
            payables_date = input('Input Payables Workbook Date (yyyy-mm-dd)\n>\t')
            if check_date(payables_date):
                break
            else:
                print('Invalid date, try again')
        return payables_date
    
    # properties
    @property
    def payables(self):
        return self._payables
    
    @payables.setter
    def payables(self, payables_wb: PayablesWorkbook):
        self._payables = payables_wb

    # class methods
    def main(self):
        """Main user interface menu function"""
        options = {
            1: ['Add Invoices', self.add_invoices],
            2: ['View Invoices', self.view_invoices],
            3: ['Remove Invoices', self.remove_invoice],
            4: ['Exit']
        }
        while True:
            cls()

            print('Invoice Input Main Menu\n')
            self.print_main_menu(options)

            selected = 0
            while not selected:
                selected = self.main_menu_input()

            if selected == list(options.keys())[-1]:
                break
            else:
                options[selected][1]()

    def main_menu_input(self):
        """Receive user input for main menu selection"""
        selection = input('\nPlease enter number of option:\n>\t')
        if re.match(r'\d+', selection):
            return int(selection)
        else:
            print('Bad option!')

    def print_main_menu(self, options: dict):
        for i in range(len(options.keys())):
            print(f'{str(i + 1)}: {options[list(options.keys())[i]][0]}')

    def add_invoices(self):
        """Loop for adding invoices to the payables table"""
        self.warn_clear_downloads()
        try:
            while True:
                cls()

                try:
                    invoice_data = self.get_invoice_data()
                except EOFError:
                    invoice_data = False
                if invoice_data == False:
                    break
                elif invoice_data[3] == True:
                    self.add_cc_user(invoice_data)
                self.payables.insert_invoice(invoice_data)

                add_more = input('Add another invoice (y/n)\n>\t')
                if add_more == 'n':
                    break
        except ValueError:
            self.payables.save_workbook()

    def warn_clear_downloads(self):
        print('CLEAR DOWNLOADS FOLDER BEFORE BEGINNING')
        input()

    def get_invoice_data(self):
        new_row = self.make_blank_row()
        self.add_to_row(new_row)

        if not self.is_blank_list(new_row):
            return new_row 
        else:
            return False

    def make_blank_row(self):
        """Make a blank row with n entries for n PayablesWorkbook columns"""
        cols = PayablesWorkbook.column_headers
        blank_row = ['' for col in cols]
        return blank_row

    def add_to_row(self, new_row: list):
        """Get new invoice data and copy into a blank row"""
        inputs = self.get_inputs()
        for i in range(len(inputs)):
            new_row[i] = inputs[i]

    def get_inputs(self):
        """UI for receiving user input for a new invoice"""
        # vendor = input('Vendor:\t')
        # invoice_num = input('Invoice Number:\t')
        # amount = np.float64(input('Invoice Amount:\t'))
        # credit_card = input('Credit card (y/n):\t')
        # if credit_card == 'y':
        #     credit_card = True
        # else:
        #     credit_card = False
        # return (vendor, invoice_num, amount, credit_card)

        # TEST NAVIGABLE INPUT 
        prompts = [
            'Vendor:\t',
            'Invoice Number:\t',
            'Invoice Amount:\t',
            'Credit card (y/n):\t'
        ]
        inputs = [0, 0, 0, 0]
        i = 0
        while 0 in inputs:
            i = self.get_user_input(prompts, inputs, i)
            
        if inputs[2] == 'y':
            inputs[2] = True
        else:
            inputs[2] = False

        
        return inputs

    def get_user_input(self, prompts: list[str], input_list: list, curr_index: int):
        index = curr_index 
        collected = 0
        end = len(prompts) - 1

        print(prompts[index], end='')
        data = input()
        if data == 'k':
            index = self.up_arrow(index)
            print('', end='\r')
        elif data == 'j':
            index = self.down_arrow(index, end)
            print('', end='\r')
        else:
            input_list[index] = data 
            index += 1

        return index 

    def up_arrow(self, index: int):
        if index > 0:
            index -= 1
            cursor_up()
        return index

    def down_arrow(self, index: int, end_index: int):
        if index >= end_index:
           index += 1
           cursor_down()
           # print('', end='\r', flush=True)
        return index


    def add_cc_user(self, invoice_data):
        """Add credit card user to invoice data for credit card invoices"""
        cc_user_index = PayablesWorkbook.column_headers.index('CC User')
        cc_user = input('Enter initials of CC user:\t')
        invoice_data[cc_user_index] = cc_user

    def is_blank_list(self, data: list):
        no_data = True
        i = 0
        while no_data and i in range(len(data)):
            if data[i]:
                no_data = False
            
            i += 1

        return no_data

    def view_invoices(self):
        """Prints invoices to screen"""
        pd.set_option('display.max_rows', None)        
        print(self.payables)

        input('\n\nPress enter to return to main menu\n')

    def remove_invoice(self):
        """UI for removing one or multiple invoices from the workbook"""
        pd.set_option('display.max_rows', None)
        print(self.payables)

        index = self.get_index_input()
        if index:
            self.payables.remove_invoice(index)
            self.payables.save_workbook()
            print('Invoice removed.')
        else:
            print('No index provided, so no invoice removed.')
        input('Enter to return to main menu')
        
    def get_index_input(self):
        """Get index(es) for removal"""
        prompts = [
            'Input index to remove in the following formats:\n',
            '\tSingle index, e.g., 10\n',
            '\tComma-separated list, e.g. 10,15,29\n',
            '\tRange of indexes, e.g. 10-15\n',
            '>\t'
        ]
        index_to_remove = input(''.join(prompts))
        try:
            parsed_index = self.parse_remove_index_input(index_to_remove)
        except:
            parsed_index = 0
        return parsed_index

    def parse_remove_index_input(self, index_str: str):
        """Parse user input of index(es) to a list"""
        if ',' not in index_str:
            index_list = [int(index_str)]
        elif '-' in index_str:
            index_list = self.index_range_to_list(index_str)
        else:
            index_list = self.split_comma_sep_input(index_str)
        return index_list

    def index_range_to_list(self, s: str):
        split = s.split('-')
        range_start = int(split[0])
        range_end = int(split[1] + 1)
        index_list = list(range(range_start, range_end))
        return index_list

    def split_comma_sep_input(self, s: str):
        split = s.split(',')
        trimmed_inputs = [str.strip(index) for index in split]
        int_indexes = [int(index) for index in trimmed_inputs]
        return int_indexes

def __main__():
    OsInterface()

