import pandas as pd
import os, re
from datetime import datetime
from abc import ABC

class CreditCardData(ABC):
    def __init__(self):
        self.data = self.get_data()
        # self.data['Transaction Date'] = pd.to_datetime(self.data['Transaction Date'])
        self.save_path = 'C:/Users/phughes_simplextradi/Desktop'
    
    def set_save_path(self, save_path: str):
        try:
            os.listdir(save_path)
        except FileNotFoundError:
            print('This path does not exist. No changes have been made')
        else:
            self.save_path = save_path
        
    def save_data(self, data: pd.DataFrame):
        now = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        full_path = self.save_path + '/search_results_{now}.xlsx'.format(now=now)
        
        with pd.ExcelWriter(full_path) as writer:
            data.to_excel(writer, 'Search Data', index=False)
    
    def search_by_description(self, search_term: str):
        results = self.data[self.data['Description'].str.contains(search_term, na=False, flags=re.IGNORECASE)]
        results = results.copy()
        results = results.reset_index(drop=True)
        
        self.search_results = results
        
    def search_by_memo(self, memo: str):
        results = self.data[self.data['Memo'].str.contains(memo, na=False, flags=re.IGNORECASE)]
        results = results.copy()
        results = results.reset_index(drop=True)

        self.search_results = results
        
    def search_by_date(self, min_date, max_date):
        min_date = datetime.strptime(min_date, '%m/%d/%Y')
        max_date = datetime.strptime(max_date, '%m/%d/%Y')
        
        if min_date and max_date:
            results = self.data[(self.data['Transaction Date'].dt.date > min_date) & (self.data['Transaction Date'].dt.date < max_date)]
        elif min_date and not max_date:
            results = self.data[self.data['Transaction Date'].dt.date > min_date]
        elif max_date and not min_date:
            results = self.data[self.data['Transaction Date'].dt.date < max_date]
        
        results = results.copy()
        results = results.reset_index(drop=True)
        
        self.search_results = results
    
    def get_data(self):
        years = ['2020', '2021', '2022', '2023', '2024']
        months = [str(i) for i in range(1,13)]

        for i in range(len(months)):
            if len(months[i]) == 1:
                months[i] = '0' + months[i]
                
        yearmonths = []

        sheets_by_month = {}

        workbook_names = {'Period': [],
                        'Path': [],
                        'Filename': [],
                        'Detail Sheet': []}

        for i in years:
            for j in months:
                yearmonth = i + j
                
                path1 = f'C:/gdrive/Shared drives/accounting/Simplex Investments/{i}/{yearmonth}/Credit Card'
                path2 = f'C:/gdrive/Shared drives/accounting/Simplex Investments/{i}/{yearmonth}'
                path3 = f'C:/gdrive/Shared drives/accounting/Simplex Investments/{i}/{yearmonth}/Misc'
                path4 = f'C:/gdrive/Shared drives/accounting/Simplex Investments/{i}'
                path5 = f'C:/gdrive/Shared drives/accounting/Simplex Investments/{i}/Credit Card Recs'
                
                f_pattern = fr'{yearmonth} - Chase CC Reconciliation'
                
                paths_to_try = [path1, path2, path3, path4, path5]
                
                for path in paths_to_try:
                    try:
                        files = os.listdir(path)
                    except FileNotFoundError:
                        continue
                    
                    for file in files:
                        match = re.search(f_pattern, file)
                        if match: 
                            #CC Rec file found
                            
                            if yearmonth in workbook_names['Period']:
                                # Comparing modified times - if the current file is older, continue; if newer, replace old file
                                curr_full_path = path + '/' + match.string
                                curr_file_mod_t = os.path.getmtime(curr_full_path)
                                
                                old_index = workbook_names['Period'].index(yearmonth)
                                old_file = workbook_names['Path'][old_index] + '/' + workbook_names['Filename'][old_index]
                                old_file_mod_t = os.path.getmtime(old_file)
                                
                                if curr_file_mod_t > old_file_mod_t:
                                    workbook_names['Filename'][old_index] = match.string
                                    workbook_names['Path'][old_index] = path
                            
                            else:
                                workbook_names['Period'].append(yearmonth)
                                workbook_names['Path'].append(path)
                                workbook_names['Filename'].append(match.string)
                        else:
                            continue

        for i in range(len(workbook_names['Period'])):
            full_path = workbook_names['Path'][i] + '/' + workbook_names['Filename'][i]
            workbook = pd.ExcelFile(full_path)
            sheets = workbook.sheet_names
            for j in sheets:
                sheet_match = re.search('Detail', j)
                if sheet_match:
                    try: 
                        workbook_names['Detail Sheet'][i]
                    except IndexError:
                        workbook_names['Detail Sheet'].append(sheet_match.string)

        full_details_table = pd.DataFrame()

        for i in range(len(workbook_names['Period'])):
            full_path = workbook_names['Path'][i] + '/' + workbook_names['Filename'][i]
            sheet_name = workbook_names['Detail Sheet'][i]
            
            curr_data = pd.read_excel(full_path, sheet_name)
            cols = curr_data.columns
            
            try:
                curr_data = curr_data[['Transaction Date', 'Description', 'Category', 'Amount', 'Memo']]
            except KeyError:
                curr_data = curr_data[['Transaction Date', 'Description', 'Category', 'Amount']]
                curr_data['Memo'] = ''
            finally:
                full_details_table = pd.concat([full_details_table, curr_data])
                full_details_table = full_details_table.reset_index(drop=True)
    
        return full_details_table