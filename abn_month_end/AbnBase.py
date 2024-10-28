from abc import ABC
from datetime import datetime, timedelta
import pandas as pd

class AbnBase(ABC):
    def __init__(self, close_year, close_month, google_drive_root='C:/gdrive'):
        self.close_year = close_year
        self.close_month = close_month
        self.moyr = self.get_moyr(close_year, close_month)
        self.gdrive_root = google_drive_root
        self.trading_path = self.get_trading_path(close_year, close_month, google_drive_root)
        self.archive_path = self.get_archive_path(google_drive_root)
        
        self.t_minus_year, self.t_minus_month = self.get_t_minus(close_year, close_month)
        self.t_plus_year, self.t_plus_month = self.get_t_plus(close_year, close_month)
        
    def get_moyr(self, year, month):
        return datetime(year, month, 1).strftime('%Y%m')
        
    def get_trading_path(self, year, month, google_drive_root):
        moyr = self.get_moyr(year, month)
        
        trading_root = google_drive_root + f'/Shared drives/accounting/Simplex Trading/{year}/{moyr}/ABN'
        
        return trading_root
    
    def get_archive_path(self, google_drive_root):
        return google_drive_root + '/Shared drives/Clearing Archive/ABN_Archive'
    
    def get_t_minus(self, close_year, close_month):
        t0 = datetime(close_year, close_month, 1)
        td = timedelta(days=20)
        t_minus = t0 - td
        
        return (t_minus.year, t_minus.month)
    
    def get_t_plus(self, close_year, close_month):
        t0 = datetime(close_year, close_month, 28)
        td = timedelta(days=20)
        t_plus = t0 + td
        
        return (t_plus.year, t_plus.month)
    
class AbnFile(AbnBase):
    def __init__(self, date: datetime, google_drive_root):
        super().__init__(date.year, date.month, google_drive_root)
        self.file_day = date.day
        self.file_date = date
        self.date_str = date.strftime('%Y%m%d')
    
    def get_data(self, file_path):
        data = pd.read_csv(file_path)
        
        return data

class EqtCashFile(AbnFile):
    def __init__(self, date: datetime, google_drive_root='C:/gdrive'):
        super().__init__(date, google_drive_root)
        self.name = f'EQTCASH_{self.date_str}.CSV'
        self.path = self.archive_path + f'/{self.date_str}/{self.name}'
        self.data = self.get_data(self.path)
        
class MicsCashFile(AbnFile):
    def __init__(self, date: datetime, google_drive_root='C:/gdrive'):
        super().__init__(date, google_drive_root)
        self.name = f'MICS_Cash_{self.date_str}.csv'
        self.path = self.archive_path + f'/{self.date_str}/{self.name}'
        self.data = self.get_data(self.path)