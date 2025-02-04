import pandas as pd
from datetime import datetime
from abc import ABC

#### BAML Transfer Table ####
class TransferTable(pd.DataFrame, ABC):
    def __init__(self, columns: list[str]):
        super().__init__(columns=columns)
        self.je_total = 0

    def add_row(self, data: list):
        self.loc[len(self)] = data




class BamlTransferTable(TransferTable):
    def __init__(self, transfer_date: str):
        self._headers = [
            'Firm',
            'TOE',
            'Debit_Credit',
            'Symbol',
            'Qty',
            'AMOUNT',
            'ACCOUNT',
            'Settle_Date',
            'TRAILER1',
            'TRAILER2',
            'TRAILER3',
            'Memo_CD',
            'Offset_CD',
            'Expiration_Date',
            'Call_Put',
            'Strike_Price'
        ]

        super().__init__(columns=self._headers)
        self.settle_date = transfer_date
        self.dt_settle_date = datetime.strptime(transfer_date, '%m/%d/%Y')
        self.comment_date_str = datetime(self.dt_settle_date.year, self.dt_settle_date.month - 1, 1).strftime('%b %Y')

    def add_data_row(self, account_no: str, amount: float, user: str = 'KPIE'):
        account_no = account_no.replace('-','')

        dc = 'D' if amount >= 0 else 'C'

        row = [1, 'JE', dc, '', '', abs(amount), account_no, self.settle_date, f'{self.comment_date_str} CLOSE OUT', user, '', '', '', '' , '', '']
        
        self.add_row(row)

        self.je_total += amount
    
    def add_final_row(self, user: str = 'KPIE'):
        dc = 'C' if self.je_total >= 0 else 'D'
        row = [1, 'JE', dc, '', '', round(abs(self.je_total),2), '64499821D9', self.settle_date, f'{self.comment_date_str} CLOSE OUT', user, '', '', '', '' , '', '']
        
        self.add_row(row)


class AbnOptTransferTable(TransferTable):
    def __init__(self, tfr_type: str):
        self._headers = [
            'Code',
            'CA',
            'Firm',
            'Origin',
            'Account',
            'SubAccount',
            'Amount',
            'Placement',
            'CurrencyCode',
            'AsOfDate',
            'Bank',
            'Check',
            'CostCenter',
            'Description'
        ]
        self._offsets = {
            '695': ['695', 'C', '10S'],
            'ET': ['695', 'C', '10S'],
            '813': ['813', '1', 'SICSH']
        }
        super().__init__(self._headers)
        self.type = tfr_type
        
        
    def add_data_row(self, account, amount):
        row = [
            '',
            'A',
            account[0:3],
            account[4:5],
            account[5:],
            '',
            amount * -1,
            '10001',
            'USD',
            '',
            '',
            '',
            '',
            'Transfer'
        ]

        self.add_row(row)
        self.je_total += amount
    
    def add_final_row(self):
        row = [
            '',
            'A',
            self._offsets[self.type][0],
            self._offsets[self.type][1],
            self._offsets[self.type][2],
            '',
            self.je_total,
            '10001',
            'USD',
            '',
            '',
            '',
            '',
            'Transfer'
        ]
        self.add_row(row)

class AbnFutTransferTable(TransferTable):
    def __init__(self):
        self._headers = [
            'Code',
            'Firm',
            'Office',
            'PrimaryAccount',
            'AT',
            'JournalAmount',
            'CC',
            'Description',
            'OffsetOffice',
            'OffsetAccount',
            'Offset_AT',
            'Blank'
        ]
        self._offsets = {
            'SIMP1': 'SICSH',
            'SIMP2': 'SICSH',
            'SIMP7': 'SICSH',
            'SIMP4': 'SIMP6',
            'SIMP3': 'SIMP6'
        }
        super().__init__()

    def add_data_row(self, account, amount):
        row = [
            '',
            'X',
            '',
            account,
            'RU',
            amount * -1,
            '',
            'Journal Transfer',
            '',
            self._offsets[account],
            'RU',
            ''
        ]

        self.add_row(row)