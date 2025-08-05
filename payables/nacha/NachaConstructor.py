from payables.nacha.NachaFile import *
import pandas as pd
from datetime import datetime


class NachaConstructor:
    company_ids = {
        "Holdings": "9620118001",
        "Investments": "9684771001",
        "Technologies": "9711101001",
        "Trading": "9007310001",
    }
    company_names = {
        "Holdings": "SIMPLEX HOLDINGS LLC",
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

    def construct_transactions(self, trx_table):
        transactions_list = []
        sequence_no = 101
        # Debug
        # print(trx_table)

        for i, row in trx_table.iterrows():
            # Debug
            # print(f'Vendor: {row['Vendor']} // Mapped Vendor: {row['Vendor Name']} // ABA: {row['Vendor ABA']} // Type: {type(row['Vendor ABA'])}')

            transaction = TransactionEntry(
                row["Vendor Name"],
                row["Amount"],
                row["Invoice #"],
                row["Vendor ABA"],
                row["Vendor Account"],
                "0" * (7 - len(str(sequence_no))) + str(sequence_no),
                debug=self.debug,
            )
            # Debug
            # if row['Simplex2'] == 'Investments':
            #     print(f'Input amount = {row['Amount']}')

            transactions_list.append(transaction)
            sequence_no += 1

        return transactions_list

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
            trxs = self.trx_table.loc[self.trx_table["Simplex2"] == i]

            transactions = self.construct_transactions(trxs)

            # Debug
            # if i == 'Investments':
            #     for j in transactions:
            #         print(f'Output amount = {j.no_decimal_amount}')

            batch = self.construct_batch(transactions, i, "0000001")
            file = self.file_constructor([batch], i, id_modifiers[counter])

            counter += 1

            files.append(file)

        return files
