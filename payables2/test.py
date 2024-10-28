from PayablesStructure import *
import os
from datetime import datetime

if os.path.exists('C:/gdrive/My Drive/code_projects/payables2/payables_test_dir/202410/Katten Muchin Rosenman40224033 - 40224033.pdf'):
    os.remove('C:/gdrive/My Drive/code_projects/payables2/payables_test_dir/202410/Katten Muchin Rosenman40224033 - 40224033.pdf')

pt = PayablesTable()
kmr = Invoice(40224033, 'Katten', 202410, 381.33, pdf = 'C:/Users/phughes_simplextradi/Downloads/KMR - 40224033.pdf')
kmr_1 = Amendment(kmr, '40224033_1', 380.00, pdf = 'C:/Users/phughes_simplextradi/Downloads/KMR - 40224033.pdf')


pt.add_invoice(kmr)

print(pt.payables_table)

pt.add_invoice(kmr_1)

print(pt.payables_table)

summary, history = pt.consolidate_amendments(kmr.uniquename)

print(summary)
print(history)

print('Unpaids')
print(pt.get_unpaids())

pt.mark_paid(kmr.uniquename, 20241025)

summary, history = pt.consolidate_amendments(kmr.uniquename)

print(summary)
print(history)