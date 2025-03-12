import pandas as pd
from datetime import datetime
import os

class JECreator():
    def __init__(self, date: datetime):
        self.date = date
        self.je_headers = ['Bill No.', 'Vendor', 'Bill Date', 'Due Date', 'Memo', 'Type', 'Category/Account', 'Description', 'Amount', 'Payment Type']
        self.je_data = {col: data for col, data in zip(self.je_headers, [[] for i in range(len(self.je_headers))])}
    
    def file_getter(self):
        ap_path = f'C:/gdrive/Shared drives/accounting/Payables/{str(self.date.year)}/{self.date.strftime('%Y%m')}/{self.date.strftime('%Y-%m-%d')}/{self.date.strftime('%Y-%m-%d')} Payables.xlsm'
        invoices_df = pd.read_excel(ap_path, 'Invoices')
        vendor_mapping = pd.read_excel('C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx', 'Vendors')
        
        companies = ['Holdings', 'Technologies', 'Investments', 'Trading']
        coas = {co: '' for co in companies}
        for co in companies:
            coa_path = f'C:/gdrive/Shared drives/accounting/patrick_data_files/gl_account_mappings/Simplex {co}_Account List.xlsx'
            coa = pd.read_excel(coa_path, 'Sheet1', skiprows=3)
            coas[co] = coa
        
        return (invoices_df, vendor_mapping, coas)
        
        
    def initiator(self, payables: pd.DataFrame, vendor_mapping: pd.DataFrame, account_mappings: dict):
        # Map vendor mapping & vendor account to payables df
        # Pass rows through je function which returns a JE for each payable item
        companies = ['Holdings', 'Investments', 'Technologies', 'Trading']
        bill_dfs = {co: pd.DataFrame(columns=self.je_headers) for co in companies}
        for co in companies:
            vendor_mapping = vendor_mapping[['Vendor', 'QB Mapping', 'Account Mapping']]
            co_payables = payables[payables['Simplex2'] == co].copy()
            co_payables = co_payables.merge(right=vendor_mapping, how='left', on='Vendor')
            # co_payables.to_csv(f'C:/Users/phughes_simplextradi/Downloads/{co}_payables_mapping_pd.csv')
            co_payables['Account Mapping'] = co_payables['Account Mapping'].fillna(0)
            account_mappings[co]['Account #'] = account_mappings[co]['Account #'].fillna(0)
            # account_mapping.to_csv('C:/Users/phughes_simplextradi/Downloads/account_mapping_pd.csv')
            account_mappings[co] = account_mappings[co].drop(account_mappings[co].iloc[-3:].index)
            account_mappings[co]['Account #'] = account_mappings[co]['Account #'].astype(int)
            
            # payables.to_csv('C:/Users/phughes_simplextradi/Downloads/payables_after_vendor_merge.csv')
            
            co_payables = co_payables.merge(right=account_mappings[co][['Account #', 'Full name', 'JE Account Name']], how='left', left_on = 'Account Mapping', right_on='Account #')
            co_payables = co_payables.rename(columns={'JE Account Name': 'Expense Account JE'})
            # payables.to_csv('C:/Users/phughes_simplextradi/Downloads/payables_after_coa_merge.csv')
            
            for i, row in co_payables.iterrows():
                bill = self.bill_creator(row)

                bill_dfs[co] = pd.concat([bill_dfs[co], bill])
                bill_dfs[co] = bill_dfs[co].reset_index(drop=True)
        
        for i in bill_dfs.keys():
            
            bill_dfs[i]['Bill No.'] = bill_dfs[i]['Bill No.'].astype(str)
            bill_dfs[i]['Memo'] = bill_dfs[i]['Memo'].astype(str)
            bill_dfs[i]['Description'] = bill_dfs[i]['Description'].astype(str)
            bill_dfs[i] = self.fix_dupe_bill_nums(bill_dfs[i], 'Vendor', 'Bill No.')
    
        return bill_dfs
    
    def fix_dupe_bill_nums(self, df, vendor_col, bill_col):
        vendors = list(df[vendor_col].values)
        bill_nos = list(df[bill_col].values)
        qb_mapping_and_bills = [str(bill_no) + str(vendor) for bill_no, vendor in zip(bill_nos, vendors)]

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

    def bill_creator(self, df_row):
        # ['Bill No.', 'Vendor', 'Bill Date', 'Due Date', 'Memo', 'Type', 'Category/Account', 'Description', 'Amount']
        bill = pd.DataFrame(columns=self.je_headers)
        
        if len(df_row['Invoice #']) > 21:
            bill.loc[0, 'Bill No.'] = df_row['Invoice #'][-21:]
        else:
            bill.loc[0, 'Bill No.'] = df_row['Invoice #']
            
        bill.loc[0, 'Vendor'] = df_row['QB Mapping']
        bill.loc[0, 'Bill Date'] = self.date.strftime('%m/%d/%Y')
        bill.loc[0, 'Memo'] = df_row['Invoice #']
        bill.loc[0, 'Type'] = 'Category Details'
        bill.loc[0, 'Category/Account'] = df_row['Expense Account JE']
        bill.loc[0, 'Description'] = df_row['Invoice #']
        bill.loc[0, 'Amount'] = df_row['Amount']
        bill.loc[0, 'Payment Type'] = df_row['Payment Type']
        
        return bill

    
    def je_creator(self, df_row, journal_no):
        je = pd.DataFrame(columns=self.je_headers)
        row_counter = 0
        
        for i, func in zip(range(4), [self.credit_cash, self.debit_ap, self.credit_ap, self.debit_expense]):
            if row_counter % 1 == 0:
                journal_no += 1
            
            je_row = func(df_row, journal_no)
            vals = self.convert_dict_vals_to_list(je_row)
            je.loc[i] = vals
            
            row_counter += 0.5

        return je
    
    def convert_dict_vals_to_list(self, row: dict):
        vals = []
        for i in list(row.keys()):
            vals.append(row[i])
            
        return vals
        
    def credit_cash(self, row, journal_number):
        cr_cash_row = {col: val for col, val in zip(self.je_headers, ['' for i in range(len(self.je_headers))])}
        cr_cash_row['JournalNo'] = journal_number
        cr_cash_row['JournalDate'] = self.date.strftime('%m/%d/%Y')
        cr_cash_row['AccountName'] = '10000 Chase Checking'
        cr_cash_row['Debits'] = row['Amount']
        cr_cash_row['Description'] = row['Invoice #']
        cr_cash_row['Name'] = row['QB Mapping']
        cr_cash_row['Memo'] = row['Invoice #']
        cr_cash_row['Currency'] = 'USD'
        
        return cr_cash_row
    
    def debit_ap(self, row, journal_number):
        dr_ap_row = {col: val for col, val in zip(self.je_headers, ['' for i in range(len(self.je_headers))])}
        dr_ap_row['JournalNo'] = journal_number
        dr_ap_row['AccountName'] = '21000 Accounts Payable'
        dr_ap_row['Credits'] = row['Amount']
        dr_ap_row['Description'] = row['Invoice #']
        dr_ap_row['Name'] = row['QB Mapping']
        dr_ap_row['Memo'] = row['Invoice #']
        dr_ap_row['Currency'] = 'USD'
        
        return dr_ap_row
    
    def credit_ap(self, row, journal_number):
        cr_ap_row = {col: val for col, val in zip(self.je_headers, ['' for i in range(len(self.je_headers))])}
        cr_ap_row['JournalNo'] = journal_number
        cr_ap_row['JournalDate'] = self.date.strftime('%m/%d/%Y')
        cr_ap_row['AccountName'] = '21000 Accounts Payable'
        cr_ap_row['Credits'] = row['Amount']
        cr_ap_row['Description'] = row['Invoice #']
        cr_ap_row['Name'] = row['QB Mapping']
        cr_ap_row['Memo'] = row['Invoice #']
        cr_ap_row['Currency'] = 'USD'
        
        return cr_ap_row
    
    def debit_expense(self, row, journal_number):
        dr_exp_row = {col: val for col, val in zip(self.je_headers, ['' for i in range(len(self.je_headers))])}
        dr_exp_row['JournalNo'] = journal_number
        dr_exp_row['AccountName'] = row['Expense Account JE']
        dr_exp_row['Debits'] = row['Amount']
        dr_exp_row['Description'] = row['Invoice #']
        dr_exp_row['Name'] = row['QB Mapping']
        dr_exp_row['Memo'] = row['Invoice #']
        dr_exp_row['Currency'] = 'USD'
        
        return dr_exp_row
    
def run_payables():
    year = int(input('Year:\n>\t'))
    month = int(input('Month:\n>\t'))
    day = int(input('Day:\n>\t'))

    batch_date = datetime(year, month, day)

    payables = JECreator(batch_date)

    invoices, vendors, coas = payables.file_getter()

    bill_dfs = payables.initiator(payables=invoices, vendor_mapping=vendors, account_mappings=coas)

    for i in bill_dfs.keys():
        bill_dfs[i].to_csv(f'{os.environ['HOMEPATH'].replace('\\','/')}/Downloads/{i} {batch_date.strftime('%Y-%m-%d')} Bills.csv', index=False)