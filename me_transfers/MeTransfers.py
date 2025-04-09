from me_transfers.DataGathering import *
from me_transfers.TransferTableSetup import *
from datetime import datetime
import os

def baml_path(date: datetime):
    
    path = f'C:/gdrive/My Drive/BAML/Account Mgmt Analysis Reports/Account Management Analysis Report-64499-{date.strftime('%m-%d-%Y')}.pdf'
    
    return path

def abn_date(date: datetime):
    return date.strftime('%Y%m%d')

def zero_pad(string: str, t_length: int, before: bool=True):
    num_zeros = t_length - len(string)
    
    if before:
        string = '0' * num_zeros + string
    else:
        string += '0' * num_zeros
        
    return string

def run_baml_table(date: datetime, save_path = '.'):
    path = baml_path(date)

    # Get BAML Month-end Data
    df = BamlReader2(path)

    row_data = []

    baml_accounts = [
        '644-40300-D4',
        '644-40846-D6',
        '644-40865-D6',
        '644-41315-D1',
        '644-99865-D6'
    ]

    for i, row in df.iterrows():
        if row['Account No.'] in baml_accounts:
            i_row = [
                row['Account No.'],
                round(float(row['Equity']),2)
            ]
            row_data.append(i_row)

    tfr_date = '3/3/2025'
    baml_table = BamlTransferTable(transfer_date=tfr_date)

    for i in row_data:
        print(i)
        baml_table.add_data_row(i[0], i[1])



    baml_table.add_final_row()

    baml_table.to_csv(save_path + f'/{date.strftime('%Y%m%d')} BofA Transfers.csv')
    
    
def run_abn_tables(date: datetime, save_path = '.'):
    date_str = abn_date(date)
    
    abn_eqt_accounts = (
        '008MMXV',      # MM    VIX Options
        '695M526',      # MM    NXM SPY Stock and ETFs
        '695M622',      # MM    Main MM Account
        '695M679',      # MM    NXM IWM, QQQ stock and ETFs
        '695MMXZ',      # MM    NXM SPX Boxes
        '813M473',      # MM    XM IWM, QQQ Options
        '813M758'       # XM    SPY and SPX Options
    )

    abn_fut_accounts = (
        '6901SIMP3',    # Prop  Futures (Elliot)
        '6901SIMP4',    # Prop  Euro/SOFR
#       '6901SIMP9',    # Prop  JJ Futures
        '8131SIMP1',    # MM    XM VIX Futures
        '8131SIMP2',    # MM    XM EMini Futures
        '8131SIMP7'     # MM    XM NQ, RTY Futures
    )
    
    sixnine_tfr_table = AbnOptTransferTable('695')
    eightone_tfr_table = AbnOptTransferTable('813')
    futures_tfr_table = AbnFutTransferTable()
    et_tfr_table = AbnOptTransferTable('ET')    
    
    eqt_me_stmt, fut_me_stmt = AbnMonthEndStatements(date.strftime('%Y%m%d'))
    et_table = EtMonthEnd(date.year, date.month)
    
    eqt_data = {acct: eqt_me_stmt.loc[eqt_me_stmt['ACCOUNT'] == acct, 'EQUITY'].values[0] for acct in abn_eqt_accounts}
    fut_data = {acct: fut_me_stmt.loc[fut_me_stmt['Account'] == acct, 'NetLiq'].values[0] for acct in abn_fut_accounts}
    
    
    table_dict = {
        '695': sixnine_tfr_table,
        '813': eightone_tfr_table,
        'Fut': futures_tfr_table
    }
    
    acct_mapping = {
        '695': abn_eqt_accounts,
        '813': abn_eqt_accounts,
        'Fut': abn_fut_accounts
    }
    
    data_ref = {
        '695': eqt_data,
        '813': eqt_data,
        'Fut': fut_data
    }
    
    f_names = {
        '695': ' - ABN - 695.csv',
        '813': ' - ABN - 813.csv',
        'Fut': ' - ABN - Futures.csv',
        'ET': ' - ABN - ETs.csv'
    }
    
    for acct_group in table_dict.keys():
        for i in acct_mapping[acct_group]:
            if i[0:3] == acct_group or (i[0:3] == '008' and acct_group == '813') or acct_group == 'Fut':
                table_dict[acct_group].add_data_row(i, data_ref[acct_group][i])
            else:
                continue
            
            
        if acct_group != 'Fut':
            table_dict[acct_group].add_final_row()
    
    for acct in et_table['Account']:
        et_tfr_table.add_data_row(acct, et_table.loc[et_table['Account'] == acct, 'Transfer'].values[0], flip=False)
        
    et_tfr_table.add_final_row()
           
    eightone_tfr_table['Firm'] = eightone_tfr_table['Firm'].apply(lambda x: zero_pad(x, 3))    
    
    for acct_group in table_dict.keys():
        table_dict[acct_group].to_csv(f'{save_path}/{date_str}{f_names[acct_group]}', index=False)
    
    et_tfr_table.to_csv(f'{save_path}/{date_str}{f_names['ET']}')
        
def run_ME_Transfers(year, month, day, save_path=os.environ['HOMEPATH'] + '\\Downloads'):
    dt = datetime(int(year), int(month), int(day))
    
    run_abn_tables(dt, save_path)
    run_baml_table(dt, save_path)
