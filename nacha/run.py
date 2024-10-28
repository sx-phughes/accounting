from NachaConstructor import *
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


payables = pd.read_excel('C:/Users/phughes_simplextradi/Downloads/20241023 ACHs.xlsx', 'Sheet1', dtype=data_types)

nacha_file = NachaConstructor(payables)
files = nacha_file.main()
counter = 1
for i in files:
    with open(f'C:/Users/phughes_simplextradi/Downloads/ACHS_{counter}.txt', 'w') as file:
        file.write(i.__str__())
    counter += 1