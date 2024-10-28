from patrick_functions.DateFunctions import last_biz_day
from zipfile import ZipFile
import pandas as pd
from AbnBase import *

## Files Needed ##
#   1. yyyymmdd-2518-C2518-CSVCASH_AC.csv.zip
#   2. yyyymmdd-2518-C2518-POSITION.csv.zip

class AbnFileGrabber(AbnBase):
    def __init__(self, year, month):
        super().__init__(year, month)
        
        self.last_biz_day = last_biz_day(year, month)
        self.moyr = self.last_biz_day.strftime('%Y%m')
        self.date_str = self.last_biz_day.strftime('%Y%m%d')
        
    def main(self):
        self.get_file_dirs()
        self.unzip()
        
        return (pd.read_csv(self.csvcash, low_memory=False), pd.read_csv(self.position, low_memory=False))
    
    def get_file_dirs(self):
        self.csvcash_name = f'{self.date_str}-2518-C2518-CSVCASH_AC.csv.zip'
        self.position_name = f'{self.date_str}-2518-C2518-POSITION.csv.zip'
        
        self.csvcash_zip = self.archive_path + f'/{self.date_str}/{self.csvcash_name}'
        self.position_zip = self.archive_path + f'/{self.date_str}/{self.position_name}'

    def unzip(self):
        paths_list = [[self.csvcash_zip, self.csvcash_zip.split('/')[-1].replace('.zip', ''), self.trading_path],
                      [self.position_zip, self.position_zip.split('/')[-1].replace('.zip', ''), self.trading_path]]
        
        
        for i in paths_list:
            with ZipFile(i[0], 'r') as zip:
                zip.extract(i[1], i[2])
                
        self.csvcash = paths_list[0][2] + '/' + paths_list[0][1]
        self.position = paths_list[1][2] + '/' + paths_list[1][1]