import pandas as pd
from BrokerFile import BrokerFile
from get_sheet_names import get_sheet_names

paths = [
    'C:/gdrive/Shared drives/accounting/Payables/2024/202410/Broker Invoices/Cowen - 32935.xls',
    'C:/gdrive/Shared drives/accounting/Payables/2024/202410/Broker Invoices/Elix - TGS_2024-09_SIMP-CH_ELIXD.XLSX'
]

for path in paths:
    sheets = get_sheet_names(path)

    df = pd.read_excel(path, sheets[0])

    file = BrokerFile(broker_file=df)

    clean_file = file.comp_df()

    print(clean_file)
