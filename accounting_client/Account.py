"""Module for housing account-related classes and functions
"""
# Standard imports
import re
import pandas as pd

segt1_vals = {
    'TRD': 'trading',
    'TEC': 'technologies',
    'INV': 'investments',
    'HOL': 'holdings',
    'SAL': 'salazar'
}

seg2_vals = {
    1: 'asset',
    2: 'liability',
    3: 'equity',
    4: 'revenue',
    5: 'expense',
    6: 'expense',
    7: 'expense',
    8: 'revenue'
}

seg2_positive = {
    1: 'debit',
    2: 'credit',
    3: 'debit',
    4: 'credit',
    5: 'debit',
    6: 'debit',
    7: 'debit',
    8: 'credit'
}

def keys(seg_dict: dict):
    return list(seg_dict.keys())


class Account:
    """Base class for account structure"""
    
    _active_accounts = {}
    _account_groups = {}
    
    _pattern = r'([A-Z]{3})-(\d)-(\d{4})-([A-Z]{2})?-([\dA-Z]{3})?'

    def __init__(
        self,
        seg1: str = None,
        seg2: str = None,
        seg3: str = None,
        seg4: str = None,
        seg5: str = None,
        full_acct: str = None,
        category: str = None,
        admin: bool = False
    ):
        if not admin:
            if isinstance(full_acct, str) and self._validate(full_acct):
                temp_segments = full_acct.split('-')
            elif self._validate([seg1, seg2, seg3, seg4, seg5]):
                temp_segments = [seg1, seg2, seg3, seg4, seg5]
            else:
                raise AttributeError('Account does not match pattern')
            
            temp_segments[1] = int(temp_segments[1])
            temp_segments[2] = int(temp_segments[2])
            
            self._segments = temp_segments
            self._category = category

            Account._active_accounts.update({self.full_account: self})
            self.add_to_group()
        else:
            pass

    def __getitem__(self, account_no: str):
        return self._active_accounts[account_no]

    def __setitem__(self, account_no: str, account):
        self._active_accounts[account_no] = account
        self.add_to_group(account)
    
    def __repr__(self):
        return self.full_account
    
    def _validate(self, input):
        if isinstance(input, str):
            tester = input
        else:
            tester = '-'.join(input)
            
        if re.match(Account._pattern, tester):
            return True
        else:
            raise TypeError('Segments do not conform to pattern' + Account.pattern)
        
    @property
    def full_account(self):
        return '-'.join([self.convert_seg_to_str(self._segments[i], i+1) for i in range(len(self._segments))])
    
    def convert_seg_to_str(self, seg, seg_num=None):
        if isinstance(seg, str):
            return seg
        else:
            seg_lens = {2: 1, 3: 4}
            str_seg = str(seg)
        
            return str(seg) + '0' * (seg_lens[seg_num] - len(str_seg))
    
    def add_to_group(self, acct=None):
        use_var = self if acct is None else acct

        try:
            Account._account_groups[use_var._category].append(use_var.full_account)
        except KeyError:
            Account._account_groups.update({use_var._category: [use_var.full_account]})

   
def is_balance_sheet(account: Account):
    """for determining which statement account goes to"""
    if account._segments[1] < 4:
        return True
    else:
        return False
    
def load_accounts(path: str):
    account_table = pd.read_csv(path)
    account_i = 0
    category_i = 7

    for i in range(len(account_table.index)):
        full_acct = account_table['account'].iloc[i]
        category = account_table['category'].iloc[i]
        acct_obj = Account(full_acct=full_acct, category=category)

mgr = Account(admin=True)
