from cm_exchange_fees.cboe_fees_dl import get_cboe_fees
from cm_exchange_fees.exchange_fees_ssh import get_exchange_fees
from abc import ABC
import os

class ExchangeFeesDownload(ABC):
    def __init__(self, month, year, download_path):
        self.month = month
        self.year = year
        self.download_path = download_path
        
    def main(self):
        os.system('cls')

        get_cboe_fees(self.year, self.month, self.download_path)
        
        os.system('cls')
        
        get_exchange_fees(self.year, self.month, self.download_path)
        
    def not_cboe_files(self):
        os.system('cls')
        
        get_exchange_fees(self.year, self.month, self.download_path)