import pandas as pd
from datetime import datetime

class JECreator():
    def __init__(self, date: datetime, je_initial_no):
        self.date = date
        self.je_initial = je_initial_no
        self.je_headers = ['Bill No.', 'Vendor', 'Bill Date', 'Due Date', 'Memo', 'Type', 'Category/Account', 'Description', 'Amount']
        self.je_data = {col: data for col, data in zip(self.je_headers, [[] for i in range(len(self.je_headers))])}
    
    def file_getter(self):
        ap_path = f'C:/gdrive/Shared drives/accounting/Payables/{str(self.date.year)}/{self.date.strftime('%Y%m')}/{self.date.strftime('%Y-%m-%d')}/{self.date.strftime('%Y-%m-%d')} Payables.xlsm'
        invoices_df = pd.read_excel(ap_path, 'Invoices')
        vendor_mapping = pd.read_excel(ap_path, 'Vendors')
        
        trading_coa_path = 'C:/gdrive/Shared drives/accounting/Simplex Trading/Simplex Trading_Account List.xlsx'
        trading_coa = pd.read_excel(trading_coa_path, 'Sheet1', skiprows=3)
        
        return (invoices_df, vendor_mapping, trading_coa)
        
        
    def initiator(self, payables: pd.DataFrame, vendor_mapping: pd.DataFrame, account_mapping: pd.DataFrame):
        # Map vendor mapping & vendor account to payables df
        # Pass rows through je function which returns a JE for each payable item
        vendor_mapping = vendor_mapping[['Vendor', 'QB Mapping', 'Account Mapping']]
        payables = payables[payables['Simplex2'] == 'Trading']
        payables = payables.merge(right=vendor_mapping, how='left', on='Vendor')
        payables['Account Mapping'] = payables['Account Mapping'].fillna(0)
        account_mapping['Account #'] = account_mapping['Account #'].fillna(0)
        account_mapping.to_csv('C:/Users/phughes_simplextradi/Downloads/account_mapping_pd.csv')
        account_mapping = account_mapping.drop(account_mapping.iloc[-3:].index)
        account_mapping['Account #'] = account_mapping['Account #'].astype(int)
        
        payables.to_csv('C:/Users/phughes_simplextradi/Downloads/payables_after_vendor_merge.csv')
        
        payables = payables.merge(right=account_mapping[['Account #', 'Full name', 'JE Account Name']], how='left', left_on = 'Account Mapping', right_on='Account #')
        payables = payables.rename(columns={'JE Account Name': 'Expense Account JE'})
        payables.to_csv('C:/Users/phughes_simplextradi/Downloads/payables_after_coa_merge.csv')
        
        bill_df = pd.DataFrame(columns=self.je_headers)
        
        for i, row in payables.iterrows():
            if row['Simplex2'] == 'Trading':
                
                bill = self.bill_creator(row)

                bill_df = pd.concat([bill_df, bill])
                bill_df = bill_df.reset_index(drop=True)
            else:
                continue
            
        bill_df['Bill No.'] = bill_df['Bill No.'].astype(str)
        bill_df['Memo'] = bill_df['Memo'].astype(str)
        bill_df['Description'] = bill_df['Description'].astype(str)
    
        return bill_df
    
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