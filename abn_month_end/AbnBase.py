from abc import ABC
from datetime import datetime, timedelta
import pandas as pd
from patrick_functions.DateFunctions import last_biz_day


abn_file_types = {
    'eqtcash': 'equities and options cash ledger',
    'micscash': 'futures cash ledger',
    'dpr': 'daily position report',
    'dtr': 'daily trader report',
    'prc': 'position report cash',
    'cash_movement': 'cash movement report - all journal entries posted',
    'csvcash_cl': 'position report cash client level csv',
    'csvcash_ac': 'position report cash account level csv',
    'position': 'full position listing csv',
    'eqtdiv': 'full dividend breakout by account'
}


class AbnBase(ABC):
    def __init__(self, close_year, close_month, google_drive_root='C:/gdrive'):
        self.year = close_year
        self.month = close_month
        self.gdrive_root = google_drive_root
        
        self.t_minus_year, self.t_minus_month = self.get_t_minus(close_year, close_month)
        self.t_plus_year, self.t_plus_month = self.get_t_plus(close_year, close_month)
    
    @property
    def year(self):
        return self._year
    
    @year.setter
    def year(self, year: int):
        self._year = year

    @property
    def month(self):
        return self._month
    
    @month.setter
    def month(self, month: int):
        self._month = month

    @property
    def eom(self):
        return last_biz_day(self.year, self.month)

    @property
    def moyr(self):
        return datetime(self.year, self.month, 1).strftime('%Y%m')

    @property
    def trading_path(self):
        return self.gdrive_root +  f'/Shared drives/accounting/Simplex Trading/{self.year}/ABN'
    
    @property
    def archive_path(self):
        return self.google_drive_root + '/Shared drives/Clearing Archive/ABN_Archive'
    
    @property
    def t_minus(self):
        t0 = datetime(self.year, self.month, 1)
        td = timedelta(days=20)
        t_minus = t0 - td
        t_minus_eom = t_minus + timedelta(days=(last_biz_day(t_minus.year, t_minus.month) - t_minus.day))
        
        return t_minus_eom
    
    @property
    def t_plus(self):
        t0 = datetime(self.year, self.month, 28)
        td = timedelta(days=20)
        t_plus = t0 + td
        t_plus_eom = t_plus + timedelta(days=(last_biz_day(t_plus.year, t_plus.month).day - t_plus.day))
        
        return t_plus_eom
    
class AbnFile(AbnBase):
    def __init__(self, date: datetime, google_drive_root=''):
        super().__init__(date.year, date.month, None if not google_drive_root else google_drive_root)
        self.file_day = date.day
        self.file_date = date

    @property
    def date(self):
        return self._date
    
    @date.setter
    def date(self, date: datetime):
        self._date = date
    
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