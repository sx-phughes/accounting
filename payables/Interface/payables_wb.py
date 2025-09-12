# Standard packages
from datetime import datetime
import os
import shutil
import pandas as pd
import numpy as np

# Package imports
try:
    from payables.Interface.functions import *
except ModuleNotFoundError:
    try:
        from Interface.functions import *
    except ModuleNotFoundError:
        from functions import *


def get_col_index(col_name: str) -> int:
    headers = PayablesWorkbook.column_headers
    try:
        i = headers.index(col_name)
    except ValueError:
        i = -1
    return i


class PayablesWorkbook(pd.DataFrame):
    # class vars
    payables_path = "C:/gdrive/Shared drives/accounting/Payables"
    vendors_path = \
        "C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx"
    column_headers = ["Vendor", "Invoice #", "Amount", "CC", "CC User", "Paid"]
    column_types = ["str", "str", "float64", "bool", "str", "bool"]
    column_defaults = ["", "", np.float64(0), False, "", False]

    # for DataFrame constructor
    _metadata = [
        # "wb_path",
        "payables_date",
        "stem",
        "f_name",
        "_payables_date",
        "_stem",
        "_f_name",
        # "_wb_path"
    ]

    @property
    def _constructor(self):
        return PayablesWorkbook

    ############################################################
    # initializer - handles reconstruction from pandas methods #
    ############################################################
    def __init__(
        self,
        data: pd.DataFrame | None = None,
        date=None,
        index=None,
        columns=None,
        dtype=None,
        copy=None,
    ):
        if date:
            self.payables_date = date
            self.stem = self.payables_date

        if data is not None:
            input_data = data
        else:
            input_data = self.initialize_from_date()

        super().__init__(input_data, index, columns, dtype, copy)

    def initialize_from_date(self):
        """Initialize Payables Workbook from a given date string

        Checks for a pre-existing payables workbook or uses a new one, then
        validates columns
        """
        # check to see if date folder exists--implies existence of payables
        # workbook
        path = self.wb_path().replace(self.f_name, "")
        if not self.path_exists(path):
            self.new_workbook()

        try:
            data = pd.read_excel(self.wb_path(), "Invoices")
        except:
            data = pd.read_excel(self.wb_path().replace("xlsx", "xlsm"), "Invoices")

        self.validate_data(data)
        data = self.set_types(data)
        return data

    def set_types(self, data: pd.DataFrame):
        for col_i in range(len(data.columns)):
            col = data.columns[col_i]
            dtype = type(self.column_defaults[col_i])
            data[col] = data[col].astype(dtype)
        return data

    def validate_data(self, data: pd.DataFrame):
        """Validate workbook columns, add missing ones, and remove
        extra columns."""

        good_cols_index = self.get_extant_cols_index(data)
        if good_cols_index < len(self.column_headers):
            self.add_new_cols(data, good_cols_index)
        elif good_cols_index > len(self.column_headers):
            drop_cols = data.columns.tolist()[good_cols_index+1:]
            data.drop(columns=drop_cols, inplace=True)

    def add_new_cols(self, data: pd.DataFrame, add_from: int):
        """Add identified missing columns to payables table"""

        end = len(PayablesWorkbook.column_headers)
        for i in range(add_from, end):
            self.initialize_new_col(data, i)

    def initialize_new_col(self, data: pd.DataFrame, col_index: int):
        """Initialize a new column using a default value"""
        default_val = PayablesWorkbook.column_defaults[col_index]
        col_name = PayablesWorkbook.column_headers[col_index]
        data[col_name] = default_val

    def get_extant_cols_index(self, original: pd.DataFrame) -> int:
        """Determine which columns exist in the DataFrame.

        Given a raw payables workbook, determine which columns are already in
        the workbook and return the index after which columns need to be added.

        Params:
            original (pd.DataFrame): The original dataframe being scanned for
            columns

        Returns:
            int: number of columns in dataframe
        """

        n = len(original.columns.values.tolist())
        return n

    ####################
    # class properties #
    ####################
    # @property
    def wb_path(self):
        """Path to payables workbook"""
        return PayablesWorkbook.payables_path + self.stem + self.f_name

    # @wb_path.setter
    # def wb_path(self, wb_path):
    #     """Needed for class reconstruction via pandas built-in methods"""
    #     pass

    @property
    def payables_date(self):
        return self._payables_date

    @payables_date.setter
    def payables_date(self, date: str | datetime) -> None:
        if isinstance(date, str):
            self.payables_date_from_str(date)
        elif isinstance(date, datetime):
            self.payables_date_from_dt(date)
        elif date is None:
            pass
            # raise TypeError

    def payables_date_from_str(self, date: str) -> None:
        if check_date(date):
            self._payables_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            raise TypeError

    def payables_date_from_dt(self, date: datetime):
        self._payables_date = date
        return 1

    @property
    def stem(self):
        return self._stem

    @property
    def f_name(self):
        return self._f_name

    @stem.setter
    def stem(self, date: datetime | str):
        if isinstance(date, datetime):
            self.stem_from_datetime(date)
        elif isinstance(date, str):
            self.stem_from_str(date)
        elif date is None:
            pass

    def stem_from_datetime(self, date):
        formats = ["%Y", "%Y%m", "%Y-%m-%d"]
        dates = [self.formatted_date(f_str) for f_str in formats]

        self._stem = "/" + "/".join(dates)
        self._f_name = "/" + dates[2] + " Payables.xlsx"

    def stem_from_str(self, date: str):
        self._stem = date
        self._f_name = "/" + date.split("/")[-1] + " Payables.xlsx"

    @f_name.setter
    def f_name(self, f_name: str):
        self._f_name = f_name

    #################
    # class methods #
    #################
    def formatted_date(self, format_str: str):
        """Return a formatted date string"""
        return self.payables_date.strftime(format_str)

    def insert_invoice(self, invoice_data: list):
        """Add an invoice to the bottom of the workbook"""
        self.loc[len(self.index)] = invoice_data

        self.move_files()
        self.save_workbook()

    def remove_invoice(self, index: list[int] | str):
        """Removed invoices at given indexes"""
        if isinstance(index, list):
            for ind in index:
                self.drop(index=ind, inplace=True)
        else:
            self.drop(index=index, inplace=True)

        self.reset_index(drop=True, inplace=True)
        self.save_workbook()

    def path_exists(self, path: str):
        if os.path.exists(path):
            return True
        else:
            os.makedirs(path)
            return False

    def new_workbook(self):
        """Create a new blank payables file for a given date"""
        cols = PayablesWorkbook.column_headers
        df = pd.DataFrame(columns=cols)
        # with pd.ExcelWriter(path=self.wb_path, engine="openpyxl") as writer:
        df.to_excel(self.wb_path(), sheet_name="Invoices", index=False)

    def save_workbook(self):
        # with pd.ExcelWriter(path=self.wb_path, engine="openpyxl") as writer:
        self.to_excel(self.wb_path(), sheet_name="Invoices", index=False)

    def move_files(self):
        """Move invoice files from Downloads to relevant payables folder with
        new names"""
        zipped_paths = self.create_new_paths()

        for old, new in zipped_paths:
            self.move_a_file(old, new)
        
    def move_a_file(self, old_path: str, new_path: str) -> None:
        while True:
            try:
                shutil.move(old_path, new_path)
                break
            except PermissionError:
                print("Close the file!")
                input()
            except FileNotFoundError:
                print("Files missing!")
                print(f"\tcannot find file {old_path}")
                input()
                break

    def create_new_paths(self):
        """Create a zipped list of an old path and a new path for invoice files"""
        old_paths = self.get_invoice_files()
        new_paths = []

        for path in old_paths:
            self.construct_new_path(path, new_paths)

        zipped = zip(old_paths, new_paths)

        return zipped

    def construct_new_path(self, old_path: str, add_to_list: list):
        """Construct a new path for a given invoice file path in downloads"""
        root = self.construct_move_to_root()
        new_f_name = self.create_new_fname()
        extension = old_path.split(".")[-1]
        full_path = root + new_f_name + extension
        add_to_list.append(full_path)

    def construct_move_to_root(self):
        """Construct root for payables folder"""
        date = self.payables_date.strftime("%Y-%m-%d")
        no_date_path = self.stem.replace("/" + date, "")
        root = PayablesWorkbook.payables_path + "/" + no_date_path + "/"
        return root

    def create_new_fname(self):
        """Create new name for invoice file

        Uses vendor and invoice_number to generate a name to be used with the
        new invoice files.
        If the invoice is a credit card payment, the vendor name will include
        the CC user's initials.
        """
        vendor, invoice_num = self.get_entered_data()
        new_f_name = f"{vendor} - {invoice_num}" + "."
        return new_f_name

    def get_entered_data(self):
        """Get input data for most recent invoice"""
        row = self.loc[len(self.index) - 1]
        vendor = self.get_vendor(row)
        invoice_num = row["Invoice #"]
        clean_invoice = self.clean_invoice_num(invoice_num)
        return (vendor, clean_invoice)

    def get_vendor(self, row: pd.Series):
        """Returns vendor, or CC User and Vendor for CC charges"""
        vendor = row["Vendor"]
        if row["CC"] == 1:
            vendor = row["CC User"] + " - " + vendor
        return vendor

    def clean_invoice_num(self, invoice_num: str):
        """Replace any forward slashes in invoice names with underscores"""
        return invoice_num.replace("/", "_")

    def get_invoice_files(self):
        """Get files in download folder"""
        drive = "C:"
        downloads = drive + os.environ["HOMEPATH"].replace("\\", "/") + "/Downloads"
        files = list(filter(lambda x: ".ini" not in x, os.listdir(downloads)))
        old_paths = [downloads + "/" + file for file in files]

        return old_paths

    def merge_vendors(self) -> pd.DataFrame:
        vendors = pd.read_excel(self.vendors_path, "Vendors",
                                dtype={
                                    "ACH ABA": str, 
                                    "ACH Account Number": str
                                })
        vendors_small = vendors[[
            "Vendor",
            "Company",
            "Expense Category",
            "Approver",
            "Payment Type",
            "QB Mapping",
            "Account Mapping",
            "ACH ABA",
            "ACH Account Number",
            "ACH Vendor Name",
        ]].copy(deep=True)
        return self.merge(right=vendors_small, how="left", on="Vendor")