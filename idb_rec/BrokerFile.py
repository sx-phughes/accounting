# IDB Rec Base

import pandas as pd
import re
from find_col_name_row import find_col_name_row
from drop_bottom_rows import drop_bottom_rows

class BrokerFile:
    def __init__(self, broker_file: pd.DataFrame):
        self.broker_file = broker_file
        
    @property
    def broker_file(self):
        return self._broker_file
    
    @broker_file.setter
    def broker_file(self, broker_file:pd.DataFrame):
        # Get row with column names
        cols_index = find_col_name_row(broker_file)
        
        # Get column names and rename to proper headers
        main_row = list(broker_file.iloc[cols_index])
        supp_row = list(broker_file.iloc[cols_index-1])
        row = [supp + main if type(supp) == str else main for supp, main in zip(supp_row, main_row)]
        renamer = {old: new for old, new in zip(list(broker_file.columns.values), row)}
        broker_file = broker_file.rename(columns=renamer)

        # Drop top junk rows
        broker_file = broker_file.drop(index=range(cols_index + 1))
        broker_file = broker_file.reset_index(drop=True)
        
        # Drop bottom junk rows
        stop = drop_bottom_rows(broker_file)
        broker_file = broker_file.drop(index=range(stop, len(broker_file.index)))
        broker_file = broker_file.reset_index(drop=True)
        
        self._broker_file = broker_file
        
    def comp_df(self):
        return self.clean_data(self.broker_file)
        
    def clean_data(self, broker_file: pd.DataFrame):
        # Create dict of patterns to look for
        cols_dict = {
            'date': r'\d{1,2}[/-.]?\d{1,2}[/-.]?\d{2,4}',
            'underlying': r'[A-Z]{1,4}',
            'comms': r'(\d{1,5}).\d{0,2}'
        }
        
        # Create clean dataframe
        clean_df = pd.DataFrame()
        
        # Find cols with needed data and add to clean dataframe
        columns = list(broker_file.columns.values)
        for col_str in cols_dict.keys():
            # Debug
            print(f'col_str = {col_str}')
            print(f'pattern = {cols_dict[col_str]}')
            match_str = self.find_col(broker_file, columns, cols_dict[col_str])
            if match_str:
                clean_df[col_str] = broker_file[match_str]
                
        return clean_df
            
        
    def find_col(self, broker_file: pd.DataFrame, columns: list, pattern: str):
        first_row = list(broker_file.iloc[0])
        
        for i in columns:
            search = re.search(pattern, i, re.IGNORECASE)
            if search:
                search_str = search.string
            else:
                continue
            
            