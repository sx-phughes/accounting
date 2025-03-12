# Standard packages
from datetime import datetime
import os, re, shutil
import pandas as pd

# Package imports
from .functions import *


class PayablesWorkbook(pd.DataFrame):
    payables_path = 'C:/gdrive/Shared drives/Accounting/Payables'
    # Normal Properties
    _metadata = ['wb_path', 'payables_date', 'stem', 'f_name']
    
    def __init__(self, date):
        self.payables_date = date
        self.stem = self.payables_date
        super().__init__(pd.read_excel(self.wb_path, 'Invoices'))
    
    @property
    def _constructor(self):
        return PayablesWorkbook
    
    @property
    def wb_path(self):
        return PayablesWorkbook.payables_path + self.stem + self.f_name
        
    @property
    def payables_date(self):
        return self._payables_date
    
    @payables_date.setter
    def payables_date(self, date: str):
        if check_date(date):
            self._payables_date = datetime.strptime(date, '%Y-%m-%d')
        else:
            raise TypeError

    @property
    def stem(self):
        return self._stem
    
    @property
    def f_name(self):
        return self._f_name
    
    @stem.setter
    def stem(self, date: datetime):
        year = date.strftime('%Y')
        month = date.strftime('%m')

        self._stem = f'/{year}/{year}{month}/{self.payables_date.strftime('%Y-%m-%d')}'
        self._f_name = f'/{self.payables_date.strftime('%Y-%m-%d')} Payables.xlsx'

    def insert_invoice(self, invoice_data: list):
        self.loc[len(self.index)] = invoice_data

        self.move_files(invoice_data[0], invoice_data[1])
        
    def remove_invoice(self, index):
        self.drop(index=index, inplace=True)
        self.reset_index(drop=True, inplace=True)
    
    def save_workbook(self):
        with pd.ExcelWriter(self.wb_path, 'xlsxwriter') as writer:
            self.to_excel(writer, 'Invoices', index=False)

    def move_files(self, vendor: str, invoice_num: str):
        # get files in downloads
        user = os.environ['HOMEPATH'].split('\\')[-1]
        downloads = f'C:/Users/{user}/Downloads'
        files = os.listdir(downloads)

        # remove ini files from move
        files = list(filter(lambda x: '.ini' not in x, files))

        # clean invoice num
        invoice_num = invoice_num.replace('/', '_')

        # sort by date added
        #   not doing this for now - be sure to have downloads folder cleared

        # take last files added
        # rename files
        new_f_names = [f'{vendor} - {invoice_num}' + '.' + f_name.split('.')[-1] for f_name in files]

        # move to payables folder
        new_paths = [PayablesWorkbook.payables_path + self.stem.replace('/' + self.payables_date, '') + f_name for f_name in new_f_names]
        
        for old, new in zip(files, new_paths):
            shutil.move(downloads + '/' + old, new)
            
    def merge_vendors(self, vendors_df):
        pass