# Standard Imports
import pandas as pd
import numpy as np
from datetime import datetime

# Package Imports
from Entry import Entry
import Account


@pd.api.extensions.register_dataframe_accessor("gl")
class LedgerAccessor:
    """Custom gl-related accessors for dataframe"""
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj
        
    @staticmethod
    def _validate(obj):
        if 'debit' not in obj.columns or 'credit' not in obj.columns:
            raise AttributeError('Must have \'debit\' and \'credit\'')
        
    @property
    def debits(self):
        debits = self._obj.debit.sum()
        return debits
    
    @property
    def credits(self):
        credits = self._obj.credit.sum()
        return credits


def load_ledger(path):
    df = pd.read_csv(path)
    gl = Ledger(df)
    gl.set_entry_id()
    return gl


class Ledger(pd.DataFrame):
    """Class for general ledger object based on pandas DataFrame"""

    cols = ['id', 'date', 'account', 'debit', 'credit', 'description', 'vendor', 'post_date']

    @property
    def _constructor(self):
        return Ledger
    
    @property
    def _constructor_sliced(self):
        return pd.Series
    
    def add_entry(self, entry: Entry):
        """Method to add a journal entry to the general ledger.
        
        Method creates a dictionary-format of the data in the journal entry
        and converts to a DataFrame, which is then appended to the end of the 
        general ledger.
        
        Returns: Ledger object with new JE added
        
        """
        if entry.validate_entry():
            data = {col_name: [] for col_name in Ledger.cols}
            
            for line in entry._lines:
                data['id'].append(entry._id)
                data['date'].append(entry._date)
                data['account'].append(line._account)
                
                if isinstance(line._debit, np.float64):
                    data['debit'].append(line._debit)
                    data['credit'].append(np.float64(0))
                else:
                    data['debit'].append(np.float64(0))
                    data['credit'].append(line._credit)
                
                data['description'].append(line._desc)
                data['vendor'].append(line._vendor)
                
                data['post_date'].append(datetime.now())
            
            entry_df = pd.DataFrame(data)
            print('\n\nLedger: add_entry() line 85: printing entry df')
            print(entry_df)
            entry_index = pd.Index(range(len(self.index), len(self.index) + len(entry_df.index)))
            print(entry_index)
            
            entry_df = entry_df.set_index(entry_index, drop=True)
            
            df_concat = pd.concat([self, Ledger(entry_df)])
            print('\n\nLedger: add_entry() line 91: printing concatted df')
            print(df_concat)
            
            return Ledger(df_concat)
        else:
            raise ValueError('Journal entry debits do not equal journal entry credits: ', entry._debits, entry._credits)

    def account_segments(self):
        """Returns a view of the GL containing account segments broken out
        into separate columns
        """
        self[['seg' + str(i) for i in range(1,6)]] = self.account.str.split('-', expand=True)
        return self
    
    def account_balance(self, account: Account.Account):
        """Given an account object, returns current balance of that account"""
        
        df = self.loc[self['account'] == str(account)].copy()
        neg = ['debit', 'credit']
        pos = Account.seg2_positive[account._segments[1]]
        
        neg.remove(pos)
        neg = neg[0]
        
        df[neg] = df[neg] * -1
        
        balance = df[pos].sum() + df[neg].sum()
        
        return balance
    
    def save_to_file(self, path):
        self.to_csv(path, index=False)

    def set_entry_id(self):
        last_id = self.id.max()
        Entry._id = last_id + 1