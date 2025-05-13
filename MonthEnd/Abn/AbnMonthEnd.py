# Basic Imports
from datetime import datetime
import re
import pandas as pd
import numpy as np

# Package Imports
from MonthEnd.Abn import Base, FileGrabber
from AbnCash import AbnCash


save_to = f'{Base.get_Base.get_trading_path()()}/{Base.cm_moyr}'
ledger_mapping, account_mapping = FileGrabber.get_mapping_files()
patrick_data_files = \
    "C:/gdrive/Shared drives/accounting/patrick_data_files"
Base.pm_moyr = Base.t_minus.strftime('%Y%m')
cm_cash= FileGrabber.get_cash_file(Base.year, Base.month)
cm_position = FileGrabber.get_position_file(Base.year, Base.month)
pm_cash = FileGrabber.get_cash_file(
    Base.t_minus.year,
    Base.t_minus.month
)
pm_position = FileGrabber.get_position_file(
    Base.t_minus.year,
    Base.t_minus.month
)
    
def main()-> None:
    run_interest_data()
    run_data_tab()
    run_positions()
    run_misc_breakdown()

def run_interest_data() -> None:
    t_plus_eqt, t_plus_mics = run_cash(
        Base.t_plus.year,
        Base.t_plus.month
    )
    
    if not t_plus_eqt.empty:
        interest_data = interest_data(t_plus_eqt, t_plus_mics)
    
        interest_w_strat = pd.merge(
            interest_data, 
            account_mapping[['ACCOUNT', 'Strategy']], 
            'left', 
            left_on='Account', 
            right_on='ACCOUNT'
        )

        interest_data.to_csv(
            save_to + '/interest_data.csv', index=False
        )

def run_data_tab()-> None:
    data = get_combined_data()
    clean_data = clean_data_tab(data)
    final = finalize_data(clean_data)
    final.to_csv(save_to + '/data_df.csv', index=False)

def get_combined_data() -> pd.DataFrame:
    merged = merge_ledger_map_to_data(
        get_pm_data(),
        get_cm_data()
    )
    return merged

def get_pm_data() -> pd.DataFrame:
    pm_data = modfiy_cash(pm_cash)
    rename_opening_balance(pm_data, Base.pm_moyr)
    merged = merge_ledger_map_to_data(ledger_mapping, pm_data)
    return merged
    
def get_cm_data() -> pd.DataFrame:
    cm_data = modfiy_cash(cm_cash)
    update_ledger_mapping(cm_data)
    rename_opening_balance(cm_data)
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
        aggfunc='Sum'
    )
    index_reset = pivoted.reset_index(drop=False)
    return index_reset

def rename_opening_balance(data: pd.DataFrame, new_name: str) -> int:
    data.rename(columns={'Opening Balance': new_name}, inplace=True)

def update_ledger_mapping(cm_cash: pd.DataFrame) -> pd.DataFrame:
    diff_mask = ~cm_cash['Concat'].isin(ledger_mapping['ABN Map'])
    diffs = cm_cash.loc[diff_mask]
    new_mappings = get_new_ledger_mappings(diffs)
    ledger_mapping = pd.concat([ledger_mapping, new_mappings])
    ledger_mapping.reset_index(drop=True, inplace=True)
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
    mask = ledger_mapping['CashDescription'] == line_item
    cols = ['AccountID', 'Simplex Map']
    similar_items = ledger_mapping.loc[mask, cols]
    print('\n\tPossible Mappings:')
    for i in similar_items.index:
        account = similar_items.loc[i, 'AccountID']
        mapping = similar_items.loc[i, 'Simplex Map']
        print(f'\t\t{account} // {mapping}')

def save_ledger_to_disk() -> int:
    path = patrick_data_files + '/abn_month_end/ABN_ledger_mapping.csv'
    ledger_mapping.to_csv(path, index=False)
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
        account_mapping,
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
    
def run_positions() -> None:
    positions = get_positions_data()
    positions_pivot = get_positions_pivot(positions)
    get_category_sumnmary(positions_pivot)

def get_positions_data() -> pd.DataFrame:
    data = clean_positions_data()
    data['Unique Name'] = get_unique_name_col(data)
    data.to_csv(save_to + '/positions.csv', index=False)
    return data

def clean_positions_data() -> pd.DataFrame:
    positions = cm_position
    positions['Strike Price'] = positions['Strike Price'].astype(np.float64)
    positions['Expiry Date'] = positions['Expiry Date'].astype(np.int64)
    cols = ['Expiry Date', 'Put Call', 'Strike Price']
    positions[cols] = positions[cols].fillna('')
    return positions
    
def get_unique_name_col(data: pd.DataFrame) -> pd.Series:
    unique_name = pd.Series()
    for i, row in data.iterrows():
        unique_name.loc[i] = create_unique_name(row)
    return unique_name 
    
def create_unique_name(pos_df_row: pd.Series) -> str:
    row = pos_df_row
    acct_type = row['Account Type']
    symbol = row['Symbol']
    strike_price = row['Strike Price']
    expiry_date = row['Expiry Date']
    put_call = row['Put Call']
    
    unique_name = ''

    if acct_type not in ['BKDL', 'XMAR']:
        unique_name += 'Futures'
    
    for i in [symbol, strike_price, expiry_date, put_call]:
        if i in ['', 0, 0.0]:
            continue
        else:
            unique_name += str(i)
    
    return unique_name

def get_positions_pivot(data: pd.DataFrame) -> pd.DataFrame:
    pivot = data.pivot_table(
        values=['Mark to Market Value', 'OTE'],
        index='Unique Name',
        aggfunc='sum'
    )
    pivot = pivot.reset_index(drop=False)
    pivot[['Mark to Market Value', 'OTE']] = pivot[
        ['Mark to Market Value', 'OTE']
    ].fillna(0)
    pivot['Category']= pivot.apply(
        lambda row: get_category(row),
        axis=0,
        raw=False
    )
    pivot['Total Category'] = pivot['Mark to Market Value'] + pivot['OTE']
    pivot.to_csv(save_to + '/positions_pivot.csv', index=False)
    return pivot

def get_category(row: pd.Series) -> str:
    if row['ote'] != 0:
        return 'OTE'

    asset = get_asset_class(row["Unique Name"])
    if row['Mark to Market Value'] > 0:
        return "Long " + asset
    elif row['Mark to Market Value'] < 0:
        return "Short " + asset
        
def get_asset_class(unique_name: str) -> str:
    if "Futures" in unique_name:
        if "Put" in unique_name or "Call" in unique_name:
            return "Futures Option"
        else:
            return "Futures"
    elif "Put" in unique_name or "Call" in unique_name:
        return "Option"
    else:
        return "Stock" 

def get_category_sumnmary(pivot: pd.DataFrame) -> pd.DataFrame:
    categories = pivot.pivot_table(
        values='Total Value',
        index='Category',
        aggfunc='sum'
    )
    categories = categories.reset_index(drop=False)
    drop_na_categories(categories)
    categories.to_csv(
        save_to + '/positions_by_category.csv',
        index=False
        )

def drop_na_categories(data: pd.DataFrame) -> None:
    data.fillna(0, inplace=True)
    na_rows = data.loc[data['Total Value'] == 0].index
    data.drop(index=na_rows, inplace=True)
    
def grab_files(year, month) -> tuple[pd.DataFrame, pd.DataFrame]:
    csv_cash = FileGrabber.get_cash_file(year, month)
    position = FileGrabber.get_position_file(year, month)
    return (csv_cash, position)
    
def run_cash(year, month) -> tuple[pd.DataFrame, pd.DataFrame]:
    cash_files = AbnCash(year, month,
                         Base.get_trading_path() + '/' + Base.cm_moyr)
    eqt_data, mics_data = cash_files.main()
    return (eqt_data, mics_data)
    
def get_mapping_files(google_drive_root='C:/gdrive') -> tuple[
                      pd.DataFrame,
                      pd.DataFrame]:
    abn_files_path = google_drive_root \
        + '/Shared drives/accounting/patrick_data_files/abn_month_end'
    ledger_mapping = pd.read_csv(abn_files_path + '/ABN_ledger_mapping.csv')
    account_mapping = pd.read_csv(
        abn_files_path + '/ABN_account_mapping.csv'
    )

    return (ledger_mapping, account_mapping)

def interest_data(t_plus_eqt: pd.DataFrame,
                  t_plus_mics: pd.DataFrame) -> pd.DataFrame:
    phrases = ['AB INT', 'SHORT STOCK', 'HAIRCUT', 'FUT CAP INT']
    mask = '|'.join(phrases)
    
    eqt_int = t_plus_eqt[t_plus_eqt['Description'].str.contains(mask)]
    mics_int = t_plus_mics[t_plus_mics['Description'].str.contains(mask)]
    
    eqt_int = eqt_int[['DateEntered', 'Account', 'Amount', 'Description']]
    mics_int = mics_int[['DateEntered', 'Account', 'Amount', 'Description']]

    all_int = pd.concat([eqt_int, mics_int])
    
    return all_int

def run_misc_breakdown() -> None:
    misc_breakdown(Base.year, Base.month)
    
def misc_breakdown(year, month) -> None:
    df = run_cash(year, month)[0]
    df.loc[df['LedgerNumber'] == 8200].to_csv(
        save_to + '/misc_breakdown.csv'
    )
    
def script_wrapper() -> None:
    main()