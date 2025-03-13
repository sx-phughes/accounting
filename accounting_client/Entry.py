"""Module for Ledger Entry Classes
"""
import numpy as np
from datetime import datetime

class EntryLine:
    """Base class for GL entry line"""
    def __init__(
            self, account: str, debit: np.float64 = None, credit: np.float64 = None,
            line_desc: str = None, vendor: str = None):
        self._validate(debit, credit)
        self._account = account
        self._debit = debit
        self._credit = credit
        self._desc = line_desc
        self._vendor = vendor

    def _validate(self, debit, credit):
        """Ensures only debit or a credit is submitted"""
        types = [type(x) for x in [debit, credit]]
        if types.count(np.float64) == 1:
            return True
        else:
            raise TypeError(
                "Can only have a value for debit or a value for credit"
                )
            

class Entry:
    """Base class for GL Entry"""
    id = 0
    def __init__(
            self, date: np.ndarray[np.int64] | datetime = None,
            lines: list[EntryLine] | EntryLine = None):
        self._id = Entry.id
        Entry.id += 1
        
        self._debits = 0
        self._credits = 0
        self._lines = []
        self.date = date
        
        if lines:
            self.add_line(lines)
    
    def __repr__(self):
        s = f'Entry object {self.id} {self.date} {self._debits}d {self._credits}c'
        return s 
    
    @property
    def date(self):
        return self._date
    
    @date.setter
    def date(self, date: np.ndarray[np.int64] | datetime):
        if type(date) == np.ndarray:
            self._date = datetime(date[0], date[1], date[2])
        else:
            self._date = date
    
    def add_line(self, line: list[EntryLine] | EntryLine):
        """Supports inputs of single and multiple entry lines"""
        if not isinstance(line, list):
            self._lines.append(line)
        else:
            for l in line:
                if l._debit:
                    self._debits += l._debit
                else:
                    self._credits += l._credit
                    
                self._lines.append(l)
            
    def validate_entry(self):
        """Debits must equal credits, must have a date"""
        if self._debits != self._credits:
            return False
        
        if not self.date:
            return False
        
        return True
    
    def read_csv(self, path: str):
        pass