# Standard Packages
import os
import numpy as np
import pandas as pd
import re
import sys
from typing import Any
import shutil
from datetime import datetime
import importlib

# Package Imports
sys.path.append(os.environ["HOMEPATH"] + "/accounting/payables")
from Interface.payables_wb import PayablesWorkbook, get_col_index
from Interface.functions import *
import nacha as nacha
import DupePayments as DupePayments


class OsInterface:

    ###################
    # Class variables #
    ###################
    payables_path = "C:/gdrive/Shared drives/Accounting/Payables"
    data_path = "C:/gdrive/Shared drives/accounting/patrick_data_files/ap"
    invoice_prompts = [
        "Vendor:",
        "Invoice Number:",
        "Invoice Amount:",
        "Credit card:",
    ]
    prompt_types = [
        "str",
        "str",
        "float64",
        "bool"
    ]


    ##################
    # initialization #
    ##################
    def __init__(self, payables_date: str = None, debug: bool=False):
        self.vendors = pd.read_excel(
            "C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx",
            "Vendors",
        )
        self.preserved_downloads = 0

        if payables_date is None:
            self.date = self.ui_workbook_date()
            self.payables = PayablesWorkbook(date=self.date)
            self.main()
        else:
            self.payables = PayablesWorkbook(date=payables_date)
        
        if debug:
            self.date = payables_date
            self.parse_date(payables_date)
            # self.main()
            
        
    ##################
    # date functions #
    ##################
    def ui_workbook_date(self):
        """User interface for getting payables date"""
        cls()
        while True:
            payables_date = input("Input Payables Workbook Date (yyyy-mm-dd)\n>\t")
            if check_date(payables_date):
                self.parse_date(payables_date)
                break
            else:
                print("Invalid date, try again")
        self.dt_date = datetime.strptime(payables_date, "%Y-%m-%d")
        return payables_date
    
    def parse_date(self, date: str) -> None:
        """Parses date pieces from yyyy-mm-dd string and assigns pieces to properties"""
        pattern = r"(\d{4})-(\d{2})-(\d{2})"
        re_match = re.match(pattern, date)
        if re_match is None:
            raise ValueError(f"Date string '{date}' improperly formatted; must be yyyy-mm-dd")
        date_pieces = re_match.groups()
        self.year, self.month, self.day = date_pieces[0:3]


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
            1: ["Add Invoices", self.add_invoices],
            2: ["View/Edit Invoices", self.view_all_invoices],
            3: ["Switch Payables Workbook", self.switch_books],
            4: ["Create Payment Files", self.make_payment_files],
            5: ["Exit"],
        }
        while True:
            cls()

            print("Payables Main Menu\n")
            self.print_main_menu_status()
            self.print_main_menu(options)

            selected = 0
            while not selected:
                selected = self.main_menu_input()

            if selected == list(options.keys())[-1]:
                cls()
                break
            else:
                options[selected][1]()
    
    def switch_books(self) -> None:
        self.payables.save_workbook()
        self.date = self.ui_workbook_date()
        self.payables = PayablesWorkbook(date=self.date)
        
    def print_main_menu_status(self) -> None:
        print_list = [
            f"Current Workbook {self.date}",
            f"Total # of invoices: {len(self.payables.index)!s}",
            "Company Totals:"
        ]
        with_vendors = self.payables.merge_vendors()
        for co in with_vendors['Company'].unique():
            co_total_invoiced = with_vendors.loc[with_vendors["Company"] == co, 'Amount'].sum()
            co_string = f"\t{co:15}: ${co_total_invoiced:,.2f}"
            print_list.append(co_string)
        
        for line in print_list:
            print(line)
        print("\n")

    def main_menu_input(self):
        """Receive user input for main menu selection"""
        selection = input("\nPlease enter number of option:\n>\t")
        if re.match(r"\d+", selection):
            return int(selection)
        else:
            print("Bad option!")

    def print_main_menu(self, options: dict):
        for i in range(len(options.keys())):
            print(f"{str(i + 1)}: {options[list(options.keys())[i]][0]}")


    ################
    # Add invoices #
    ################
    def add_invoices(self):
        """Loop for adding invoices to the payables table"""
        print("Move downloads to temp folder? (y/n)")
        resp = input(">\t")
        if resp == "y":
            self.preserve_downloads()
            self.preserved_downloads = 1
    
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

                paid_status_index = get_col_index("Paid")
                invoice_data[paid_status_index] = False

                self.payables.insert_invoice(invoice_data)

                add_more = input("\nAdd another invoice (y/n)\n>\t")
                if add_more == "n":
                    break
        except ValueError:
            self.payables.save_workbook()

        if self.preserved_downloads:
            self.restore_downloads()
            self.preserved_downloads = 0

    def preserve_downloads(self) -> None:
        try:
            os.mkdir("./.tempdownloads")
        except FileExistsError:
            pass

        self.move_all_files("./Downloads", "./.tempdownloads/")

    def restore_downloads(self) -> None:
        self.move_all_files("./.tempdownloads", "./Downloads/")
        shutil.rmtree("./.tempdownloads")

    def move_all_files(self, source: str, dest: str) -> None:
        files = os.listdir(source)
        for file in files:
            shutil.move(src=source + f"/{file}", dst=dest + f"/{file}")

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
        blank_row = ["" for col in cols]
        return blank_row

    def add_to_row(self, new_row: list):
        """Get new invoice data and copy into a blank row"""
        inputs = self.get_inputs(OsInterface.invoice_prompts)
        for i in range(len(inputs)):
            new_row[i] = inputs[i]

    def get_inputs(self, prompts: list[str], **kwargs) -> list[str | int]:
        """UI for receiving user input for a new invoice"""
        inputs = [0 for i in range(len(prompts))]
        i = 0
        while 0 in inputs:
            i = self.get_user_input(prompts, inputs, i)

        self.set_input_types(inputs)

        check_result = self.add_invoice_vendor_check(inputs)
        if isinstance(check_result, bool) and check_result:
            return inputs
        elif isinstance(check_result, list):
            return check_result
        else:
            return self.make_blank_row()
        
    def set_input_types(
        self, inputs: list[str | int]) -> list[str | int | bool]:

        zipped_inputs_and_types = zip(
            inputs, OsInterface.prompt_types
        )
        self.fix_cc_input(inputs)

        index = 0
        for val, val_type in zipped_inputs_and_types:
            inputs[index] = set_type(val, val_type)
            index += 1
            
    def fix_cc_input(self, inputs: list[str | int]) -> list[str | int]:
        cc_index = self.get_input_index("Credit card")
        cc_input = inputs[cc_index]
        inputs[cc_index] = self.swap_cc_input(cc_input)
        
    def swap_cc_input(self, cc_val: str) -> str:
        new_val = '' 
        if cc_val == "y":
            new_val = cc_val
        return new_val
    
    def get_input_index(self, col: str) -> int:
        with_stub = col + ":"
        return OsInterface.invoice_prompts.index(with_stub)

    def str_list_to_int(self, n: list[str]) -> list[int]:
        n_copy = n.copy()
        list_len = len(n)
        for i in range(list_len):
            val = n[i]
            if isinstance(val, int) or isinstance(val, np.float64):
                continue

            str_as_int = self.string_to_int(n[i])
            n_copy[i] = str_as_int

        return n_copy

    def string_to_int(self, string: str) -> int:
        sum = 0
        for char in string:
            sum += ord(char)
        return sum

    def get_user_input(
        self, prompts: list[str], input_list: list, curr_index: int
    ) -> int:

        index = curr_index
        end = len(prompts) - 1

        padded = self.pad_string(prompts[index], 20)
        print(padded, end="")
        response = input_list[index]

        if response != 0:
            input_len = len(input_list[index])
            print(input_list[index], end='', flush=True)
            print(f"\033[{input_len}D", end='', flush=True)

        data = input()
        if data == "k":
            index = self.up_arrow(index)
            print("", end="\r", flush=True)
        elif data == "j":
            index = self.down_arrow(index, end)
            print("", end="\r")
        elif index != 3 and data == '':
            index += 1
        else:
            input_list[index] = data
            index += 1

        return index

    def add_invoice_vendor_check(
        self, inputs: list[str | int]) -> bool | list[str]:
        found_vendor = self.validate_vendor(inputs)

        if found_vendor:
            return True
        else:
            zero_sum = sum(self.str_list_to_int(inputs)) == 0
            if not zero_sum:
                inputs = self.get_inputs(OsInterface.invoice_prompts)
                return inputs
            else:
                return True
    
    def validate_vendor(self, inputs: list[str | int] | str) -> bool:
        vendors = self.vendors.Vendor.values.tolist()
        if isinstance(inputs, list):
            found_vendor = inputs[0] in vendors
        else:
            found_vendor = inputs in vendors

        return found_vendor

    def add_cc_user(self, invoice_data) -> None:
        """Add credit card user to invoice data for credit card invoices"""
        cc_user_index = PayablesWorkbook.column_headers.index("CC User")
        cc_user = input("Enter initials of CC user:\t")
        invoice_data[cc_user_index] = cc_user

    def is_blank_list(self, data: list) -> bool:
        no_data = True
        i = 0
        while no_data and i in range(len(data)):
            if data[i]:
                no_data = False

            i += 1

        return no_data


    ####################
    # Input Navigation #
    ####################
    def up_arrow(self, index: int) -> int:
        if index > 0:
            index -= 1
            cursor_up()
        return index

    def down_arrow(self, index: int, end_index: int) -> int:
        if index <= end_index:
            index += 1
            cursor_down()
            # print('', end='\r', flush=True)
        return index
    

    ######################
    # Create NACHA files #
    ######################
    def make_payment_files(self):
        self.check_for_duplicate_payments()

        vd = self.dt_date.strftime("%y%m%d")
        nacha_file = self.get_nacha_constructor(value_date=vd)

        files = nacha_file.main()
        co_names = nacha.NachaConstructor.NachaConstructor.company_names
        list_of_co_names = list(co_names.keys())

        for i in range(len(files)):
            current = files[i]
            company_name = list_of_co_names[i]
            self.write_payment_file(current, vd, company_name)

    def check_for_duplicate_payments(self):
        dupes = DupePayments.search_for_dupe_payments(
            self.date,
            4, 
            "C:/gdrive/My Drive/dupe_pmts"
        )
        if len(dupes.index) > 0:
            print("Dupe payments present; please correct and rerun payables.")
            print("Hit enter to return")
            input()
            raise ValueError("Duplicate invoices present")
        
    def get_nacha_constructor(self, 
        value_date: str):
        """Create nacha file constructor object."""
        
        ach_payments = self.get_only_ach_payments()
        debug_bool = self.ask_for_debug()
        nacha_file = nacha.NachaConstructor.NachaConstructor(
            ach_payments,
            value_date,
            debug_bool)
        
        return nacha_file
    
    def get_only_ach_payments(self) -> pd.DataFrame:
        """Returns a table of only invoices paid via ACH."""

        payables_with_deets = self.payables.merge_vendors()
        ach_payments = payables_with_deets.loc[
            payables_with_deets["Payment Type"] == "ACH"
        ].copy(deep=True)
        return ach_payments
    
    def ask_for_debug(self) -> bool:
        debug_yn = input("\nPrint debug information? (y/n)\n>\t")
        debug_bool = False
        if debug_yn == "y":
            debug_bool = True
        return debug_bool
    
    def write_payment_file(self, 
                           company_data,
                           value_date: str, 
                           company_name: str) -> None:
        """Writes NACHA files to Downloads on disk"""

        with open(
            file="/".join([
                os.environ["HOMEPATH"].replace("\\","/"),
                "Downloads",
                f"{value_date}_ACHS_{company_name}.txt"
            ]),
            mode="w"
        ) as file:
            file.write(company_data.__str__())
    

    ####################################
    # Create Summary Workbook for Joan #   
    ####################################
    def make_summary_workbook(self) -> None:
        # Summary tables
        #   1. By Vendor
        #   2. By Approver
        #   3. By Category
        # Payment Setup - this is for me, so I can do what I want here
        #   1. Summarize wires by vendor with invoice values concatted by string
        #      to make wires easier to input
        merged_vendors = self.payables.merge_vendors()
        by_vendor = merged_vendors.pivot_table(
            values="Amount", 
            index="QB Mapping",
            aggfunc="sum",
        ).sort_values("Amount", ascending=False)
        by_approver = merged_vendors.pivot_table(
            values="Amount",
            index="Approver",
            aggfunc="sum"
        )
        by_expense_cat = merged_vendors.pivot_table(
            values="Amount",
            index="Expense Category",
            aggfunc="sum"
        )
        by_company = merged_vendors.pivot_table(
            values="Amount",
            index="Company",
            aggfunc="sum"
        )
        summary_tables = [by_vendor, by_approver, by_expense_cat, by_company]

        for table in summary_tables:
            table.loc["Total", "Amount"] = table["Amount"].sum()

        with pd.ExcelWriter(
            os.environ["HOMEPATH"] + "/Downloads/payables_summary.xlsx", 
            "xlsxwriter", 
            date_format="%Y-%m-%d"
        ) as writer:
            workbook = writer.book
            money = workbook.add_format({"num_format": "$#,##0.00"})

            summary_sheet = workbook.add_worksheet("Main Summary")
            summary_sheet.write(0,0,f"Payables Summary: {self.date}")
            write_col = 0
            for table in summary_tables:
                table.to_excel(writer, 
                               sheet_name="Main Summary", 
                               startcol=write_col, 
                               startrow=2)
                summary_sheet.set_column(first_col=write_col,
                                         last_col=write_col,
                                         width=30)
                summary_sheet.set_column(first_col=write_col+1,
                                         last_col=write_col+1,
                                         width=20,
                                         cell_format=money)
                write_col += 3


    ######################
    # Invoice management #
    ######################
    def view_all_invoices(self) -> None:
        cls()
        self.view_invoices(self.payables)

    def view_idb_invoices(self) -> None:
        # get table after merge with vendors
        # filter on idb brokers
        # print table
        pass

    def print_invoices(self, data: pd.DataFrame) -> None:
        pd.set_option("display.max_rows", None)
        print(data)

    def view_invoices(self, data: pd.DataFrame) -> None:
        """Prints invoices to screen"""
        while True:
            cls()
            self.print_invoices(data)

            print("\n\nEnter an index to view invoice details,")
            print("or hit enter to return to the main menu.")
            response = input(">\t")

            if re.match(r"\d+", response):
                self.invoice_details(int(response))
            elif re.search(r"vendor:", response, re.IGNORECASE):
                self.filter_df(data, "Vendor", response)
            elif response == "":
                break
            else:
                print("Invalid input")

    def invoice_details(self, index: int) -> None:
        """Prints invoice details to screen"""
        while True:
            cls()
            self.print_invoice_details(index)
            self.print_details_directions()

            update = input(">\t")
            pattern = r"([,]?[\s]?[\w\s#]+: [\d\w\s\(\)\.-]+)+"
            matched_phrase = re.match(pattern, update)

            ret = self.handle_invoice_details_input(
                index, matched_phrase, update
            )
            if ret == 0:
                break

            self.payables.save_workbook()
    
    def handle_invoice_details_input(
        self, index: int, match: re.Match| None, update: str) -> int:
        if match:
            groups = match.groups()
            self.update_values(index, groups)
        elif update == "":
            return 0
        elif update == "delete":
            self.payables.remove_invoice(index)
            return 0
        elif update == "open":
            self.open_invoice(index)
        else:
            print("Invalid inputs!")
            return 0

    def print_invoice_details(self, index: int) -> None:
        invoice_data = self.payables.iloc[index]
        lines = self.make_invoice_lines(invoice_data)
        for line in lines:
            print(line)
    
    def print_details_directions(self) -> None:
        print("\n\n")

        print("To remove an invoice, type delete, then enter\n")
        print("To open an invoice, type open, then enter\n")
        print("To update a value, type [field]: [new value]")
        print(
            "For multiple fields, separate field-value pairs with a comma\n"
        )
        print("To return to invoice view, hit enter on a blank line")
    
    def open_invoice(self, index: int) -> None:
        vendor = self.payables.loc[index, "Vendor"]
        invoice_no = self.payables.loc[index, "Invoice #"]
        file_info = self.get_invoice_paths(vendor, invoice_no)

        print("Select file to open:")
        count = 0
        for i in file_info:
            list_no = count + 1
            print(f"{list_no}:\t{i[1]} file")
            count += 1
        
        file_selection = self.convert_str_to_int_input(input("\n>\t"))
        file_selection -= 1

        os.system(f"\"{file_info[file_selection][0]}\"")
    
    def filter_df(self, data: pd.DataFrame, column: str, response: str) -> None:
        parsed_response = response[response.index(":")+1:].strip()
        debug(f"\nparsed_reponse: {parsed_response}")
        filtered = data.loc[
            data[column].str.match(parsed_response, case=False)
        ].copy()
        if filtered.empty:
            return
        self.view_invoices(filtered)

    def invoice_search_path_constructor(self) -> str:
        pieces = [
                  self.payables_path,
                  self.year,
                  self.year + self.month,
                #   self.date
        ]
        path = '/'.join(pieces)
        return path
        
    def get_invoice_paths(
        self, vendor: str, inv_no: str
    ) -> list[list[str]]:
        test_var = 0
        path = self.invoice_search_path_constructor()
        pattern = f"{vendor} - {inv_no}"
        files = self.find_files(path, pattern)
        return files

    def find_files(self, path: str, pattern: str) -> list[list[str]]:
        """find files in a dir matching pattern
        Returns: list of lists with file and extensions
        """
        found_files = []
        # print(f"Using pattern: {pattern}")
        for dirpath, dirnames, filenames in os.walk(path):
            # print(f"searching dirpath: {dirpath}")
            for f_name in filenames:
                if re.match(pattern, f_name):
                    # print(f"matched: {f_name}")
                    joined = '/'.join([dirpath, f_name])
                    found_files.append(joined)
        extensions = self.get_file_extensions(found_files)
        files_w_exts = list(zip(found_files, extensions))
        return files_w_exts
    
    def get_file_extensions(self, file_list: list[str]) -> list[str]:
        exts = []
        for file in file_list:
            extension = file.split('.')[-1]
            exts.append(extension)
        return exts
        
    def update_values(self, index: int, groups: tuple[str]):
        for group in groups:
            if group is None:
                continue

            split_text = group.split(":")
            col = split_text[0].replace(", ", "")
            val = split_text[1].strip()

            if not self.validate_updates(col, val):
                input()
                break

            col_index = self.payables.columns.tolist().index(col)
            val_type = self.prompt_types[col_index]
            typed_val = set_type(val, val_type)
            self.payables.loc[index, col] = typed_val

        self.payables.save_workbook()
    
    def validate_updates(self, col: str, val: str):
        inputs_valid = True

        if not self.check_col(col):
            print(f"Invalid column name: {col}")
            inputs_valid = False
        
        if col == "Vendor" and not self.check_vendor(val):
            print(f"Bad vendor {val}")
            inputs_valid = False

        return inputs_valid

    def check_col(self, col: str) -> bool:
        return (col in self.payables.columns)

    def make_invoice_lines(self, data: pd.Series) -> list[str]:
        """Creates a list of formatted lines to print as invoice details

        Args:
            data (pd.Series): row of dataframe containing invoice details

        Returns:
            list[str]: list of lines to print to screen
        """
        fields = self.payables.columns.values.tolist()

        def pad_field(string: str):
            pad_len = 20
            return self.pad_string(string, pad_len, ".")

        padded_fields = [pad_field(field) for field in fields]
        field_vals_arr = list(zip(padded_fields, data.values.tolist()))
        lines = [self.get_field_line(pair) for pair in field_vals_arr]
        return lines

    def get_field_line(self, field_val_pair: list[str | Any]) -> str:
        """Make a single invoice details line for a field and value pair"""
        pair = [str(field_val_pair[0]), str(field_val_pair[1])]
        line = "".join(pair)
        return line

    def pad_string(self, string: str, pad_len: int, char: str = " ") -> str:
        """Pad a string to a given length with char

        Args:
            string (str): string to pad
            pad_len (int): length to pad to
            char (str, optional): char to pad with. Defaults to " " (space).

        Returns:
            str: padded string
        """
        pad_len = pad_len - len(string)
        if pad_len < 0:
            return string[0 : (pad_len - 1)]
        elif pad_len > 0:
            pad = "".join([char for i in range(pad_len)])
            padded_string = "".join([string, pad])
            return padded_string
        else:
            return string

    def get_index_input(self) -> int:
        """Get index(es) selection from user"""
        prompts = [
            "Input index in the following formats:\n",
            "\tSingle index, e.g., 10\n",
            "\tComma-separated list, e.g. 10,15,29\n",
            "\tRange of indexes, e.g. 10-15\n",
            ">\t",
        ]
        index_to_remove = input("".join(prompts))
        try:
            parsed_index = self.parse_remove_index_input(index_to_remove)
        except:
            parsed_index = 0
        return parsed_index

    def parse_remove_index_input(self, index_str: str) -> list[int]:
        """Parse user input of index(es) to a list"""
        if "," not in index_str:
            index_list = [int(index_str)]
        elif "-" in index_str:
            index_list = self.index_range_to_list(index_str)
        else:
            index_list = self.split_comma_sep_input(index_str)
        return index_list

    def index_range_to_list(self, s: str) -> list[int]:
        split = s.split("-")
        range_start = int(split[0])
        range_end = int(split[1] + 1)
        index_list = list(range(range_start, range_end))
        return index_list

    def split_comma_sep_input(self, s: str) -> list[int]:
        split = s.split(",")
        trimmed_inputs = [str.strip(index) for index in split]
        int_indexes = [int(index) for index in trimmed_inputs]
        return int_indexes

    def edit_invoice(self) -> None:
        cls()
        self.print_invoices()
        print("\n\n Input invoices to edit\n")

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
        prompts = [col + ": " + no_nans[col] for col in table_cols]
        return prompts

    def remove_nans(self, new_data) -> dict[str, str]:
        no_nans = {}
        for col in self.payables.columns.to_list():
            val = self.substitue_nan(new_data[col], "")
            updater = {col: val}
            no_nans.update(updater)
        return no_nans

    def substitue_nan(self, value: Any, sub: Any) -> Any:
        if isinstance(value, float) and np.isnan(value):
            value = sub
        return value
    
    def convert_str_to_int_input(self, input: str) -> int:
        """Checks if a string is int-able and returns the int"""
        if re.match(r"\d+", input):
            return int(input)
        else:
            raise TypeError(f"Input was not a number: {input}")

def debug_script():
    instance = OsInterface("2025-08-31", True)
    instance.make_summary_workbook()

def run_interface():
    OsInterface()

if __name__ == "__main__":
    debug_script()