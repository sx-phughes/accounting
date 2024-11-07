import pandas as pd

def get_sheet_names(path: str):
    f = pd.ExcelFile(path)
    sheets = f.sheet_names
    
    return sheets
    