import re
from datetime import datetime
import pandas as pd

class WireField():
    def __init__(self, field_name, field_len:int, field_value):
        self.name = field_name
        self.len = field_len
        self.val = field_value

    @property
    def val(self):
        return self._val
    
    @val.setter
    def val(self, field_value):
        if self.len == 0:
            field_value = ''
        elif len(field_value) > self.len:
            field_value = field_value[0:self.len]
        else:
            field_value = field_value
        
        if ',' in field_value:
            field_value = '"' + field_value + '"'
        
        self._val = field_value

class Vendor:
    vendor_info = pd.read_csv('C:/gdrive/My Drive/code_projects/payables2/vendors.csv')
    def __init__(self, vendor):
        self.vendor = vendor
        self.get_vendor_info(vendor)
    
    def get_vendor_info(self, vendor):
        vendor_row = Vendor.vendor_info.loc[Vendor.vendor_info['Vendor'] == vendor]
        self.account = vendor_row['Bank Account Number'].values[0]
        self.bank_id_type = vendor_row['ID Type'].values[0]
        self.bank_id = vendor_row['ID Value'].values[0]
        self.bank_country = vendor_row['Bank Country'].values[0]
        self.intermediary_id_type = vendor_row['Intermediary ID Type'].values[0]
        self.intermediary_id_value = vendor_row['Intermediary ID Value'].values[0]
        
        
    
class WirePayment:
    def __init__(self, orig_bank_id, orig_account, amount, value_date: datetime, vendor: Vendor):
        self.orig_bank_id = orig_bank_id
        self.orig_account = orig_account
        self.amount = amount
        self.value_date = value_date
        self.vendor = vendor

        self.input_type = 'P'
        self.method = 'WIRE'
        self.bank_to_bank_transfer = 'N'
        self.currency = 'USD'
        
        
        
    @property
    def orig_bank_id(self):
        return self._orig_bank_id
    
    @orig_bank_id.setter
    def orig_bank_id(self, bank_id):
        if re.match('\d{9}', bank_id):
            self._orig_bank_id = bank_id
        else:
            raise TypeError
    
    @property
    def orig_account(self):
        return self._orig_account
    
    @orig_account.setter
    def orig_account(self, bank_account):
        if re.match('[\d- ]{6,}', bank_account):
            self._orig_account = bank_account
        else:
            raise TypeError
        
    @property
    def amount(self):
        return self._amount
    
    @amount.setter
    def amount(self, amount: float):
        if re.match(r'\d+.\d{2}', amount):
            self._amount = amount
        elif re.match(r'\d+.\d{3,}', amount):
            self._amount = round(amount, 2)
        else:
            raise TypeError
    
    @property
    def value_date(self):
        return self._value_date
    
    @value_date.setter
    def value_date(self, value_date: datetime):
        self._value_date = value_date.strftime('%Y%m%d')