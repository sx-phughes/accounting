from cm_exchange_fees.cboe_fees_dl import get_cboe_fees
from cm_exchange_fees.exchange_fees_ssh import get_exchange_fees
import os

class ExchangeFeesDownload:
    def __init__(self, month, year, download_path):
        self.month = month
        self.year = year
        self.download_path = download_path
        
    def cboe_files(self, un, pw):
        os.system('cls')

        get_cboe_fees(self.year, self.month, self.download_path, un, pw)
        
    def other_exchange_files(self, un, pw):
        os.system('cls')
        
        get_exchange_fees(self.year, self.month, self.download_path, un, pw)