"""Reporting Module Base Classes"""

# Standard imports
from datetime import datetime
from abc import ABC, abstractmethod

# Package imports
import Account
import Ledger

class Report(ABC):
    def __init__(
            self,
            date1: datetime,
            date2: datetime,
            accounts: list[str],
            gl: Ledger,
            title: str = None):
        self._start = date1,
        self._end = date2
        self._title = title
        self.use_accounts = accounts
    
    @abstractmethod
    @property
    def use_accounts(self):
        return self._use_accounts
    
    @abstractmethod
    @use_accounts.setter
    def use_accounts(self, accounts: list, balance_sheet: bool):
        acct_list = []
        for acct in accounts:
            name = acct
            obj = Account.mgr[name]
            if Account.is_balance_sheet(obj) == balance_sheet:
                acct_list.append(obj)
            else:
                continue
        self._use_accounts = acct_list
    
    
class BalanceSheet(Report):
    def __init__(self, as_of_date: datetime, accounts: list[str], gl: Ledger):
        title = ''.join(
            'Balance Sheet as of ',
            as_of_date.strftime('%Y-%m-%d')
        )
        super().__init__(date1=None, date2=as_of_date, title=title)
        self.use_accounts = accounts
    
    @property
    def use_accounts(self):
        return super()._use_accounts
    
    @use_accounts.setter
    def use_accounts(self, accounts: list):
        super().use_accounts(accounts, balance_sheet=True)