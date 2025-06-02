import pandas as pd
from datetime import datetime
import re

from MonthEnd.Abn import Base, FileGrabber

def get_data()-> pd.DataFrame:
    data = get_combined_data()
    clean_data = clean_data_tab(data)
    final = finalize_data(clean_data)
    return final

def get_combined_data() -> pd.DataFrame:
    merged = merge_ledger_map_to_data(
        get_pm_data(),
        get_cm_data()
    )
    return merged

def get_pm_data() -> pd.DataFrame:
    pm_data = modfiy_cash(FileGrabber.pm_cash)
    rename_opening_balance(pm_data, Base.pm_moyr)
    merged = merge_ledger_map_to_data(Base.ledger_mapping, pm_data)
    return merged
    
def get_cm_data() -> pd.DataFrame:
    cm_data = modfiy_cash(FileGrabber.cm_cash)
    update_ledger_mapping(cm_data)
    rename_opening_balance(cm_data, Base.cm_moyr)
    return cm_data
    
def modfiy_cash(cash: pd.DataFrame) -> pd.DataFrame:
    needed_data = cash[[
        'Account Name',
        'Cash Title',
        'Opening Balance'
    ]].copy()
    needed_data['Concat'] = needed_data['Account Name'] \
                            + needed_data['Cash Title']
    pivoted = needed_data.pivot_table(
        values='Opening Balance',
        index=['Account Name', 'Cash Title', 'Concat'],
        aggfunc='sum'
    )
    index_reset = pivoted.reset_index(drop=False)
    return index_reset

def rename_opening_balance(data: pd.DataFrame, new_name: str) -> int:
    data.rename(columns={'Opening Balance': new_name}, inplace=True)

def update_ledger_mapping(cm_cash: pd.DataFrame) -> pd.DataFrame:
    diff_mask = ~cm_cash['Concat'].isin(Base.ledger_mapping['ABN Map'])
    diffs = cm_cash.loc[diff_mask]
    new_mappings = get_new_ledger_mappings(diffs)
    ledger_mapping = pd.concat([Base.ledger_mapping, new_mappings])
    ledger_mapping.reset_index(drop=True, inplace=True)
    Base.ledger_mapping = ledger_mapping
    save_ledger_to_disk()

def get_new_ledger_mappings(diffs_df: pd.DataFrame) -> pd.DataFrame:
    diffs_df = diffs_df.drop(columns='Opening Balance')
    new_mappings = []
    for i, row in diffs_df.iterrows():
        account = row.iloc[0]
        line_item = row.iloc[1]

        print(f'{account} // {line_item}')
        print_similar_items(line_item)

        print('Input new ledger mapping:')
        new_item = input('>\t')
        
        new_mappings.append(new_item)
    
    diffs_df['Ledger Mapping'] = new_mappings 

    renamer = {
        'Account Name': 'AccountID',
        'Cash Title': 'CashDescription',
        'Concat': 'ABN Map',
        'Ledger Mapping': 'Simplex Map'
    }
    diffs_df = diffs_df.rename(columns=renamer)
    input('\n\nClose ledger mapping file if open, enter to continue')
    
    return diffs_df

def print_similar_items(line_item: str) -> None:
    mask = Base.ledger_mapping['CashDescription'] == line_item
    cols = ['AccountID', 'Simplex Map']
    similar_items = Base.ledger_mapping.loc[mask, cols]
    print('\n\tPossible Mappings:')
    for i in similar_items.index:
        account = similar_items.loc[i, 'AccountID']
        mapping = similar_items.loc[i, 'Simplex Map']
        print(f'\t\t{account} // {mapping}')

def save_ledger_to_disk() -> int:
    path = Base.patrick_data_files + '/abn_month_end/ABN_ledger_mapping.csv'
    Base.ledger_mapping.to_csv(path, index=False)
    return 0

def merge_ledger_map_to_data(left_data: pd.DataFrame,
                             right_data: pd.DataFrame) -> pd.DataFrame:
    data = left_data.merge(
        right=right_data,
        how='left',
        left_on='ABN Map',
        right_on='Concat'
    )
    no_nas = data[['Account Name', 'Cash Title']].fillna('no match') 
    data[['Account Name', 'Cash Title']] = no_nas
    dropped_cols = data.drop(columns=[
        'Account Name', 
        'Cash Title', 
        'Concat'
    ])

    return dropped_cols
    
def clean_data_tab(dirty_data: pd.DataFrame) -> pd.DataFrame:
    drop_na(dirty_data)
    zeroed_margin = zero_margin(dirty_data)
    change_col = zeroed_margin[Base.cm_moyr] - zeroed_margin[Base.pm_moyr]
    zeroed_margin['Change'] = change_col
    return zeroed_margin

def drop_na(data: pd.DataFrame) -> None:
    na_mask = (data[Base.pm_moyr].isna()) & (data[Base.cm_moyr].isna())
    both_na = data.loc[na_mask].index
    data.drop(both_na, inplace=True)
    
def zero_margin(data: pd.DataFrame) -> pd.DataFrame:
    margin_mask = data['CashDescription'].str.contains(
        'margin',
        flags=re.IGNORECASE
    )
    for i in [Base.pm_moyr, Base.cm_moyr]:
        data[i] = data[i].mask(margin_mask, 0)
    return data

def rename_for_final(data: pd.DataFrame) -> None:
    renamer = {
        'Simplex Map': 'Mapping',
        'ABN Map': 'Concatenation',
        Base.cm_moyr: datetime.strptime(
            Base.cm_moyr + '01',
            '%Y%m%d'
        ).strftime('%b %Y\t'),
        Base.pm_moyr: datetime.strptime(
            Base.pm_moyr + '01',
            '%Y%m%d'
        ).strftime('%b %Y\t')
    }
    data.rename(columns=renamer, inplace=True)

def finalize_data(data: pd.DataFrame) -> pd.DataFrame:
    merged_accounts = data.merge(
        Base.account_mapping,
        'left',
        left_on='AccountID',
        right_on='ACCOUNT'
    )
    dropped_cols = merged_accounts.drop(columns=['ACCOUNT', 'Description'])
    col_subset = [
        'AccountID',
        'CashDescription',
        Base.cm_moyr,
        Base.pm_moyr,
        'Change',
        'Strategy',
        'Simplex Map',
        'ABN Map'
    ]
    final = dropped_cols[col_subset]

    rename_for_final(final)
    return final