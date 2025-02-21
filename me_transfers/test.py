from DataGathering import *
from TransferTableSetup import *

path = 'C:/gdrive/My Drive/BAML/Account Mgmt Analysis Reports/Account Management Analysis Report-64499-01-31-2025.pdf'

df = BamlMonthEndStmtReader(path)

row_data = []

baml_accounts = [
    '644-40300-D4',
    '644-40846-D6',
    '644-40865-D6',
    '644-41315-D1',
    '644-99865-D6'
]

abn_eqt_accounts = [
    '008MMXV',
    '695M526',
    '695M622',
    '695M679',
    '695MMXV',
    '813M473',
    '813M758'
]

abn_fut_accounts = [
    '6901SIMP3',
    '6901SIMP4',
    '6901SIMP1',
    '6901SIMP2',
    '6901SIMP7'
]

for i, row in df.iterrows():
    if row['ACCOUNT NO.'] in baml_accounts:
        i_row = [
            row['ACCOUNT NO.'],
            round(float(row['EQUITY']),2)
        ]
        row_data.append(i_row)

tfr_date = '02/03/2025'
table = BamlTransferTable(transfer_date=tfr_date)

for i in row_data:
    print(i)
    table.add_row(i[0], i[1])

table.add_final_row()

table.to_csv('./testBamlTable.csv')