""" Script for testing / debugging GL Program
"""


# Standard imports
import numpy as np
from datetime import datetime

# Package Imports
import Ledger
import Entry
import Account

gl = Ledger.Ledger(columns=Ledger.Ledger.cols)
print(gl.head())

new_line = Entry.EntryLine('TEC-1-0000--CHA', debit=np.float64(500), line_desc='line one')
second_line = Entry.EntryLine('TEC-2-0000--', credit=np.float64(500), line_desc='line two')


#### Testing Entry validation and line adding
entry_1 = Entry.Entry(lines=[new_line, second_line])

entry_1.date = np.array([2025, 3, 13])

#### Testing add entry to gl function
gl = gl.add_entry(entry_1)

## Testing Second Entry id incrementation
entry_2 = Entry.Entry()

entry_2.date = datetime(2025,3,14)

e2line1 = Entry.EntryLine('TEC-1-0000--CHA', debit=np.float64(798.82), line_desc='cash entry')
e2line2 = Entry.EntryLine('TEC-2-2000--', credit=np.float64(798.82), line_desc='exchange fee expensed')

entry_2.add_line(e2line1)

entry_2.add_line(e2line2)

gl = gl.add_entry(entry_2)

# Testing Account module functionality
chase = Account.Account(full_acct='TEC-1-0000--CHA')
ap = Account.Account('TEC', '2', '0000', '', '')
acc_exp = Account.Account('TEC', '2', '2000', '', '')