import getpass
import pandas as pd
import pyodbc
import os
import shutil
import time
import sys

sys.path.append(os.environ["HOMEPATH"] + "/accounting/payables")
sys.path.append(os.environ["HOMEPATH"] + "/accounting")
sys.path.append(os.environ["HOMEPATH"] + "/accounting/Wires")

import APDatabase
from SigIntHandler import DelayedKeyboardInterrupt
from functions import *
from CursorFunc import *


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
            "Create Payment Files": self.make_payment_files,
            "Create Summary Workbook": self.save_summary_workbook,
            "Create Quickbooks Bill Files": self.create_bill_files,
            "Exit": "",
        }
        while True:
            cls()

            print("Payables Main Menu\n")
            # self.print_main_menu_status()
            # print("\n")
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

    ####
    # Add invoices code
    ####
    def add_invoices(self):
        """Main loop for adding invoices to the payables table"""

        with DelayedKeyboardInterrupt():
            self.preserve_downloads_handler()
            while True:
                cls()

                try:
                    invoice_data = self.get_inputs(
                        prompts=self.invoice_prompts
                    )
                except EOFError:
                    invoice_data = [0]
                if is_blank_list(data=invoice_data):
                    break

                if invoice_data[3]:
                    self.add_cc_user(invoice_data=invoice_data)

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
                self.preserve_downloads()
                self.preserved_downloads = np.uint8(1)
        elif self.preserved_downloads == np.uint8(1):
            self.restore_downloads()
            self.preserved_downloads = np.uint8(0)

    def preserve_downloads(self) -> None:
        """Preserves downloads contents by moving to temp folder"""

        try:
            os.mkdir("/".join([os.environ["HOMEPATH"], ".tempdownloads"]))
        except FileExistsError:
            pass

        self.move_all_files(
            "/".join([os.environ["HOMEPATH"], "Downloads"]),
            "/".join([os.environ["HOMEPATH"], ".tempdownloads/"]),
        )

    def restore_downloads(self) -> None:
        """Restores downloads from temp folder"""

        self.move_all_files(
            "/".join([os.environ["HOMEPATH"], ".tempdownloads/"]),
            "/".join([os.environ["HOMEPATH"], "Downloads"]),
        )
        shutil.rmtree("/".join([os.environ["HOMEPATH"], ".tempdownloads/"]))

    def move_all_files(self, source: str, dest: str) -> None:
        """Moves all files from a source folder to a destination folder."""

        files = os.listdir(source)
        for file in files:
            shutil.move(src=source + f"/{file}", dst=dest + f"/{file}")

    def get_inputs(self, prompts: list[str], **kwargs) -> list[str | int]:
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

        self.set_input_types(inputs)

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

    def set_input_types(
        self, inputs: list[str | int]
    ) -> list[str | int | bool]:
        """Types str input values to table column d-types"""

        zipped_inputs_and_types = zip(inputs, self.prompt_types)
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

        new_val = ""
        if cc_val == "y":
            new_val = cc_val
        return new_val

    def get_input_index(self, col: str) -> int:
        """Gets the index of the prompt corresponding to the desired column
        header."""

        with_stub = col + ":"
        return self.invoice_prompts.index(with_stub)

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

        padded = pad_string(prompts[index], 20)
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
            clear_end_of_line_after_input(value=data)
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
        cc_user = input("Enter initials of CC user:\t")
        invoice_data[cc_user_index] = cc_user

    def print_possible_vendors(self, vendor: str):
        """Prints a list of possible correct vendors to screen"""

        possibilities = APDatabase.search_possible_vendors(vendor, self.conn)
        val_list = possibilities["vendor"].values.tolist()
        print("Vendor invalid. Did you mean...")
        for i in val_list:
            print(f"\t{i}")

    def view_invoices(self):
        pass

    def make_payment_files(self):
        pass

    def save_summary_workbook(self):
        pass

    def create_bill_files(self):
        pass


if __name__ == "__main__":
    app = ApGui()
