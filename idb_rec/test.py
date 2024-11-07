import pandas as pd
from BrokerFile import BrokerFile
from get_sheet_names import get_sheet_names

path = 'C:/gdrive/Shared drives/accounting/Payables/2024/202410/Broker Invoices/Cowen - 32935.xls'

sheets = get_sheet_names(path)

df = pd.read_excel(path, sheets[0])

cowen = BrokerFile(broker_file=df)

cowen_comp = cowen.comp_df()

print(cowen_comp)
