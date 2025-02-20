import pandas as pd
from BrokerFile import BrokerFile
from get_sheet_names import get_sheet_names
from FileFinder import FileFinder

def test_broker_file(paths):

    for path in paths:
        print(path)
        sheets = get_sheet_names(path)
        
        if sheets[0] == 'Summary':
            sheets.pop(0)
            use_sheet = sheets[0]
        # elif 'IDB' in sheets:
        #     use_sheet = sheets[sheets.index('IDB')]
        else:
            use_sheet = sheets[0]

        df = pd.read_excel(path, use_sheet)

        file = BrokerFile(broker_file=df)

        clean_file = file.comp_df()

        print(clean_file)
        
        input()
        
def test_filefinder():
    finder = FileFinder(2024, 10)
    files = finder.find_files()
    full_paths = finder.full_paths_list()
    
    return full_paths
    
paths = test_filefinder()

test_broker_file(paths)