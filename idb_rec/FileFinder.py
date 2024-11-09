import os, re
from datetime import datetime
import pandas as pd

class FileFinder:
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.yrmo = datetime(year, month, 1).strftime('%Y%m')
        self.search_dir = f'C:/gdrive/Shared drives/accounting/payables/{year}/{self.yrmo}/Broker Invoices'
        
    def find_files(self):
        f_list = [i.split('/')[-1] for i in os.listdir(self.search_dir)]
        
        f_list = list(filter(lambda x: re.search(r'.xlsx|.xls|.csv', x, re.IGNORECASE), f_list))
        
        idb_mapping = pd.read_csv('C:/gdrive/Shared drives/accounting/patrick_data_files/idb_rec/idb_code_mapping.csv')
        
        idb_mapping['File Name'] = ''
        
        for i, row in idb_mapping.iterrows():
            if row['File Name'] == '':
                for file in f_list:
                    if '(' in row['File Tag'] or ')' in row['File Tag']:
                        file_tag = row['File Tag'].replace('(','\(')
                        file_tag = file_tag.replace(')', '\)')
                    else:
                        file_tag = row['File Tag']
                        
                    
                    search = re.search(file_tag, file, re.IGNORECASE)
                    
                    if search:
                        print(search.string)
                        idb_mapping.loc[idb_mapping['Broker Name'] == row['Broker Name'], 'File Name'] = search.string
                        break
                    else:
                        continue
            else:
                continue
        
        self.idb_mapping = idb_mapping
        
    def full_paths_list(self):
        full_paths_list = [self.search_dir + '/' + file for file in self.idb_mapping['File Name'] if file != '']
        return full_paths_list