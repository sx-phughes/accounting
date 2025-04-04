# Standard packages
from datetime import datetime
import os
import re
import shutil
import pandas as pd
<<<<<<< HEAD
from pynput.keyboard import Key, Listener
=======
>>>>>>> 9325cd371a8bd70a67527f7fe426df02c9ee9e04

# Package imports
from functions import *


class PayablesWorkbook(pd.DataFrame):
    payables_path = 'C:/gdrive/Shared drives/accounting/Payables'
    # Normal Properties
    _metadata = ['wb_path', 'payables_date', 'stem', 'f_name', '_payables_date', '_stem', '_f_name']
    
    def __init__(self, data=None, date=None, index=None, columns=None, dtype=None, copy=None):
        if date:
            self.payables_date = date
            self.stem = self.payables_date

        if data is not None:
            input_data = data
        else:
<<<<<<< HEAD
            input_data = self.initialize_from_date()
=======
            input_data = pd.read_excel(self.wb_path, 'Invoices')[['Vendor', 'Invoice #', 'Amount']]
>>>>>>> 9325cd371a8bd70a67527f7fe426df02c9ee9e04

        super().__init__(input_data, index, columns, dtype, copy)
    
    @property
    def _constructor(self):
        return PayablesWorkbook
    
    @property
    def wb_path(self):
        return PayablesWorkbook.payables_path + self.stem + self.f_name

    @wb_path.setter
    def wb_path(self, wb_path):
        pass 
        
    @property
    def payables_date(self):
        return self._payables_date
    
    @payables_date.setter
    def payables_date(self, date: str|datetime):
        if isinstance(date, str):
            if check_date(date):
                self._payables_date = datetime.strptime(date, '%Y-%m-%d')
            else:
                raise TypeError
        elif isinstance(date, datetime):
            self._payables_date = date
        elif date is None:
            pass
        else:
            raise TypeError

    @property
    def stem(self):
        return self._stem
    
    @property
    def f_name(self):
        return self._f_name
    
    @stem.setter
    def stem(self, date: datetime|str):
        if isinstance(date, datetime):
            year = date.strftime('%Y')
            month = date.strftime('%m')

            self._stem = f'/{year}/{year}{month}/{self.payables_date.strftime('%Y-%m-%d')}'
            self._f_name = f'/{self.payables_date.strftime('%Y-%m-%d')} Payables.xlsx'
        elif isinstance(date, str):
            self._stem = date
            self._f_name = '/' + date.split('/')[-1] + ' Payables.xlsx'
        elif date is None:
            pass
    
    @f_name.setter
    def f_name(self, f_name):
        self._f_name = f_name
<<<<<<< HEAD
    
    def initialize_from_date(self):
        path = self.wb_path.replace(self.f_name, '')
        if not self.check_path(path):
           self.new_workbook()
        
        data = pd.read_excel(self.wb_path, 'Invoices')[['Vendor', 'Invoice #',
                                                       'Amount']]
        return data
        
=======
>>>>>>> 9325cd371a8bd70a67527f7fe426df02c9ee9e04

    def insert_invoice(self, invoice_data: list):
        self.loc[len(self.index)] = invoice_data

        self.move_files(invoice_data[0], invoice_data[1])
        self.save_workbook()
        
    def remove_invoice(self, index):
        self.drop(index=index, inplace=True)
        self.reset_index(drop=True, inplace=True)
        self.save_workbook()
    
<<<<<<< HEAD
    def check_path(self, path):
        if os.path.exists(path):
            return True
        else:
            os.makedirs(path)
            return False 

    def new_workbook(self):
        df = pd.DataFrame(columns=['Vendor', 'Invoice #', 'Amount'])
        with pd.ExcelWriter(self.wb_path, 'xlsxwriter') as writer:
            df.to_excel(writer, 'Invoices', index=False)

=======
>>>>>>> 9325cd371a8bd70a67527f7fe426df02c9ee9e04
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
        new_paths = [PayablesWorkbook.payables_path + self.stem.replace('/' + self.payables_date.strftime('%Y-%m-%d'), '') + '/' + f_name for f_name in new_f_names]
        
        for old, new in zip(files, new_paths):
            shutil.move(downloads + '/' + old, new)
            
    def merge_vendors(self, vendors_df):
        pass
