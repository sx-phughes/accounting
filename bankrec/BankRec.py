import pandas as pd

class BankRec:
    def __init__(self, bank_rec_data):
        self.data = bank_rec_data
        
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, bank_rec_data:pd.DataFrame):
        mask = bank_rec_data['Description'].str.contains('END-OF-DAY INVESTMENT SWEEP - REDEMPTION OF SHARES IN JPMORGAN U.S. GOVERNMENT MONEY MARKET FUND') | bank_rec_data['Description'].str.contains('END-OF-DAY INVESTMENT SWEEP - PURCHASE OF SHARES IN JPMORGAN U.S. GOVERNMENT MONEY MARKET FUND')
        index = bank_rec_data.loc[mask].index
        bank_rec_data = bank_rec_data.drop(index=index)
        
        self._data = bank_rec_data