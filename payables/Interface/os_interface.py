# Standard Packages
import os
import numpy as np
import pandas as pd
import re
import sys
from typing import Any
import shutil
from datetime import datetime
import xlsxwriter

# Path updates for package imports
sys.path.append(os.environ["HOMEPATH"] + "/accounting/payables")
sys.path.append(os.environ["HOMEPATH"] + "/accounting")
sys.path.append(os.environ["HOMEPATH"] + "/accounting/Wires")

# Package Imports
from Interface.payables_wb import PayablesWorkbook, get_col_index
from Interface.functions import *
from nacha import NachaConstructor
import DupePayments as DupePayments
from Wires import WireFile, WirePayment


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
    up_key = "k"
    down_key = "j"


    ##################
    # initialization #
    ##################
    def __init__(self, payables_date: str = None, debug: bool=False):
        self.preserved_downloads = 0

        if payables_date is None:
            self._ui_workbook_date()
        else:
            self._validate_date(payables_date)

        self.payables = PayablesWorkbook(date=payables_date)

        if not debug:
            self.main()
        

    ##################
    # date functions #
    ##################
    def _ui_workbook_date(self) -> None:
        """User interface for getting payables date"""

        cls()
        valid_date = False
        while not valid_date:
            payables_date = input(
                "Input Payables Workbook Date (yyyy-mm-dd)\n>\t"
            )
            valid_date = self.validate_date(payables_date)
            if not valid_date:
                print("Invalid date, try again")
    
    def _validate_date(self, date: str) -> bool:
        if check_date(date):
            self.date = date
            self._parse_date(date)
            self.dt_date = datetime.strptime(date, "%Y-%m-%d")
            return True
        else:
            return False
    
    def _parse_date(self, date: str) -> None:
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

    @property
    def vendors(self):
        path = "/".join([
            "C:/gdrive/Shared drives/accounting/patrick_data_files",
            "ap/Vendors.xlsx"
        ])
        vendors = pd.read_excel(
            io=path,
            sheet_name="Vendors",
        )
        return vendors


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
            f"Total # of invoices: {len(self.payables.data.index)!s}",
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
        """Main loop for adding invoices to the payables table"""
        self.preserve_downloads_handler()
        try:
            while True:
                cls()

                try:
                    invoice_data = self.get_inputs(prompts=self.invoice_prompts)
                except EOFError:
                    invoice_data = [0]
                if is_blank_list(data=invoice_data):
                    break

                if invoice_data[3]:
                    self.add_cc_user(invoice_data=invoice_data)
                self.set_paid_status(inputs=invoice_data, status=False)

                self.payables.insert_invoice(invoice_data=invoice_data)
                add_more = input("\nAdd another invoice (y/n)\n>\t")
                if add_more == "n":
                    break
        except ValueError:
            self.payables.save_workbook()

        self.preserve_downloads_handler(end=True)

    def preserve_downloads_handler(self, end: bool=False) -> int:
        if not end and self.preserved_downloads == np.uint8(0):
            print("Move downloads to temp folder? (y/n)")
            resp = input(">\t")
            if resp == "y":
                self.preserve_downloads()
                self.preserved_downloads = np.uint8(1)
        elif self.preserved_downloads == np.uint8(1):
            self.restore_downloads()
            self.preserved_downloads = np.uint8(0)
        
    def preserve_downloads(self) -> None:
        """Preserves downloads contents by moving to temp folder"""

        try:
            os.mkdir("./.tempdownloads")
        except FileExistsError:
            pass

        self.move_all_files("./Downloads", "./.tempdownloads/")

    def restore_downloads(self) -> None:
        """Restores downloads from temp folder"""

        self.move_all_files("./.tempdownloads", "./Downloads/")
        shutil.rmtree("./.tempdownloads")

    def move_all_files(self, source: str, dest: str) -> None:
        """Moves all files from a source folder to a destination folder."""

        files = os.listdir(source)
        for file in files:
            shutil.move(src=source + f"/{file}", dst=dest + f"/{file}")

    def get_inputs(self, prompts: list[str], **kwargs) -> list[str | int]:
        """Management of receiving user input for a new invoice"""
        inputs = ["" for i in range(len(PayablesWorkbook.column_headers))]
        for i in range(len(prompts)):
            inputs[i] = 0
        
        if kwargs:
            keys = list(kwargs.keys())
            for i in range(len(keys)):
                old_val = kwargs[keys[i]]
                if old_val:
                    inputs[i] = old_val

        i = 0
        while 0 in inputs:
            i = self.get_single_user_input(prompts, inputs, i)
        
        self.set_input_types(inputs)

        if self.add_invoice_vendor_check(inputs) or is_blank_list(inputs):
            return inputs
        else:
            self.print_possible_vendors(inputs[0])
            inputs = self.get_inputs(
                prompts=prompts,
                vendor=0,
                invoice_num=inputs[1],
                invoice_amt=inputs[2],
            )
            return inputs
        
    def set_input_types(
        self, inputs: list[str | int]) -> list[str | int | bool]:
        """Types str input values to table column d-types"""

        zipped_inputs_and_types = zip(
            inputs, OsInterface.prompt_types
        )
        self.fix_cc_input(inputs)

        index = 0
        for val, val_type in zipped_inputs_and_types:
            inputs[index] = set_type(val, val_type)
            index += 1
            
    def fix_cc_input(self, inputs: list[str | int]) -> list[str | int]:
        """Standardizes cc response to 'y' or ''."""

        cc_index = self.get_input_index("Credit card")
        cc_input = inputs[cc_index]
        inputs[cc_index] = self.swap_cc_input(cc_input)
        
    def swap_cc_input(self, cc_val: str) -> str:
        """Returns 'y' if user response was 'y', else returns ''"""

        new_val = '' 
        if cc_val == "y":
            new_val = cc_val
        return new_val
    
    def get_input_index(self, col: str) -> int:
        """Gets the index of the prompt corresponding to the desired column 
        header."""

        with_stub = col + ":"
        return OsInterface.invoice_prompts.index(with_stub)

    def get_single_user_input(
        self, prompts: list[str], input_list: list, curr_index: int
    ) -> int:
        """Gets a single user input for a given prompt in a list of prompts.

        Args:
            prompts (list[str]): list of prompts to work from
            input_list (list): list of received user inputs
            curr_index (int): current location in list of prompts

        Returns:
            int: next prompt location to go to
        """

        index = curr_index
        end = len(prompts) - 1

        padded = self.pad_string(prompts[index], 20)
        print(padded, end="")
        response = input_list[index]

        if response:
            input_len = len(str(response))
            print(response, end='', flush=True)
            # Erase from cursor to end of line
            print("\033[0K", end='', flush=True)
            # Move cursor to beginning of the response
            print(f"\033[{input_len}D", end='', flush=True)


        data = input()

        # Overwrite input_list[i] only if it's 0 or you're putting in a new val
        if data != self.up_key and data != self.down_key:
            if not input_list[index]:
                input_list[index] = data
            elif input_list[index] and data != '':
                input_list[index] = data
            index += 1
        elif data == self.up_key:
            index = self.up_arrow(index)
            print("", end="\r", flush=True)
        elif data == self.down_key: 
            index = self.down_arrow(index, end)
            print("", end="\r")

        return index

    def add_invoice_vendor_check(
        self, inputs: list[str | int]) -> bool | list[str]:
        """Checks for valid vendor in user inputs. Recursively gets inputs if 
        invalid."""

        vendor_name = inputs[0]
        found_vendor = self.validate_vendor(vendor_name)
        if found_vendor:
            return True
        else:
            return False
            
    def validate_vendor(self, input: str | int) -> bool:
        """Validates presence of inputs in Vendor list"""

        vendors = self.vendors.Vendor.values.tolist()
        found_vendor = input in vendors
        return found_vendor

    def add_cc_user(self, invoice_data) -> None:
        """Add credit card user to invoice data for credit card invoices"""
        cc_user_index = PayablesWorkbook.column_headers.index("CC User")
        cc_user = input("Enter initials of CC user:\t")
        invoice_data[cc_user_index] = cc_user

    def print_possible_vendors(self, vendor: str):
        """Prints a list of possible correct vendors to screen"""

        vals = self.get_possible_vendors(vendor)
        print("Vendor invalid. Did you mean...")
        for i in vals:
            print(f"\t{i}")

    def get_possible_vendors(self, vendor: str) -> list[str]:
        """Returns a list of possible correct vendor choices"""

        split_vendor = vendor.split(" ")
        possibilities = self.vendors.loc[
            self.vendors["Vendor"].str.contains(
                pat=split_vendor[0],
                case=False,
                na=""
            )
        ]
        return possibilities["Vendor"].tolist()
        
    def set_paid_status(self, inputs: list, status: bool) -> None:
        paid_status_index = get_col_index("Paid")
        inputs[paid_status_index] = status

        
    ####################
    # Input Navigation #
    ####################
    def up_arrow(self, index: int) -> int:
        """Navigates cursor up one line. Returns resulting value after nav."""

        if index > 0:
            index -= 1
            cursor_up()
        return index

    def down_arrow(self, index: int, end_index: int) -> int:
        """Navigates cursor down one line to a max line end_index. Returns 
        resulting value."""

        if index <= end_index:
            index += 1
            cursor_down()
            # print('', end='\r', flush=True)
        return index
    
    ######################
    # Create NACHA files #
    ######################
    def make_payment_files(self):
        """Creates NACHA payment files for current payables batch."""

        self.check_for_duplicate_payments()

        vd = self.get_vd()
        nacha_file = self.get_nacha_constructor(value_date=vd)

        files = nacha_file.main()
        co_names = NachaConstructor.NachaConstructor.company_names
        list_of_co_names = list(co_names.keys())

        for i in range(len(files)):
            current = files[i]
            company_name = list_of_co_names[i]
            self.write_payment_file(current, vd, company_name)

    def check_for_duplicate_payments(self):
        """Checks for duplicate payments in current payables batch."""
        
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
        
        ach_payments = self.filter_payments_on_type("ACH")
        debug_bool = self.ask_for_debug()
        nacha_file = NachaConstructor.NachaConstructor(
            ach_payments,
            value_date,
            debug_bool)
        
        return nacha_file
    
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
    

    #############################
    # Create Wire Payment Files #
    #############################
    def make_wire_files(self) -> None:
        """Makes a wire payment file for upload to JPM Access"""
        vd = self.get_vd()
        self.wire_vd = vd

        wire_payments = self.filter_payments_on_type("Wire")
        vendor_dict = self.get_vendor_objs(wire_payments)
        payments = self.make_payment_objs(wire_payments, vendor_dict)

        file = WireFile.WireFile(payments)
        f_name = " ".join([self.date, "Wire Payments"])
        file.write_file("/".join([os.environ["HOMEPATH"], "Downloads"]), f_name)
        
    def get_vendor_objs(self, wires: pd.DataFrame) -> dict[str, WirePayment.Vendor]:
        """Returns a dict mapping vendor names to their corresponding vendor 
        object."""

        unique_vendors = wires["Vendor"].unique()
        vendor_dict = {}
        for vendor in unique_vendors:
            vendor_obj = WirePayment.Vendor(vendor)
            vendor_dict.update({vendor: vendor_obj})
        return vendor_dict
    
    def make_payment_objs(self,
                          wires: pd.DataFrame,
                          vendors: dict[str, WirePayment.Vendor]) -> list[WirePayment.WirePayment]:
        """Returns a tuple of wire payment objects for use in a WireFile 
        object"""
        payments = []
        dt_wire_vd = datetime.strptime(self.wire_vd, "%y%m%d")
        for i, row in wires.iterrows():
            company_account = WirePayment.company_ids[row["Company"]]
            vendor_ob = vendors[row["Vendor"]]

            new_payment = WirePayment.WirePayment(
                orig_bank_id="071000013",
                orig_account=company_account,
                amount=row["Amount"],
                value_date=dt_wire_vd,
                vendor=vendor_ob,
                details=row["Invoice #"],
                template=True
            )
            payments.append(new_payment)
        return payments

    #################################
    # Payment File Common Functions #
    #################################
    def filter_payments_on_type(self, type: str) -> pd.DataFrame:
        """Returns a table of only invoices paid via ACH."""

        no_cc_pmts = self.payables.data.loc[~(self.payables.data["CC"])]
        payables_with_deets = no_cc_pmts.merge_vendors()
        filtered_payments = payables_with_deets.loc[
            payables_with_deets["Payment Type"] == type
        ].copy(deep=True)
        return filtered_payments

    def get_vd(self) -> str:
        year = int(get_valid_input("VD Year:  ", r"\d{4}"))
        month = int(get_valid_input("VD Month: ", r"\d{1,2}"))
        day = int(get_valid_input("VD Day:   ", r"\d{1,2}"))
        vd_dt = datetime(year, month, day)
        vd_str = vd_dt.strftime("%y%m%d")
        return vd_str

    ####################################
    # Create Summary Workbook for Joan #   
    ####################################
    def make_summary_workbook(self) -> None:
        """Write invoice summary workbook to disk"""
        # Summary tables
        #   1. By Vendor
        #   2. By Approver
        #   3. By Category
        # Payment Setup - this is for me, so I can do what I want here
        #   1. Summarize wires by vendor with invoice values concatted by string
        #      to make wires easier to input

        with pd.ExcelWriter(
            os.environ["HOMEPATH"] + "/Downloads/payables_summary.xlsx", 
            "xlsxwriter", 
            date_format="%Y-%m-%d"
        ) as writer:
            workbook: xlsxwriter.workbook.Workbook = writer.book

            # Cell formats
            global money, bold_with_border, decimal
            money = workbook.add_format({"num_format": "$#,##0.00"})
            bold_with_border = workbook.add_format({"bold": True})
            bold_with_border.set_border(1)
            decimal = workbook.add_format({"num_format": "#,##0.00"})
            
            self.write_summary_sheet(writer, workbook)
            self.write_wire_setup_sheet(writer, workbook)
            self.write_invoice_sheet(writer, workbook)

    def write_summary_sheet(self,
                            writer: pd.ExcelWriter,
                            workbook: xlsxwriter.Workbook) -> None:
        """Write the summary sheet to file."""

        summary_tables = self.get_summary_tables()
        summary_sheet = self.create_summarypage(workbook)
        write_col = 0
        for table in summary_tables:
            table.to_excel(excel_writer=writer, 
                           sheet_name="Main Summary", 
                           startcol=write_col, 
                           startrow=2)
            # Set table first column width to 30
            summary_sheet.set_column(first_col=write_col,
                                     last_col=write_col,
                                     width=30)
            # Set table second col width 20, num format with $
            summary_sheet.set_column(first_col=write_col+1,
                                     last_col=write_col+1,
                                     width=20,
                                     cell_format=money)
            write_col += 3
        
    def write_invoice_sheet(self,
                            writer: pd.DataFrame,
                            workbook: xlsxwriter.Workbook) -> None:
        invoice_sheet = workbook.add_worksheet("Invoices")
        invoices = self.get_invoice_table()
        invoices.to_excel(excel_writer=writer, sheet_name="Invoices")

        invoice_sheet.set_row(row=0, cell_format=bold_with_border)
        num_cols = len(invoices.columns)
        invoice_sheet.set_column(first_col=1, last_col=num_cols-1, width=30)
        invoice_sheet.set_column(first_col=num_cols,
                                 last_col=num_cols,
                                 width=20,
                                 cell_format=money)
            
    def write_wire_setup_sheet(self, 
                               writer: pd.ExcelWriter,
                               workbook: xlsxwriter.Workbook) -> None:
        wire_sheet = workbook.add_worksheet("Wire Setup")
        wires = self.get_wire_table()
        wires.to_excel(excel_writer=writer, sheet_name="Wire Setup")
        wire_sheet.set_column(first_col=0,
                              last_col=0,
                              width=30)
        wire_sheet.set_column(first_col=1,
                              last_col=1,
                              width=20,
                              cell_format=decimal)
        
    def get_invoice_table(self) -> pd.DataFrame:
        data = self.payables.merge_vendors()
        cols = [
            'Vendor',
            'Invoice #',
            'Company',
            'Expense Category',
            'Approver',
            'Payment Type',
            'Amount'
        ]
        selected_cols = data[cols].copy(deep=True)
        return selected_cols
        
    def create_summarypage(
        self,
        workbook: xlsxwriter.workbook.Workbook
    ) -> xlsxwriter.workbook.Worksheet:
        summary_sheet = workbook.add_worksheet("Main Summary")
        summary_sheet.write(0,0,f"Payables Summary: {self.date}")
        return summary_sheet
        
    def get_summary_tables(self) -> tuple[pd.DataFrame]:
        """Get summary tables for the main summary page of the workbook."""

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
        summary_tables = (by_vendor, by_approver, by_expense_cat, by_company)

        for table in summary_tables:
            table.loc["Total", "Amount"] = table["Amount"].sum()

        return summary_tables
        
    def get_wire_table(self) -> pd.DataFrame:
        with_deets = self.payables.merge_vendors()
        wire_mask = with_deets["Payment Type"] == "Wire"
        wires = with_deets.loc[wire_mask].copy(deep=True)
        by_vendor_wires = wires.pivot_table(
            values="Amount",
            index="Vendor",
            aggfunc="sum"
        )

        invoices_by_vendor_wires = self.get_wire_invoices_by_vendor(wires)
        by_vendor_wires_merged = by_vendor_wires.merge(
            right=invoices_by_vendor_wires,
            how="left",
            on="Vendor"
        )
        return by_vendor_wires_merged
    
    def get_wire_invoices_by_vendor(self, wires: pd.DataFrame) -> pd.DataFrame:
        unique_vendors = wires["Vendor"].unique()
        unique_vendors.sort()
        wire_invoices_by_vendor = pd.DataFrame(index=unique_vendors,
                                               columns=["Invoices"])
        wire_invoices_by_vendor = wire_invoices_by_vendor.rename_axis("Vendor")
        # print(wire_invoices_by_vendor)
        for vendor in unique_vendors:
            vendor_invoices = wires.loc[wires.index == vendor, "Invoice #"]
            str_vendor_invoices = ", ".join(vendor_invoices)
            mask = wire_invoices_by_vendor.index == vendor
            wire_invoices_by_vendor.loc[mask, "Invoices"] = \
                                                            str_vendor_invoices
        return wire_invoices_by_vendor


    ######################
    # Invoice management #
    ######################
    def view_all_invoices(self) -> None:
        cls()
        self.view_invoices(self.payables.data)

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
            print("type 'Vendor: [vendor]' to filter by vendor,")
            print("or export: [file_name] to save file to downloads")
            print("or hit enter to return to the main menu.")
            response = input(">\t")

            if re.match(r"\d+", response):
                self.invoice_details(int(response))
            elif re.search(r"vendor:", response, re.IGNORECASE):
                self.filter_df(data, "Vendor", response)
            elif re.search(r"export", response, re.IGNORECASE):
                match = re.search(r"export:?", response, re.IGNORECASE)
                f_name = '.'.join([
                    response.replace(match.group(), "").strip(),
                    'xlsx'
                ])
                print(f_name)
                path = '/'.join([os.environ["HOMEPATH"], "Downloads", f_name])
                data.to_excel(excel_writer=path,
                              sheet_name="Export",
                              index=False,
                              na_rep="")
                print("Data export success. File in downloads.")
                print("Enter to continue.")
                input()
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
        invoice_data = self.payables.data.iloc[index]
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
        vendor = self.payables.data.loc[index, "Vendor"]
        invoice_no = self.payables.data.loc[index, "Invoice #"]
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

            col_index = self.payables.data.columns.tolist().index(col)
            val_type = self.payables.column_types[col_index]
            typed_val = set_type(val, val_type)
            self.payables.data.loc[index, col] = typed_val

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
        return (col in self.payables.data.columns)

    def make_invoice_lines(self, data: pd.Series) -> list[str]:
        """Creates a list of formatted lines to print as invoice details

        Args:
            data (pd.Series): row of dataframe containing invoice details

        Returns:
            list[str]: list of lines to print to screen
        """
        fields = self.payables.data.columns.values.tolist()

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
        data = self.payables.data.loc[index].copy()
        edit_prompts = self.make_edit_prompts(data)
        inputs = self.get_input(edit_prompts)
        self.payables.data.loc[index] = inputs

    def make_edit_prompts(self, new_data) -> None:
        table_cols = self.payables.data.columns.to_list()
        no_nans = self.remove_nans(new_data)
        prompts = [col + ": " + no_nans[col] for col in table_cols]
        return prompts

    def remove_nans(self, new_data) -> dict[str, str]:
        no_nans = {}
        for col in self.payables.data.columns.to_list():
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
    instance = OsInterface(payables_date="2030-12-31")
    instance.main()
    # instance = OsInterface()
    # inv = [
    #     "Baycrest (IDB)",
    #     "test",
    #     np.float64(1000),
    #     False,
    #     "",
    #     False
    # ]
    # instance.payables.insert_invoice(inv)

def run_interface():
    OsInterface()

if __name__ == "__main__":
    debug_script()