import pandas as pd
from datetime import datetime

class TransferTable(pd.DataFrame):
    def __init__(self, col_names: list[str]):
        super().__init__(columns=col_names)
        # self.columns = col_names
        self.je_total = 0

    def add_row(self, data: list):
        self.loc[len(self)] = data

class BamlTransferTable(TransferTable):
    cols = [
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
    
    def __init__(self, transfer_date: str):

        super().__init__(col_names=BamlTransferTable.cols)
        self.settle_date = transfer_date

    @property
    def settle_date(self):
        return self._settle_date
    
    @settle_date.setter
    def settle_date(self, date):
        self._settle_date = date
        self.dt_settle_date = datetime.strptime(date, '%m/%d/%Y')
        self.comment_date_str = datetime(
            self.dt_settle_date.year,
            self.dt_settle_date.month,
            1
        ).strftime('%b %Y')
    
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
    headers = [
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
    
    offsets = {
            '695': ['695', 'C', '10S'],
            'ET': ['695', 'C', '10S'],
            '813': ['813', '1', 'SICSH']
        }
    
    def __init__(self, tfr_type: str):
        super().__init__(AbnOptTransferTable.headers)
        self.type = tfr_type
        
    def add_data_row(self, account, amount, flip=True):
        if flip:
            new_amount = amount * -1
            self.je_total += amount
        else:
            new_amount = amount
            self.je_total -= amount
            
        row = [
            '',
            'A',
            str(account[0:3]),
            account[3:4],
            account[4:],
            '',
            new_amount,
            '10001',
            'USD',
            '',
            '',
            '',
            '',
            'Transfer'
        ]

        self.add_row(row)
    
    def add_final_row(self):
        row = [
            '',
            'A',
            AbnOptTransferTable.offsets[self.type][0],
            AbnOptTransferTable.offsets[self.type][1],
            AbnOptTransferTable.offsets[self.type][2],
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
    headers = [
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
    
    offsets = {
            'SIMP1': 'SICSH',
            'SIMP2': 'SICSH',
            'SIMP7': 'SICSH',
            'SIMP4': 'SIMP6',
            'SIMP3': 'SIMP6',
            'SIMP9': 'SIMP6'
        }
    
    def __init__(self):
        super().__init__(col_names=AbnFutTransferTable.headers)

    def add_data_row(self, account: str, amount: float):
        
        short_account = account[4:]
        
        row = [
            '',
            'X',
            '',
            short_account,
            'RU',
            amount * -1,
            '',
            'Journal Transfer',
            '',
            self.offsets[short_account],
            'RU',
            ''
        ]

        self.add_row(row)