from NachaConstructor import *
from datetime import datetime
import pandas as pd

data_types = {
    'Vendor': str,
    'Invoice #': str,
    'Vendor ABA': str,
    'Vendor Account': str,
    'Vendor Name': str,
    'Simplex2': str,
    'Expense Category': str,
    'Approved By': str,
    'Payment Type': str,
    'Amount': float
}

valuedate = datetime(2024,10,31).strftime('%y%m%d')

payables = pd.read_excel('C:/gdrive/Shared drives/accounting/Payables/2024/202410/2024-10-31/2024-10-31 Payables.xlsm', 'Invoices', dtype=data_types)
payables = payables.loc[payables['Payment Type'] == 'ACH'].copy()

### value date must be formatted "YYMMDD"
nacha_file = NachaConstructor(payables, valuedate)
files = nacha_file.main()
counter = 1
for i in files:
    with open(f'C:/Users/phughes_simplextradi/Downloads/{valuedate}_ACHS_{counter}.txt', 'w') as file:
        file.write(i.__str__())
    counter += 1