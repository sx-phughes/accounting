# 4. T+1 cash files
#       a. EQTCASH_yyyymmdd.CSV
#       b. MICS_Cash_20240501.csv

from abc import ABC
from datetime import datetime, timedelta
import calendar, shutil
from AbnMonthEnd import AbnMonthEnd
from patrick_functions.DateFunctions import first_biz_day
from AbnBase import *


class AbnT1Cash(AbnMonthEnd):
    def __init__(self, close_year, close_month):
        super().__init__(close_year, close_month)
        self.close_year = self.year
        self.close_month = self.month
        self.set_t1_dates()
        self.first_biz_day = first_biz_day(self.t1_year, self.t1_month)
        
    def main(self):
        eqt, mics = self.get_cash_files()
        self.copy_files(eqt.path, mics.path)
        
    def set_t1_dates(self):
        t0 = datetime(self.close_year, self.close_month, 1)
        td = timedelta(days=30)
        t1 = t0 + td
        self.t1_year = t1.year
        self.t1_month = t1.month
    
    def get_cash_files(self):
        curr_eqt = EqtCashFile(self.first_biz_day)
        curr_mics = MicsCashFile(self.first_biz_day)
        
        return (curr_eqt, curr_mics)
    
    def copy_files(self, *paths):
        for path in paths:
            shutil.copy(path, self.abn_folder + f'/{self.eqtcash_name}')
        
        
        