""" Script for testing / debugging GL Program
"""

# Standard imports
import numpy as np
from datetime import datetime
import os

# Package Imports
import Ledger
import Entry
import Account
import LoadQb


def main_test():
    gl = Ledger.Ledger(columns=Ledger.Ledger.cols)
    print(gl.head())

    new_line = Entry.EntryLine(
        'TEC-1-0000--CHA',
        debit=np.float64(500),
        line_desc='line one'
    )
    second_line = Entry.EntryLine(
        'TEC-2-0000--',
        credit=np.float64(500),
        line_desc='line two'
    )


    #### Testing Entry validation and line adding
    entry_1 = Entry.Entry(lines=[new_line, second_line])

    entry_1.date = np.array([2025, 3, 13])

    #### Testing add entry to gl function
    gl = gl.add_entry(entry_1)

    ## Testing Second Entry id incrementation
    entry_2 = Entry.Entry()

    entry_2.date = datetime(2025,3,14)

    e2line1 = Entry.EntryLine(
        'TEC-1-0000--CHA',
        debit=np.float64(798.82),
        line_desc='cash entry'
    )

    e2line2 = Entry.EntryLine(
        'TEC-2-2000--',
        credit=np.float64(798.82),
        line_desc='exchange fee expensed'
    )

    entry_2.add_line(e2line1)

    entry_2.add_line(e2line2)

    gl = gl.add_entry(entry_2)

    # Testing Account module functionality
    chase = Account.Account(full_acct='TEC-1-0000--CHA')
    ap = Account.Account('TEC', '2', '0000', '', '')
    acc_exp = Account.Account('TEC', '2', '2000', '', '')

    # Testing Save Ledger Functionality
    print('\n\nTest: Line 66: Ledger Save Capability')
    print('\nTest: Line 67: Saving Ledger to file')
    path = 'C:/gdrive/Shared drives/accounting/patrick_data_files/new_gl/test_ledger.csv'
    gl.save_to_file(path)
    print('\nTest: Line 68: ls output of save dir')
    path_to_scan = '\\'.join(path.split('/')[:-1])
    print('Test: printing path to check', path_to_scan)
    print('\n'.join(os.listdir(path_to_scan)))

    # Testing Load Ledger Functionality
    gl2 = Ledger.load_ledger(path)
    print('\n\nTest: Line 78: loading and printing saved ledger')
    print(gl2)
    print('\n\nTest: Checking updated Entry ID from ledger load')
    print(Entry.Entry._id)

    # Testing Third Entry with loaded ledger
    print('\n\nTest: Line 84: Creating 3rd Entry')
    entry3L1 = Entry.EntryLine(acc_exp, debit=np.float64(600), line_desc='double payment')
    entry3L2 = Entry.EntryLine(chase, credit=np.float64(600), line_desc='double payment')

    entry3 = Entry.Entry(lines=[entry3L1, entry3L2], date=np.array([2025,3,18]))
    print('\nTest: Line 89: Adding 3rd Entry to GL')
    gl2 = gl2.add_entry(entry3)
    print('\nTest: Line 91: Printing GL after 3rd Entry Add')
    print(gl2)

    # Testing Account index accessing with account string
    print('\n\nTest: Line 95: printing account string')
    print('\n', chase.full_account)
    print('\nTest: Line 97: Accessing account object from class and printing')
    print(Account.mgr[chase.full_account])


    # Testing Loading accounts from file
    print('\n\nTest: Line 103: Testing account load from file')
    load_path = 'C:/gdrive/Shared drives/accounting/patrick_data_files/new_gl/accounts.csv'
    Account.load_accounts(load_path)
    print('Account Load Successful')
    print('\nTest: line 107: checking accounts not programmed here')
    print(
        Account.mgr['TEC-1-2100--'], 
        Account.mgr['TEC-1-4000--'], 
        Account.mgr['TEC-6-1000--']
    )

def load_qb_test():
    tech_test_path = 'C:/gdrive/Shared drives/accounting/patrick_data_files/new_gl/test_tech.csv'
    df = LoadQb.load_ledger(tech_test_path)
    
    clean_df = LoadQb.clean_ledger(df)
    
    print(clean_df)
    journals = LoadQb.make_jes(clean_df, 'TEC')
    ledger = LoadQb.make_ledger_obj(journals)
    
    print(ledger)
    
load_qb_test()