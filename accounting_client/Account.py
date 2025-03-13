"""Module for housing account-related classes and functions
"""
# Standard imports
import re
import numpy as np

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
    
    active_accounts = []
    
    pattern = r'([A-Z]{3})-(\d)-(\d{4})-([A-Z]{2})?-([\dA-Z]{3})?'
    def __init__(
        self,
        seg1: str = None,
        seg2: str = None,
        seg3: str = None,
        seg4: str = None,
        seg5: str = None,
        full_acct: str = None
    ):
        
        if isinstance(full_acct, str) and self._validate(full_acct):
            temp_segments = full_acct.split('-')
        elif self._validate([seg1, seg2, seg3, seg4, seg5]):
            temp_segments = [seg1, seg2, seg3, seg4, seg5]
        else:
            raise AttributeError('Account does not match pattern')
        
        temp_segments[1] = int(temp_segments[1])
        temp_segments[2] = int(temp_segments[2])
        
        self._segments = temp_segments
        
    
    def __repr__(self):
        return self.full_account
    
    def _validate(self, input):
        if isinstance(input, str):
            tester = input
        else:
            tester = '-'.join(input)
            
        if re.match(Account.pattern, tester):
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
        
        