import pandas as pd
import numpy as np
from datetime import datetime
import os

class JECreator():
    companies = ['Holdings', 'Technologies', 'Investments', 'Trading']

    def __init__(self, date: datetime):
        self.date = date
        self.je_headers = [
            'Bill No.',
            'Vendor',
            'Bill Date',
            'Due Date',
            'Memo',
            'Type',
            'Category/Account',
            'Description',
            'Amount',
            'Payment Type'
        ]
        self.je_data = {
            col: data for col, data in zip(
                self.je_headers,
                [[] for i in range(len(self.je_headers))]
            )
        }
        self.vendors = self.get_vendor_map()
        self.coas = self.get_coas()
        self.invoices = self.get_invoice_data()
    
    def get_vendor_map(self) -> pd.DataFrame:
        vendor_path = 'C:/gdrive/Shared drives/accounting' \
            + '/patrick_data_files/ap/Vendors.xlsx' 
        vendor_mapping = pd.read_excel(vendor_path, 'Vendors')
        vendor_mapping = vendor_mapping[
            ['Vendor', 'QB Mapping', 'Account Mapping']
        ]
        return vendor_mapping
    
    def get_coas(self) -> dict[str, pd.DataFrame]:
        """Get chart of accounts for each company"""
        coas = {co: '' for co in JECreator.companies}
        for co in JECreator.companies:
            coa_path = 'C:/gdrive/Shared drives/accounting/' \
                + 'patrick_data_files/gl_account_mappings/' \
                + f'Simplex {co}_Account List.xlsx'
            coa = pd.read_excel(coa_path, 'Sheet1', skiprows=3)
            no_total_line = coa.loc[coa['Account #'] != 'TOTAL']
            cleaned_coa = self.clean_account_mapping(no_total_line)
            coas[co] = cleaned_coa
        return coas
        
    def get_invoice_data(self):
        ap_path = '/'.join([
            'C:/gdrive/Shared drives/accounting/Payables',
            str(self.date.year),
            self.date.strftime('%Y%m'),
            self.date.strftime('%Y-%m-%d'),
            f'{self.date.strftime('%Y-%m-%d')} Payables.xlsm'
        ])
        invoices_df = pd.read_excel(ap_path, 'Invoices')
        return invoices_df
        
    def generate_all_bills(self) -> dict[str, pd.DataFrame]:
        """Create bills for all companies, separated into dataframes for every
        140 bills"""
        company_bill_sheets = {co: '' for co in JECreator.companies}

        for co in JECreator.companies:
            co_payables = self.filter_payables(co)
            bill_tables = self.make_company_bills(co_payables)

            company_bill_sheets[co] = bill_tables

        return company_bill_sheets

    def make_company_bills(self, invoices: pd.DataFrame) -> list[pd.DataFrame]:
        """Create bill sheets for one specific company"""
        bill_dfs = []
        num_invoices = len(invoices.index)
        while num_invoices > 0:
            start = np.floor_divide(num_invoices, 140) * 140
            end = start + 140
            if start + 140 > num_invoices:
                end = num_invoices - 1

            bills = self.create_bills(invoices.iloc[start:end])
            num_invoices -= len(bills.index)
            bill_dfs.append(bills)

        return bill_dfs
        
    def clean_account_mapping(self, accounts: pd.DataFrame):
        accounts['Account #'].fillna(0, inplace=True)
        accounts.drop(accounts.iloc[-3:].index, inplace=True)
        accounts['Account #'] = accounts['Account #'].astype(int)

    def get_company_invoices(self, company: str):
        payables = self.invoices[self.invoices['Simplex2'] == company].copy()
        payables = self.modify_invoice_table(company, payables)
        return payables
    
    def modify_invoice_table(self, company: str, 
                             raw_invoices: pd.DataFrame) -> pd.DataFrame:
        """Merge vendors and account mappings to company invoice table"""
        raw_invoices = raw_invoices.merge(
            right=self.vendors,
            how='left', 
            on='Vendor'
        )
        raw_invoices['Account Mapping'].fillna(0, inplace=True)
        raw_invoices = raw_invoices.merge(
            right=self.coas[company][
                ['Account #', 'Full name', 'JE Account Name']
            ],
            how='left',
            left_on = 'Account Mapping',
            right_on='Account #'
        )
        raw_invoices = raw_invoices.rename(
            columns={'JE Account Name': 'Expense Account JE'},
            inplace=True
        )
    
    def create_bills(self, invoices: pd.DataFrame) -> pd.DataFrame:
        """Convert invoice entries from payables data to a bill item for QB"""
        bills = pd.DataFrame(columns=self.je_headers)
        for i, row in invoices.iterrows():
            print(f'Processing bill {row['Vendor']} - {row['Invoice #']}',
                    end = '\r')
            bill = self.bill_creator(row)
            bills = pd.concat([bills, bill])
            bills = bills.reset_index(drop=True)
        self.clean_bill_dfs(bills)
        return bills

    def clean_bill_dfs(self, company_data: pd.DataFrame):
        """Adjust column types and fix duplicate invoice names"""
        company_data['Bill No.'] = company_data['Bill No.'].astype(str)
        company_data['Memo'] = company_data['Memo'].astype(str)
        company_data['Description'] = company_data['Description'].astype(str)
        company_data = self.fix_dupe_bill_nums(
            company_data,
            'Vendor',
            'Bill No.'
        )
    
    def fix_dupe_bill_nums(self, df: pd.DataFrame,
                           vendor_col: str, bill_col: str) -> pd.DataFrame:
        """Convert duplicate bill numbers to usable numbers"""
        vendors = list(df[vendor_col].values)
        bill_nos = list(df[bill_col].values)
        qb_mapping_and_bills = [
            str(bill_no) + str(vendor) for bill_no, vendor in zip(
                bill_nos,
                vendors
            )
        ]

        for i in range(len(bill_nos)):
            c1 = bill_nos.count(bill_nos[i])
            c2 = qb_mapping_and_bills.count(qb_mapping_and_bills[i])
            if c1 > 1 and c2 == 1:
                new_no = vendors[i][0:4] + bill_nos[i]
                bill_nos[i] = new_no
            else:
                continue

        df[bill_col] = bill_nos
        return df

    def bill_creator(self, df_row: pd.Series) -> pd.DataFrame:
        """Create a bill from an invoice entry"""
        bill = pd.DataFrame(columns=self.je_headers)
        
        bill.loc[0, 'Bill No.'] = df_row['Invoice #']
        if len(df_row['Invoice #']) > 21:
            bill.loc[0, 'Bill No.'] = df_row['Invoice #'][-21:]
            
        bill.loc[0, 'Vendor'] = df_row['QB Mapping']
        bill.loc[0, 'Bill Date'] = self.date.strftime('%m/%d/%Y')
        bill.loc[0, 'Memo'] = df_row['Invoice #']
        bill.loc[0, 'Type'] = 'Category Details'
        bill.loc[0, 'Category/Account'] = df_row['Expense Account JE']
        bill.loc[0, 'Description'] = df_row['Invoice #']
        bill.loc[0, 'Amount'] = df_row['Amount']
        bill.loc[0, 'Payment Type'] = df_row['Payment Type']
        
        return bill
    
def run_payables():
    """Run payables process for a specific date and create the bill import files for QB"""
    year = int(input('Year:\n>\t'))
    month = int(input('Month:\n>\t'))
    day = int(input('Day:\n>\t'))

    batch_date = datetime(year, month, day)
    payables = JECreator(batch_date)
    bill_dfs = payables.generate_bills()

    for i in bill_dfs.keys():
        for j in range(len(i)):
            company_name = i
            if j > 1:
                company_name += str(j)
            
            bill_dfs[i][j].to_csv('/'.join(
                f'{os.environ['HOMEPATH'].replace('\\','/')}',
                f'Downloads',
                f'{company_name} {batch_date.strftime('%Y-%m-%d')} Bills.csv',
            ), index=False)