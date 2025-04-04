import os, re, zipfile
from datetime import datetime
import pandas as pd

class FileFinder:
    '''
    Class to find broker invoice excel files.\n
    Initialize with year and month of broker invoices (month received) needed; e.g., Broker invoices covering
    activity in October 2024 would use inputs of 2024, 11.\n
    Main method is .find_files()
    '''
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.yrmo = datetime(year, month, 1).strftime('%Y%m')
        self.search_dir = f'C:/gdrive/Shared drives/accounting/payables/{year}/{self.yrmo}/Broker Invoices'
        self.find_files()
        
    def find_files(self):
        '''
        Finds files in folder given upon initialization. Returns none, puts file paths to excel files in a tabular
        format with cols ['Broker Code', 'Broker Name', 'File Tag']\n
        \tBroker Code corresponds to the IDB Rec code\n
        \tBroker Name is the full broker name\n
        \tFile Tag is the tag for the broker used when saving the invoice files.\n
        Returns nothing, adds new column to the IDB table with path to the invoice data.
        '''
        # Separate file names from the full path
        f_list = [i.split('/')[-1] for i in os.listdir(self.search_dir)]
        
        # Filter for excel, xls and csv files
        f_list = list(filter(lambda x: re.search(r'.xlsx|.xls|.csv', x, re.IGNORECASE), f_list))
        
        # Read in the IDB mapping
        idb_mapping = pd.read_csv('C:/gdrive/Shared drives/accounting/patrick_data_files/idb_rec/idb_code_mapping.csv')
        
        # Add blank column for file name
        idb_mapping['File Name'] = ''
        
        # Iterate through rows of the IDB table
        for i, row in idb_mapping.iterrows():
            
            # If the file name is blank, search for a file matching the tag in the file list; else continue
            if row['File Name'] == '':
                
                for file in f_list:
                    
                    # If the file tag has a parens, escape it
                    if '(' in row['File Tag'] or ')' in row['File Tag']:
                        file_tag = str(row['File Tag']).replace('(',r'\(')
                        file_tag = file_tag.replace(')',r'\)')
                    else:
                        file_tag = row['File Tag']
                        
                    # Search the file tag for a match
                    search = re.search(file_tag, file, re.IGNORECASE)
                    
                    # If a match is found, save it to the IDB file; else, continue to next file name
                    if search:
                        # Debug
                        # print(search.string)
                        idb_mapping.loc[idb_mapping['Broker Name'] == row['Broker Name'], 'File Name'] = search.string
                        break
                    else:
                        continue
            else:
                continue
        
        self.idb_mapping = idb_mapping
        
    def full_paths_list(self) -> list[str]:
        '''
        Returns a list of file paths for each found broker file
        '''
        # Create a list of the full paths from C: to the file, not including blanks
        full_paths_list = [self.search_dir + '/' + file for file in self.idb_mapping['File Name'] if file != '']
        return full_paths_list
    
    def get_sheet_names(self, path: str):
        try:
            f = pd.ExcelFile(path, engine='openpyxl')
            sheets = f.sheet_names
            return sheets
        except zipfile.BadZipFile:
            self.is_not_excel_file(path)
            
    def is_not_excel_file(self, path: str):
        f_name_ext = path.split('/')[-1]
        f_name, ext = '.'.join(f_name_ext.split('.')[:-1]), f_name_ext.split('.')[-1]
        
                