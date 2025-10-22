import getpass
import pandas as pd
import pyodbc
import os
import shutil
import time
import sys
import warnings

sys.path.append(os.environ["HOMEPATH"] + "/accounting/payables")
sys.path.append(os.environ["HOMEPATH"] + "/accounting")
sys.path.append(os.environ["HOMEPATH"] + "/accounting/Wires")

import APDatabase
from functions import *
from CursorFunc import *
from wires import PayablesWires


def get_uid_pwd() -> tuple[str]:
    uid = input("Username: ")
    pwd = getpass.getpass()
    return (uid, pwd)


def cls():
    os.system("cls")


class ApGui:

    invoice_prompts = [
        "Vendor:",
        "Invoice Number:",
        "Invoice Amount:",
        "Credit card:",
    ]
    prompt_types = ["str", "str", "float64", "bool"]
    up_key = "k"
    down_key = "j"

    def __init__(self):
        pd.set_option("display.max_rows", None)
        warnings.simplefilter(action="ignore", category=UserWarning)
        self.conn = None
        self.preserved_downloads = np.uint8(0)
        self.connect_to_db()
        self.main_menu()

    def connect_to_db(self) -> pyodbc.Connection:
        while self.conn is None:
            cls()
            creds = get_uid_pwd()
            try:
                self.conn = APDatabase.establish_db_connection(*creds)
                print("Connection to accounting database successful.")
                time.sleep(3)
            except:
                self.conn = None

    def main_menu(self):
        """Main user interface menu function"""
        options = {
            "Add Invoices": self.add_invoices,
            "View/Edit Invoices": self.view_invoices,
            "Create Payment Files": self.make_all_payment_files,
            "Create Summary Workbook": self.save_summary_workbook,
            "Create Quickbooks Bill Files": self.create_bill_files,
            "Exit": "",
        }
        while True:
            cls()

            now_date = datetime.now()
            date_str = now_date.strftime("%m-%d-%Y")

            print_to_ascii_table(f"Simplex Accounts Payable\t{date_str}")

            print("\n\n")
            self.print_main_menu_status()
            self.print_main_menu(options)

            selected = 0
            while not selected:
                selected = self.main_menu_input()

            key = list(options.keys())[selected - 1]

            if selected == len(list(options.keys())):
                cls()
                break
            else:
                options[key]()

    def print_main_menu(self, options: dict):
        for i in range(len(options.keys())):
            key = list(options.keys())[i]
            print(f"{str(i + 1)}: {key}")

    def main_menu_input(self):
        """Receive user input for main menu selection"""
        selection = input("\nPlease enter number of option:\n>\t")
        if re.match(r"\d+", selection):
            return int(selection)
        else:
            print("Bad option!")

    def print_main_menu_status(self) -> None:
        summary_data = APDatabase.get_main_menu_summary_data(self.conn)
        print("* Unpaid Invoices Summary *")
        if summary_data.empty:
            print("\t<no unpaid invoices currently>")
        else:
            data_lines = ["Company\tAmount"]
            for i, row in summary_data.iterrows():
                company_line = f"{row["company"]}\t${row["total"]:,.2f}"
                data_lines.append(company_line)
            total_line = f"TOTAL\t${summary_data.total.sum():,.2f}"
            data_lines.append(total_line)
            print_to_ascii_table(*data_lines, total_line=True)

            print("\n\n")

    ####
    # Add invoices code
    ####
    def add_invoices(self):
        """Main loop for adding invoices to the payables table"""

        self.preserve_downloads_handler()
        while True:
            cls()

            try:
                invoice_data = self.get_invoice_data(
                    prompts=self.invoice_prompts
                )
            except EOFError:
                invoice_data = [0]

            if is_blank_list(data=invoice_data):
                break
            elif APDatabase.check_for_duplicate_entry(
                invoice_data[0], invoice_data[1]
            ):
                print("Invoice was a duplicate, not submitting entry.")
            else:
                APDatabase.add_invoice(
                    invoice_data=invoice_data, connection=self.conn
                )

            add_more = input("\nAdd another invoice (y/n)\n>\t")
            if add_more == "n":
                break

        self.preserve_downloads_handler(end=True)

    def preserve_downloads_handler(self, end: bool = False) -> int:
        if not end and self.preserved_downloads == np.uint8(0):
            print("Move downloads to temp folder? (y/n)")
            resp = input(">\t")
            if resp == "y":
                preserve_downloads()
                self.preserved_downloads = np.uint8(1)
        elif self.preserved_downloads == np.uint8(1):
            restore_downloads()
            self.preserved_downloads = np.uint8(0)

    def get_invoice_data(
        self, prompts: list[str], **kwargs
    ) -> list[str | int]:
        """Management of receiving user input for a new invoice"""

        inputs = ["" for i in range(5)]
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

        fix_cc_input(inputs)
        if inputs[3]:
            self.add_cc_user(inputs)

        if APDatabase.check_vendor(inputs[0], self.conn) or is_blank_list(
            inputs
        ):
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

        pad_len = 30
        padded = pad_string(prompts[index], pad_len)
        print(padded, end="")
        response = input_list[index]

        if response:
            print_sugg_value(value=response)

        data = input()

        # Overwrite input_list[i] only if it's 0 or you're putting in a new val
        if data != self.up_key and data != self.down_key:
            if not input_list[index]:
                input_list[index] = data
            elif input_list[index] and data != "":
                input_list[index] = data
            index += 1
            clear_end_of_line_after_input(value=data, pad_len=pad_len)
        elif data == self.up_key:
            index = self.up_arrow(index)
            print("\r", end="", flush=True)
        elif data == self.down_key:
            index = self.down_arrow(index, end)
            print("\r", end="", flush=True)

        return index

    def add_cc_user(self, invoice_data) -> None:
        """Add credit card user to invoice data for credit card invoices"""

        cc_user_index = len(self.invoice_prompts)
        padded = pad_string("Enter initials of CC User:", 30)
        print(padded, end="")
        cc_user = input()
        invoice_data[cc_user_index] = cc_user

    def print_possible_vendors(self, vendor: str):
        """Prints a list of possible correct vendors to screen"""

        possibilities = APDatabase.search_possible_vendors(vendor, self.conn)
        val_list = possibilities["vendor"].values.tolist()
        print("Vendor invalid. Did you mean...")
        for i in val_list:
            print(f"\t{i}")

    def view_invoices(self, data: pd.DataFrame = None):
        """Prints unpaid invoices for user."""

        cols = [
            "id",
            "vendor",
            "inv_num",
            "company",
            "amount",
            "approved",
            "approver",
        ]

        while True:
            cls()
            print_header("UNPAID INVOICES")

            if data:
                df = data
            else:
                sql = APDatabase.construct_sql_query(
                    "invoices", cols=cols, paid=False, cc=False
                )
                df = pd.read_sql(sql, con=self.conn, index_col="id")

            if df.empty:
                print("\n<no unpaid invoices currently>\n")
            else:
                print(df)

            print("\n\nEnter an index to view invoice details,")
            print("type 'Vendor: [vendor]' to filter by vendor,")
            print("'Approver: [name]' to filter by approver,")
            print("'export: [file_name]' to save file to downloads")
            print("'IDB' to view IDB only invoices,")
            # print("'unapproved' to see all unapproved invoices,")
            # print("'mark approved' to mark all showing invoices as approved")
            print("or just hit enter to return to the main menu.")

            response = input(">\t")
            parse_result = APDatabase.parse_user_response(
                user_response=response,
                table="invoices",
                table_cols=cols,
                con=self.conn,
            )
            if isinstance(parse_result, np.int8) and parse_result == np.int8(
                1
            ):
                break
            elif isinstance(parse_result, tuple):
                self.response_handler(*parse_result)
            elif isinstance(parse_result, pd.DataFrame):
                self.view_invoices(data=parse_result)

    def response_handler(self, option: np.int8, data: pd.DataFrame) -> None:
        if option == np.int8(2):
            self.print_invoice_details(data=data)
        else:
            return

    def print_invoice_details(self, data: pd.DataFrame) -> None:
        id = data.index[0]
        date_added = data.iloc[0]["date_added"]
        vendor = data.iloc[0]["vendor"]
        inv_num = data.iloc[0]["inv_num"]
        amount = data.iloc[0]["amount"]
        approved = data.iloc[0]["approved"]
        paid = data.iloc[0]["paid"]
        pay_date = data.iloc[0]["date_paid"]

        cls()
        print_header("Invoice Details")
        print("")
        print(f"{"Vendor:":15}    {vendor}")
        print(f"{"Invoice:":15}    {inv_num}")
        print(f"{"Amount:":15}    ${amount:,.2f}")
        print("\n Status")
        print(" ", "_" * 20, sep="")
        if approved:
            print(f"| {"APPROVED":18} |")
        else:
            print(f"| {"Needs approval":18} |")
        if paid:
            print(f"| Paid on {pay_date} |")
        else:
            print(f"| {"Unpaid":18} |")
        print(" ", "\u203e" * 20, sep="")
        print(f"\n\nLast updated: {date_added}")

        print("To remove this invoice, enter 'delete'.")
        print("To update a value, enter '<field>: <new value>")
        print("To return, press enter.")

        response = input(">\t")
        status = parse_inv_dets_response(response, id, self.conn)

    ########################
    # Create Payment Files #
    ########################
    def generate_nacha_files(self) -> None:
        """Create NACHA payment files for invoiced payable via ACH and save
        to disk."""

        vd = ui_get_date(dt=True).strftime("%Y-%m-%d")
        debug = True if input("Debug (y/n): ") == "y" else False
        make_nacha_files(value_date=vd, con=self.conn, debug=debug)
        print("NACHA file generation complete. Files saved to downloads.")
        input("Enter to continue.")

    def generate_wire_files(self) -> None:
        """Method for creating a simple batch of wire payments for a given
        payables run. One invoice = one wire.
        """

        vd = ui_get_date(dt=True)
        make_wire_pmt_files(value_date=vd, con=self.conn)

    def make_all_payment_files(self) -> None:
        self.generate_nacha_files()
        self.generate_wire_files()

    def save_summary_workbook(self):
        pass

    def create_bill_files(self):
        pass


if __name__ == "__main__":
    app = ApGui()
