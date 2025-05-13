import pandas as pd
from zipfile import ZipFile
from MonthEnd.Abn import Base, EoyCashFile, FileGrabber
from patrick_functions.DateFunctions import last_biz_day

csvcash_name = '-2518-C2518-CSVCASH_AC.csv.zip'
position_name = '-2518-C2518-POSITION.csv.zip'

def get_cash_file(year: int, month: int):
    return get_file(year, month, csvcash_name)

def get_position_file(year: int, month: int):
    return get_file(year, month, position_name)

def get_file(year: int, month: int, file_pattern: str):
    date_str = last_biz_day(year, month).strftime('%Y%m%d')
    zip_file_path = get_file_dir(date_str, file_pattern)

    extracted_path = extract_file(zip_file_path)
    return pd.read_csv(extracted_path, low_memory=False)

def get_file_dir(date_str: str, pattern: str):
    file_name = date_str + pattern
    zip_path = Base.get_archive_path() + f'/{date_str}/{file_name}'

    return zip_path

def extract_file(path: str) -> str:
    csv_file_name = path.split('/')[-1].replace('.zip', '')
    dest = Base.get_trading_path + '/' + Base.cm_moyr
    unzip(path, csv_file_name, dest)
    
    return '/'.join([dest, csv_file_name])
    
def unzip(zip_path: str, file_name: str, dest: str) -> None:
    with ZipFile(zip_path, 'r') as zip:
        zip.extract(file_name, dest)

def get_global_files():
    global cm_cash, cm_position, pm_cash, pm_position
    cm_cash = get_cash_file(Base.year, Base.month)
    cm_position = get_position_file(Base.year, Base.month)
    pm_cash = FileGrabber.get_cash_file(Base.t_minus.year, Base.t_minus.month)
    pm_position = FileGrabber.get_position_file(
        Base.t_minus.year,
        Base.t_minus.month
    )

    if Base.t_minus.month == 12:
        pm_cash = EoyCashFile.convert_to_eoy_cash(Base.year - 1, pm_cash)