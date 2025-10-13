import os
import sys
sys.path.append('/'.join([os.environ["HOMEPATH"], 'accounting']))
from payables.nacha.NachaFile import *
import pandas as pd
from datetime import datetime
import numpy as np


class NachaConstructor:
    company_ids = {
        "Holdings": "9542988001",
        "Investments": "9684771001",
        "Technologies": "9711101001",
        "Trading": "9007310001",
    }
    company_names = {
        "Holdings": "SIMPLEX HOLDCO",
        "Investments": "SIMPLEX INVESTMENTS LLC",
        "Technologies": "SIMPLEX TECHNOLOGIES",
        "Trading": "SIMPLEX TRADING, LLC",
    }

    company_abas = {
        "Holdings": "071000013",
        "Investments": "071000013",
        "Technologies": "071000013",
        "Trading": "071000013",
    }

    def __init__(self, trx_table: pd.DataFrame, value_date, debug=False):
        self.trx_table = trx_table
        self.value_date = value_date
        self.debug = debug
        self.get_col_names()

    def construct_transactions(self, trx_table):
        """Given a table of transactions, encodes each transaction as a
        string in NACHA format and returns them as a list."""

        transactions_list = []
        sequence_no = 101
        for i, row in trx_table.iterrows():
            transaction = TransactionEntry(
                row[self.vendor_col],
                row["Amount"],
                row["Invoice #"],
                row[self.aba_col],
                row[self.account_col],
                "0" * (7 - len(str(sequence_no))) + str(sequence_no),
                debug=self.debug,
            )
            transactions_list.append(transaction)
            sequence_no += 1

        return transactions_list
    
    def get_col_names(self) -> None:
        """Gets columns required for construct_transactions, allowing for
        different source tables."""

        cols = [
            ["Vendor Name", "ACH Vendor Name"],
            ["Vendor ABA", "ACH ABA"],
            ["Vendor Account", "ACH Account Number"]
        ]
        name_index = 0
        try:
            column_data = self.trx_table[cols[0][0]]
        except KeyError:
            name_index = 1
        self.vendor_col = cols[0][name_index]
        self.aba_col = cols[1][name_index]
        self.account_col = cols[2][name_index]

    def construct_batch(self, transactions, company_name, batch_number):
        """Construct NACHA batch - joined transaction strings grouped with
        header and footer information."""

        batch = Batch(
            company_name=NachaConstructor.company_names[company_name],
            company_id=NachaConstructor.company_ids[company_name],
            co_entry_descr="Payables",
            effective_date=self.value_date,
            orig_dfi_id=NachaConstructor.company_abas[company_name][0:8],
            batch_number=batch_number,
            trx_entries=transactions,
        )
        return batch

    def file_constructor(self, batches, company_name, file_id_modifier):
        """Adds NACHA file header and footer information to existing batch
        data."""

        file = NachaFile(
            bank_aba=NachaConstructor.company_abas[company_name],
            company_id=NachaConstructor.company_ids[company_name],
            file_creation_date=datetime.now().strftime("%y%m%d%H%M"),
            file_id_modifier=file_id_modifier,
            orig_bank_name="JPMORGAN CHASE BANK, N.A.",
            co_name=NachaConstructor.company_names[company_name],
            batches=batches,
        )

        return file

    def main(self):
        """Creates and returns NACHA payment files ready to be written to disk.
        
        Returns a string for each operating company with each company's
        transactions encoded and formatted such that when written to disk in a 
        text file, the resulting file may be uploaded to JP Morgan for payment.
        """

        files = []
        id_modifiers = ["A", "B", "C", "D"]
        counter = 0
        for i in NachaConstructor.company_names.keys():
            try:
                trxs = self.trx_table.loc[self.trx_table["Simplex2"] == i]
            except KeyError:
                trxs = self.trx_table.loc[self.trx_table["Company"] == i]
                
            # company_trxs_grouped = self.get_grouped_trx_table(data=trxs)

            transactions = self.construct_transactions(trxs)
            batch = self.construct_batch(transactions, i, "0000001")
            file = self.file_constructor([batch], i, id_modifiers[counter])

            counter += 1

            files.append(file)

        return files
    
    def get_grouped_trx_table(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handler function for grouping transactions by vendor then merging
        the vendors table to the resulting table."""

        grouped = self.group_trx_by_vendor(data)
        merged = self.join_vendor_table(grouped, col="ACH Vendor Name")
        return merged

    def join_vendor_table(self, left: pd.DataFrame, col: str) -> pd.DataFrame:
        """Left-join vendors table to another table on the given column."""

        vendors = self.get_vendor_table()
        short_vendors = vendors[[
            "ACH Vendor Name",
            "ACH ABA",
            "ACH Account Number"
        ]].copy(deep=True)
        merged = left.merge(right=short_vendors, how="left", on=col)
        return merged
    
    def get_vendor_table(self) -> pd.DataFrame:
        """Read vendors table into memory and return the table."""

        path = '/'.join([
            "C:/gdrive/Shared drives/accounting/patrick_data_files",
            "ap/Vendors.xlsx"
        ])
        vendors = pd.read_excel(io=path, sheet_name="Vendors")
        return vendors
    
    def group_trx_by_vendor(self, data: pd.DataFrame) -> pd.DataFrame:
        """Group payments by company for one payment per vendor."""

        # Need to think about edge cases when current addendum algorithm won't 
        # work
        pre_sort_vendors = data[self.vendor_col].unique().tolist() 
        vendors = sorted(pre_sort_vendors)
        table = self.create_unique_payment_table(vendors)
        for i, row in table.iterrows():
            filtered_on_vendor = data.loc[
                data[self.vendor_col] == row["ACH Vendor Name"]
            ]
            inv_total, addendum = self.group_vendor_data(filtered_on_vendor)
            table.loc[i, "Amount"] = inv_total
            table.loc[i, "Invoice #"] = addendum

        return table
    
    def create_unique_payment_table(self, vendors: list[str]) -> pd.DataFrame:
        """Returns a dataframe with columns for vendor, total invoiced amount
        and the addendum string"""

        zeroes = [np.float64(0) for i in vendors]
        empty_strs = ["" for i in vendors]
        data = {
            "ACH Vendor Name": vendors,
            "Amount": zeroes,
            "Invoice #": empty_strs
        }
        df = pd.DataFrame(data=data)
        return df

    def group_vendor_data(self, 
                          vendor_data: pd.DataFrame) -> tuple[np.float64 | str]:
        """Returns the vendor data as a tuple of sum and joined invoice nums."""

        total_amount = np.float64(vendor_data["Amount"].sum(skipna=True))
        invoice_str = self.get_invoice_str(vendor_data["Invoice #"])
        return (total_amount, invoice_str)
    
    def get_invoice_str(self, invoice_nums: pd.Series) -> str:
        """Creates the invoice string for the vendor row.
        
        The addenda to the ACH is limited to 80 chars. This function takes a 
        series of strings and joins the whole strings or equal-length 
        parts of each string."""

        invoice_data = pd.DataFrame(invoice_nums)
        joined_invs = " ".join(invoice_data["Invoice #"].tolist())
        total_len = len(joined_invs)
        if total_len < 80:
            return joined_invs

        invoice_data["str_len"] = invoice_data["Invoice #"].apply(len)
        num_invoices = len(invoice_data.index)
        len_per_num = np.floor_divide(80, num_invoices) - 1
        invoice_data["sliced"] = invoice_data["Invoice #"].str. \
            slice(-len_per_num)
        sliced_joined = " ".join(invoice_data["sliced"].tolist())
        return sliced_joined

