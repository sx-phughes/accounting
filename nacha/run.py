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
vd_year = int(input('VD Year:\n>\t'))
vd_month = int(input('VD Month:\n>\t'))
vd_day = int(input('VD Day:\n>\t'))

pb_year = int(input('Payables Year:\n>\t'))
pb_month = int(input('Payables Month:\n>\t'))
pb_day = int(input('Payables Day:\n>\t'))

payables_date = datetime(pb_year,pb_month,pb_day)
valuedate = datetime(vd_year,vd_month,vd_day).strftime('%y%m%d')

payables_path = f'C:/gdrive/Shared drives/accounting/Payables/{payables_date.strftime('%Y')}/{payables_date.strftime('%Y%m')}/{payables_date.strftime('%Y-%m-%d')}/{payables_date.strftime('%Y-%m-%d')} Payables.xlsm'
payables = pd.read_excel(payables_path, 'Invoices', dtype=data_types)
payables = payables.loc[payables['Payment Type'] == 'ACH'].copy()

### value date must be formatted "YYMMDD"
nacha_file = NachaConstructor(payables, valuedate)
files = nacha_file.main()
counter = 1
for i in files:
    with open(f'C:/Users/phughes_simplextradi/Downloads/{valuedate}_ACHS_{counter}.txt', 'w') as file:
        file.write(i.__str__())
    counter += 1