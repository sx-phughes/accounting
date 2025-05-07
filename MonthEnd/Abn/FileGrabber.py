import pandas as pd
from zipfile import ZipFile
from MonthEnd.Abn.Abn import get_trading_path, get_archive_path, cm_moyr
from patrick_functions.DateFunctions import last_biz_day


def get_data(year: int, month: int):
    date_str = last_biz_day(year, month).strftime('%Y%m%d')
    csvcash_zip_path, position_zip_path = get_file_dirs(date_str)
            
    csvcash = extract_file(csvcash_zip_path)
    position = extract_file(position_zip_path)

    return (pd.read_csv(csvcash, low_memory=False), pd.read_csv(position, low_memory=False))

def get_file_dirs(date_str: str):
    csvcash_name = f'{date_str}-2518-C2518-CSVCASH_AC.csv.zip'
    position_name = f'{date_str}-2518-C2518-POSITION.csv.zip'
    
    csvcash_zip = get_archive_path() + f'/{date_str}/{csvcash_name}'
    position_zip = get_archive_path() + f'/{date_str}/{position_name}'

    return (csvcash_zip, position_zip)

def extract_file(path: str) -> str:
    csv_file_name = path.split('/')[-1].replace('.zip', '')
    dest = get_trading_path + '/' + cm_moyr
    unzip(path, csv_file_name, dest)
    
    return '/'.join([dest, csv_file_name])
    
def unzip(zip_path: str, file_name: str, dest: str) -> None:
    with ZipFile(zip_path, 'r') as zip:
        zip.extract(file_name, dest)