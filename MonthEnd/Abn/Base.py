from datetime import datetime, timedelta
from patrick_functions.DateFunctions import last_biz_day
import pandas as pd

def set_globals(data_year: int, data_month: int, gdrive: str) -> None:
    global year, month, gdrive_root, t_minus, t_plus, save_to
    year = data_year
    month = data_month
    gdrive_root = gdrive
    t_minus = get_t_minus()
    t_plus = get_t_plus()
    save_to = f'{get_trading_path()}/{get_moyr()}'
    
    global cm_moyr, pm_moyr
    cm_moyr = get_moyr()
    pm_moyr = t_minus.strftime('%Y%m')

    get_mapping_files()

    global patrick_data_files
    patrick_data_files = "C:/gdrive/Shared drives/accounting/patrick_data_files"


def get_t_minus() -> datetime:
    t0 = datetime(year, month, 1)
    td = timedelta(days=20)
    t_minus = t0 - td
    t_minus_eom = t_minus + timedelta(days=(last_biz_day(t_minus.year, t_minus.month).day - t_minus.day))
    
    return t_minus_eom

def get_t_plus() -> datetime:
    t0 = datetime(year, month, 28)
    td = timedelta(days=20)
    t_plus = t0 + td
    t_plus_eom = t_plus + timedelta(days=(last_biz_day(t_plus.year, t_plus.month).day - t_plus.day))
    
    return t_plus_eom

def get_trading_path() -> str:
    return gdrive_root +  f'/Shared drives/accounting/Simplex Trading/{year}/ABN'

def get_archive_path() -> str:
    return gdrive_root + '/Shared drives/Clearing Archive/ABN_Archive'

def get_moyr():
    return datetime(year, month, 1).strftime('%Y%m')

def get_mapping_files(google_drive_root='C:/gdrive') -> tuple[pd.DataFrame, pd.DataFrame]:
    abn_files_path = google_drive_root + '/Shared drives/accounting/patrick_data_files/abn_month_end'
    global ledger_mapping, account_mapping
    ledger_mapping = pd.read_csv(abn_files_path + '/ABN_ledger_mapping.csv')
    account_mapping = pd.read_csv(abn_files_path + '/ABN_account_mapping.csv')

def get_archive_date_path(day=0):
    if day == 0:
        date_str = last_biz_day(year, month).strftime('%Y%m%d')
    else:
        date_str = datetime(year, month, day).strftime('%Y%m%d')

    dir_path = get_archive_path + '/' + date_str

    return dir_path