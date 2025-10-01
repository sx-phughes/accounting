import pandas as pd
import numpy as np
from datetime import datetime
import os, sys

sys.path.append("/".join([os.environ["HOMEPATH"], "accounting"]))
from Interface.payables_wb import PayablesWorkbook
from Interface.functions import ui_get_date


class JECreator:
    companies = ["Holdings", "Technologies", "Investments", "Trading"]

    def __init__(self, date: datetime):
        self.date = date
        self.standard_wb = True
        self.je_headers = [
            "Bill No.",
            "Vendor",
            "Bill Date",
            "Due Date",
            "Memo",
            "Type",
            "Category/Account",
            "Description",
            "Amount",
            "Payment Type",
        ]
        self.je_data = {
            col: data
            for col, data in zip(
                self.je_headers, [[] for i in range(len(self.je_headers))]
            )
        }
        self.vendors = self.get_vendor_map()
        self.coas = self.get_coas()
        self.invoices = self.get_invoice_data()

    def get_vendor_map(self) -> pd.DataFrame:
        vendor_path = (
            "C:/gdrive/Shared drives/accounting"
            + "/patrick_data_files/ap/Vendors.xlsx"
        )
        vendor_mapping = pd.read_excel(vendor_path, "Vendors")
        vendor_mapping = vendor_mapping[
            ["Vendor", "QB Mapping", "Account Mapping"]
        ]
        return vendor_mapping

    def get_coas(self) -> dict[str, pd.DataFrame]:
        """Get chart of accounts for each company"""

        coas = {co: "" for co in JECreator.companies}
        for co in JECreator.companies:
            coa_path = (
                "C:/gdrive/Shared drives/accounting/"
                + "patrick_data_files/gl_account_mappings/"
                + f"Simplex {co}_Account List.xlsx"
            )
            coa = pd.read_excel(coa_path, "Sheet1", skiprows=3)
            no_total_line = coa.loc[coa["Account #"] != "TOTAL"]
            cleaned_coa = self.clean_account_mapping(no_total_line)
            coas[co] = cleaned_coa
        return coas

    def get_invoice_data(self):
        ap_path = "/".join(
            [
                "C:/gdrive/Shared drives/accounting/Payables",
                str(self.date.year),
                self.date.strftime("%Y%m"),
                self.date.strftime("%Y-%m-%d"),
                f"{self.date.strftime('%Y-%m-%d')} Payables.xlsm",
            ]
        )
        try:
            invoices_df = pd.read_excel(ap_path, "Invoices")
        except FileNotFoundError:
            invoices_df = PayablesWorkbook(self.date).merge_vendors()
            self.standard_wb = False

        return invoices_df

    def generate_all_bills(self) -> dict[str, pd.DataFrame]:
        """Create bills for all companies, separated into dataframes for every
        140 bills"""

        company_bill_sheets = {co: "" for co in JECreator.companies}

        for co in JECreator.companies:
            co_payables = self.get_company_invoices(co)
            bill_tables = self.make_company_bills(co_payables)
            company_bill_sheets[co] = bill_tables

        return company_bill_sheets

    def make_company_bills(self, invoices: pd.DataFrame) -> list[pd.DataFrame]:
        """Create bill sheets for one specific company"""

        invoices_copy = invoices.copy(deep=True)
        bill_dfs = []
        num_invoices = len(invoices_copy.index)
        print("initial num invoices = %d" % num_invoices)
        while num_invoices > 0:
            start = max(0, np.floor_divide(num_invoices, 140) - 1) * 140
            end = start + 140
            if end > num_invoices:
                end = num_invoices

            subset = invoices_copy.iloc[start:end]
            bills = self.create_bills(subset)
            invoices_copy = invoices_copy.drop(index=subset.index)
            num_invoices -= len(bills.index)
            bill_dfs.append(bills)

        return bill_dfs

    def clean_account_mapping(self, accounts: pd.DataFrame):
        """Fills blanks and casts types."""

        clean_accounts = accounts.copy()
        clean_accounts["Account #"] = accounts["Account #"].fillna(0)
        dropped_bottom = clean_accounts.drop(clean_accounts.iloc[-3:].index)
        dropped_bottom["Account #"] = dropped_bottom["Account #"].astype(int)
        return dropped_bottom

    def get_company_invoices(self, company: str):
        """Get dataframe of invoices filtered for a specific company"""

        col = "Company"
        if "Simplex2" in self.invoices.columns:
            col = "Simplex2"

        payables = self.invoices[self.invoices[col] == company].copy()
        payables = self.modify_invoice_table(company, payables)
        return payables

    def modify_invoice_table(
        self, company: str, raw_invoices: pd.DataFrame
    ) -> pd.DataFrame:
        """Merge vendors and account mappings to company invoice table"""

        if self.standard_wb:
            invoices = raw_invoices.copy(deep=True).merge(
                right=self.vendors, how="left", on="Vendor"
            )
        else:
            invoices = raw_invoices.copy(deep=True)

        invoices["Account Mapping"] = invoices["Account Mapping"].fillna(0)
        invoices_w_coas = invoices.merge(
            right=self.coas[company][
                ["Account #", "Full name", "JE Account Name"]
            ],
            how="left",
            left_on="Account Mapping",
            right_on="Account #",
        )
        invoices_renamed = invoices_w_coas.rename(
            columns={"JE Account Name": "Expense Account JE"}
        )
        return invoices_renamed

    def create_bills(self, invoices: pd.DataFrame) -> pd.DataFrame:
        """Convert invoice entries from payables data to a bill item for QB"""

        bills = pd.DataFrame(columns=self.je_headers)
        for i, row in invoices.iterrows():
            # print(
            #     f"Processing bill {row['Vendor']} - {row['Invoice #']}",
            #     end="\r",
            # )
            bill = self.bill_creator(row)

            if len(bills.index) > 0:
                bills = pd.concat([bills, bill])
            else:
                bills = bill

            bills = bills.reset_index(drop=True)

        clean_bills = self.clean_bill_df(bills)
        return clean_bills

    def clean_bill_df(self, company_data: pd.DataFrame):
        """Adjust column types and fix duplicate invoice names"""

        new = company_data.copy(deep=True)
        new["Bill No."] = new["Bill No."].astype(str)
        new["Memo"] = new["Memo"].astype(str)
        new["Description"] = new["Description"].astype(str)
        new = self.fix_dupe_bill_nums(new, "Vendor", "Bill No.")
        return new

    def fix_dupe_bill_nums(
        self, df: pd.DataFrame, vendor_col: str, bill_col: str
    ) -> pd.DataFrame:
        """Convert duplicate bill numbers to usable numbers"""

        vendors = list(df[vendor_col].values)
        bill_nos = list(df[bill_col].values)
        qb_mapping_and_bills = [
            str(bill_no) + str(vendor)
            for bill_no, vendor in zip(bill_nos, vendors)
        ]

        new = df.copy(deep=True)
        for i in range(len(bill_nos)):
            c1 = bill_nos.count(bill_nos[i])
            c2 = qb_mapping_and_bills.count(qb_mapping_and_bills[i])
            if c1 > 1 and c2 == 1:
                new_no = vendors[i][0:4] + bill_nos[i]
                new.loc[i, bill_col] = new_no
            else:
                continue

        return new

    def bill_creator(self, df_row: pd.Series) -> pd.DataFrame:
        """Create a bill from an invoice entry"""

        bill = pd.DataFrame(columns=self.je_headers)

        if len(str(df_row["Invoice #"])) > 21:
            bill.loc[0, "Bill No."] = str(df_row["Invoice #"])[-21:]
        else:
            bill.loc[0, "Bill No."] = str(df_row["Invoice #"])

        bill.loc[0, "Vendor"] = df_row["QB Mapping"]
        bill.loc[0, "Bill Date"] = self.date.strftime("%m/%d/%Y")
        bill.loc[0, "Memo"] = df_row["Invoice #"]
        bill.loc[0, "Type"] = "Category Details"
        bill.loc[0, "Category/Account"] = df_row["Expense Account JE"]
        bill.loc[0, "Description"] = df_row["Invoice #"]
        bill.loc[0, "Amount"] = df_row["Amount"]
        bill.loc[0, "Payment Type"] = df_row["Payment Type"]
        return bill


def get_bill_file_path(company: str, date: datetime) -> str:
    path = "/".join(
        [
            f'{os.environ['HOMEPATH'].replace('\\','/')}',
            f"Downloads",
            f"{company} {date.strftime('%Y-%m-%d')} Bills.csv",
        ]
    )
    return path


def run_payables():
    """Run payables process for a specific date and create the bill import files for QB"""

    year, month, day = ui_get_date(dt=False)

    batch_date = datetime(year, month, day)
    payables = JECreator(batch_date)
    bill_dfs = payables.generate_all_bills()

    for i in bill_dfs.keys():
        for j in range(len(bill_dfs[i])):
            company_name = i
            if j >= 1:
                company_name += str(j)

            while True:
                try:
                    bill_dfs[i][j].to_csv(
                        path_or_buf=get_bill_file_path(
                            company_name, batch_date
                        ),
                        index=False,
                    )
                    break
                except PermissionError as e:
                    print(e)
                    print("Close invoices csv file")
                    input()


if __name__ == "__main__":
    run_payables()
