import pandas as pd
from BrokerFile import BrokerFile
from FileFinder import FileFinder
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

def test_filefinder():
    finder = FileFinder(2024, 10)
    
    full_paths = finder.full_paths_list()
    
    return full_paths

def test_broker_file(paths):

    for path in paths:
        # if 'Canaccord' not in path:
            # continue
        
        print(f'Path:\t{path}')
        
        sheets = FileFinder.get_sheet_names(path)
        
        if sheets[0] == 'Summary':
            sheets.pop(0)
            use_sheet = sheets[0]
        else:
            use_sheet = sheets[0]
        
        file = BrokerFile(path, use_sheet)
        
        print(file)

        # clean_file = file.comp_df()

        # print(clean_file)
        
        input()
        

paths = test_filefinder()

test_broker_file(paths)