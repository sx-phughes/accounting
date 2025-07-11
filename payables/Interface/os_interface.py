# Standard Packages
import os
import numpy as np
import pandas as pd
import sys
from typing import Any

# Package Imports
from payables.Interface.payables_wb import PayablesWorkbook
from payables.Interface.functions import *

def cursor_up():
    sys.stdout.flush()
    sys.stdout.write('\033[A')
    sys.stdout.write('\033[A')
    sys.stdout.flush()

def cursor_down():
    sys.stdout.flush()
    sys.stdout.flush()

def cls():
    os.system('cls')

class OsInterface():
    payables_path = 'C:/gdrive/Shared drives/Accounting/Payables'
    data_path = 'C:/gdrive/Shared drives/accounting/patrick_data_files/ap'
    invoice_prompts = [
        'Vendor:\t',
        'Invoice Number:\t',
        'Invoice Amount:\t',
        'Credit card (y/n):\t'
    ]

    ##################
    # initialization #
    ##################
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

    ##############
    # properties #
    ##############
    @property
    def payables(self):
        return self._payables
    
    @payables.setter
    def payables(self, payables_wb: PayablesWorkbook):
        self._payables = payables_wb

    #######################
    # interface mechanics #
    #######################
    def main(self):
        """Main user interface menu function"""
        options = {
            1: ['Add Invoices', self.add_invoices],
            2: ['View All Invoices', self.view_all_invoices],
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

    def make_blank_row(self) -> list[str]:
        """Make a blank row with n entries for n PayablesWorkbook columns"""
        cols = PayablesWorkbook.column_headers
        blank_row = ['' for col in cols]
        return blank_row

    def add_to_row(self, new_row: list):
        """Get new invoice data and copy into a blank row"""
        inputs = self.get_inputs(OsInterface.invoice_prompts)
        for i in range(len(inputs)):
            new_row[i] = inputs[i]

    def get_inputs(self, prompts: list[str], **kwargs) -> list[str|int]:
        """UI for receiving user input for a new invoice"""
        inputs = [0 for i in range(len(prompts))]
        i = 0
        while 0 in inputs:
            i = self.get_user_input(prompts, inputs, i)
            
        
        self.standardize_cc_response(inputs)

        check_result = self.check_vendor(inputs)

        if isinstance(check_result, bool):
            return inputs
        elif isinstance(check_result, list):
            return check_result
        else:
            return self.make_blank_row()
    
    def standardize_cc_response(self, inputs: list[str|int]) -> None:
        try:
            cc_index = self.invoice_prompts.index('Credit card (y/n):\t')
            str_response = inputs[cc_index]
            inputs[cc_index] = self.convert_cc_response_to_bool(str_response)
        except:
            inputs = inputs
        
    def convert_cc_response_to_bool(self, cc_response: str) -> bool:
        if cc_response == 'y':
            return True
        else:
            return False

    def str_list_to_int(self, n: list[str]) -> list[int]:
        n_copy = n.copy()
        list_len = len(n)
        for i in range(list_len):
            if isinstance(n[i], int):
                continue
            int_as_str = ascii(n[i])
            int_as_int = int(int_as_str)
            n_copy[i] = int_as_int
        
        return n_copy
            
    def get_user_input(self, prompts: list[str], input_list: list, 
                       curr_index: int) -> int:

        index = curr_index 
        end = len(prompts) - 1

        print(prompts[index], end='')
        response = input_list[index]

        if response != 0:
            sys.stdout.write(input_list[index])
            sys.stdout.flush()

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
    
    def check_vendor(self, inputs: list[str|int]) -> bool|list[str]:
        if inputs[0] in self.vendors.Vendor.values.tolist():
            return True
        else:
            zero_sum = sum(self.str_list_to_int(inputs)) == 0
            if not zero_sum:
                print("Vendor name does not match any known vendor")
                inputs = self.get_inputs(self.invoice_prompts)
                return inputs
            else:
                return True

    def up_arrow(self, index: int) -> int:
        if index > 0:
            index -= 1
            cursor_up()
        return index

    def down_arrow(self, index: int, end_index: int) -> int:
        if index >= end_index:
           index += 1
           cursor_down()
           # print('', end='\r', flush=True)
        return index

    def add_cc_user(self, invoice_data) -> None:
        """Add credit card user to invoice data for credit card invoices"""
        cc_user_index = PayablesWorkbook.column_headers.index('CC User')
        cc_user = input('Enter initials of CC user:\t')
        invoice_data[cc_user_index] = cc_user

    def is_blank_list(self, data: list) -> bool:
        no_data = True
        i = 0
        while no_data and i in range(len(data)):
            if data[i]:
                no_data = False
            
            i += 1

        return no_data
    
    ######################
    # Invoice management #
    ######################
    def view_all_invoices(self) -> None:
        self.view_invoices(self.payables)
    
    def view_idb_invoices(self) -> None:
        # get table after merge with vendors
        # filter on idb brokers
        # print table
        pass
    
    def print_invoices(self, data: pd.DataFrame) -> None:
        pd.set_option('display.max_rows', None)
        print(data)

    def view_invoices(self, data: pd.DataFrame) -> None:
        """Prints invoices to screen"""
        self.print_invoices(data)

        input('\n\nPress enter to return to main menu\n')

    def remove_invoice(self) -> None:
        """UI for removing one or multiple invoices from the workbook"""
        self.print_invoices()

        index = self.get_index_input()
        if index:
            self.payables.remove_invoice(index)
            self.payables.save_workbook()
            print('Invoice removed.')
        else:
            print('No index provided, so no invoice removed.')
        input('Enter to return to main menu')
        
    def get_index_input(self) -> int:
        """Get index(es) selection from user"""
        prompts = [
            'Input index in the following formats:\n',
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

    def parse_remove_index_input(self, index_str: str) -> list[int]:
        """Parse user input of index(es) to a list"""
        if ',' not in index_str:
            index_list = [int(index_str)]
        elif '-' in index_str:
            index_list = self.index_range_to_list(index_str)
        else:
            index_list = self.split_comma_sep_input(index_str)
        return index_list

    def index_range_to_list(self, s: str) -> list[int]:
        split = s.split('-')
        range_start = int(split[0])
        range_end = int(split[1] + 1)
        index_list = list(range(range_start, range_end))
        return index_list

    def split_comma_sep_input(self, s: str) -> list[int]:
        split = s.split(',')
        trimmed_inputs = [str.strip(index) for index in split]
        int_indexes = [int(index) for index in trimmed_inputs]
        return int_indexes

    def edit_invoice(self) -> None:
        cls()
        self.print_invoices()
        print('\n\n Input invoices to edit\n')
         
    def do_edits(self) -> None:
        indexes = self.get_index_input()
        for index in indexes:
            self.perform_edit(index)

    def perform_edit(self, index: int) -> None:
        data = self.payables.loc[index].copy()
        edit_prompts = self.make_edit_prompts(data)
        inputs = self.get_input(edit_prompts)
        self.payables.loc[index] = inputs

    def make_edit_prompts(self, new_data) -> None:
        table_cols = self.payables.columns.to_list()
        no_nans = self.remove_nans(new_data)
        prompts = [col + ': ' + no_nans[col] for col in table_cols]
        return prompts

    def remove_nans(self, new_data) -> dict[str, str]:
        no_nans = {}
        for col in self.payables.columns.to_list():
            val = self.substitue_nan(new_data[col], '')
            updater = {col: val}
            no_nans.update(updater)
        return no_nans

    def substitue_nan(self, value: Any, sub: Any) -> Any:
        if isinstance(value, float) and np.isnan(value):
            value = sub
        return value

def __main__():
    OsInterface()

