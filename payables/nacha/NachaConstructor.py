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
        """Gets needed columns, allowing for different source tables"""
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
        files = []
        id_modifiers = ["A", "B", "C", "D"]
        counter = 0
        for i in NachaConstructor.company_names.keys():
            try:
                trxs = self.trx_table.loc[self.trx_table["Simplex2"] == i]
            except KeyError:
                trxs = self.trx_table.loc[self.trx_table["Company"] == i]
                

            transactions = self.construct_transactions(trxs)
            batch = self.construct_batch(transactions, i, "0000001")
            file = self.file_constructor([batch], i, id_modifiers[counter])

            counter += 1

            files.append(file)

        return files
    
    def group_trx_by_company(self, data: pd.DataFrame) -> pd.DataFrame:
        """Group payments by company for one payment per vendor."""

        vendors = data[self.vendor_col].unique()
        for vendor in vendors:
            vendor_mask = data[self.vendor_col] == vendor
            vendor_invoice_data = data.loc[vendor_mask].copy(deep=True)
            
    def group_vendor_data(self, 
                          vendor_data: pd.DataFrame) -> tuple[np.float64 | str]:
        """Returns the vendor data as a tuple of sum and joined invoice nums."""

        total_amount = vendor_data["Amount"].sum(skipna=True)
        invoice_str = " ".join(vendor_data["Invoice #"])
    
    def get_invoice_str(self, invoice_nums: pd.Series) -> str:
        """Creates the invoice string for the vendor row.
        
        The addenda to the ACH is limited to 80 chars. This function takes a 
        series of strings and joins the whole strings or equal-length 
        parts of each string."""

        invoice_data = pd.DataFrame(invoice_nums)
        joined_invs = " ".join(invoice_data["Invoice #"].tolist())
        if len(joined_invs) < 80:
            return joined_invs

        print("Over 80")
        invoice_data["str_len"] = invoice_data["Invoice #"].apply(len)
        total_len = invoice_data["str_len"].sum() + len(invoice_data.index) - 1
        
        if total_len > 80:
            num_invoices = len(invoice_data.index)
            len_per_num = np.floor_divide(80, num_invoices)
            invoice_data["start_index"] = invoice_data["str_len"] - len_per_num
            replace_mask = invoice_data["start_index"] < 0
            invoice_data["start_index"] = invoice_data["start_index"].mask(
                replace_mask, 0
            )
            # invoice_data["sliced_inv_num"] = invoice_data["Invoice #"].str.slice

def get_test_data() -> pd.DataFrame:
    path = '/'.join([
        'C:/gdrive/Shared drives/accounting/Payables',
        '2025/202508/2025-08-31/2025-08-31 Payables.xlsm'
    ])
    invoices = pd.read_excel(io=path, sheet_name="Invoices")
    return invoices

def debug() -> None:
    data = get_test_data()
    constructor = NachaConstructor(
        trx_table=data,
        value_date="20250930",
        debug=False
    )
    bgc = data.loc[data["Vendor"] == "BGC"].copy(deep=True)
    bgc_invoices = bgc["Invoice #"]
    inv_str = constructor.get_invoice_str(bgc_invoices)
    print(inv_str)

if __name__ == "__main__":
    debug()