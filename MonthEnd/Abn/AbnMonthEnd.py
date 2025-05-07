# Basic Imports
from datetime import datetime
import re
import pandas as pd
import numpy as np

# Package Imports
from MonthEnd.Abn.FileGrabber import AbnFileGrabber
from MonthEnd.Abn.AbnBase import *
from AbnCash import AbnCash


class AbnMonthEnd(AbnBase):
    def __init__(self, year: int, month: int):
        super().__init__(year, month)
        self.save_to = f'{self.trading_path}/{self.moyr}'
        self.ledger_mapping, self.account_mapping = self.get_mapping_files()
        self.patrick_data_files = "C:/gdrive/Shared drives/accounting/patrick_data_files"
        self.pm_moyr = self.t_minus.strftime('%Y%m')
        self.cm_cash, self.cm_position = self.grab_files(self.year, self.month)
        self.pm_cash, self.pm_position = self.grab_files(self.t_minus_year, self.t_minus_month)
        
    def main(self) -> None:
        self.run_interest_data()
        self.run_data_tab()
        self.run_positions()
        self.run_misc_breakdown()

    def run_interest_data(self) -> None:
        t_plus_eqt, t_plus_mics = self.run_cash(self.t_plus_year, self.t_plus_month)
        
        if not t_plus_eqt.empty:
            interest_data = self.interest_data(t_plus_eqt, t_plus_mics)
        
            interest_w_strat = pd.merge(
                interest_data, 
                self.account_mapping[['ACCOUNT', 'Strategy']], 
                'left', 
                left_on='Account', 
                right_on='ACCOUNT'
            )

            interest_data.to_csv(self.save_to + '/interest_data.csv', index=False)

    def run_data_tab(self) -> None:
        data = self.get_combined_data()
        clean_data = self.clean_data_tab(data)
        final = self.finalize_data(clean_data)
        final.to_csv(self.save_to + '/data_df.csv', index=False)
    
    def get_combined_data(self) -> pd.DataFrame:
        merged = self.merge_ledger_map_to_data(
            self.get_pm_data(),
            self.get_cm_data()
        )
        return merged

    def get_pm_data(self) -> pd.DataFrame:
        pm_data = self.modfiy_cash(self.pm_cash)
        self.rename_opening_balance(pm_data, self.pm_moyr)
        merged = self.merge_ledger_map_to_data(self.ledger_mapping, pm_data)
        return merged
        
    def get_cm_data(self) -> pd.DataFrame:
        cm_data = self.modfiy_cash(self.cm_cash)
        self.update_ledger_mapping(cm_data)
        self.rename_opening_balance(cm_data)
        return cm_data
        
    def modfiy_cash(self, cash: pd.DataFrame) -> pd.DataFrame:
        needed_data = cash[['Account Name', 'Cash Title', 'Opening Balance']].copy()
        needed_data['Concat'] = needed_data['Account Name'] + needed_data['Cash Title']
        pivoted = needed_data.pivot_table(values='Opening Balance', index=['Account Name', 'Cash Title', 'Concat'], aggfunc='Sum')
        index_reset = pivoted.reset_index(drop=False)
        return index_reset

    def rename_opening_balance(self, data: pd.DataFrame, new_name: str) -> int:
        data.rename(columns={'Opening Balance': new_name}, inplace=True)

    def update_ledger_mapping(self, cm_cash: pd.DataFrame) -> pd.DataFrame:
        diffs = cm_cash.loc[~cm_cash['Concat'].isin(self.ledger_mapping['ABN Map'])]
        new_mappings = self.get_new_ledger_mappings(diffs)
        self.ledger_mapping = pd.concat([self.ledger_mapping, new_mappings])
        self.ledger_mapping.reset_index(drop=True, inplace=True)
        self.save_ledger_to_disk()

    def get_new_ledger_mappings(self, diffs_df: pd.DataFrame) -> pd.DataFrame:
        diffs_df = diffs_df.drop(columns='Opening Balance')
        new_mappings = []
        for i, row in diffs_df.iterrows():
            account = row.iloc[0]
            line_item = row.iloc[1]

            print(f'{account} // {line_item}')
            self.print_similar_items(line_item)

            print('Input new ledger mapping:')
            new_item = input('>\t')
            
            new_mappings.append(new_item)
        
        diffs_df['Ledger Mapping'] = new_mappings 

        renamer = {'Account Name': 'AccountID', 'Cash Title': 'CashDescription', 'Concat': 'ABN Map', 'Ledger Mapping': 'Simplex Map'}
        diffs_df = diffs_df.rename(columns=renamer)
        input('\n\nClose ledger mapping file if open, enter to continue')
        
        return diffs_df

    def print_similar_items(self, line_item: str) -> None:
        mask = self.ledger_mapping['CashDescription'] == line_item
        similar_items = self.ledger_mapping.loc[mask, ['AccountID', 'Simplex Map']]
        print('\n\tPossible Mappings:')
        for i in similar_items.index:
            account = similar_items.loc[i, 'AccountID']
            mapping = similar_items.loc[i, 'Simplex Map']
            print(f'\t\t{account} // {mapping}')
    
    def save_ledger_to_disk(self) -> int:
        path = self.patrick_data_files + '/abn_month_end/ABN_ledger_mapping.csv'
        self.ledger_mapping.to_csv(path, index=False)
        return 0
    
    def merge_ledger_map_to_data(self, left_data: pd.DataFrame, right_data: pd.DataFrame) -> pd.DataFrame:
        data = left_data.merge(right=right_data, how='left', left_on='ABN Map', right_on='Concat')
        data[['Account Name', 'Cash Title']] = data[['Account Name', 'Cash Title']].fillna('no match')
        dropped_cols = data.drop(columns=['Account Name', 'Cash Title', 'Concat'])
        return dropped_cols
        
    def clean_data_tab(self, dirty_data: pd.DataFrame) -> pd.DataFrame:
        self.drop_na(dirty_data)
        zeroed_margin = self.zero_margin(dirty_data)
        zeroed_margin['Change'] = zeroed_margin[self.moyr] - zeroed_margin[self.pm_moyr]
        return zeroed_margin
    
    def drop_na(self, data: pd.DataFrame) -> None:
        na_mask = (data[self.pm_moyr].isna()) & (data[self.moyr].isna())
        both_na = data.loc[na_mask].index
        data.drop(both_na, inplace=True)
        
    def zero_margin(self, data: pd.DataFrame) -> pd.DataFrame:
        margin_mask = data['CashDescription'].str.contains(
            'margin',
            flags=re.IGNORECASE
        )
        for i in [self.pm_moyr, self.moyr]:
            data[i] = data[i].mask(margin_mask, 0)
        return data

    def rename_for_final(self, data: pd.DataFrame) -> None:
        renamer = {
            'Simplex Map': 'Mapping',
            'ABN Map': 'Concatenation',
            self.moyr: datetime.strptime(self.moyr + '01', '%Y%m%d').strftime('%b %Y\t'),
            self.pm_moyr: datetime.strptime(self.pm_moyr + '01', '%Y%m%d').strftime('%b %Y\t')
        }
        data.rename(columns=renamer, inplace=True)
    
    def finalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        merged_accounts = data.merge(self.account_mapping, 'left', left_on='AccountID', right_on='ACCOUNT')
        dropped_cols = merged_accounts.drop(columns=['ACCOUNT', 'Description'])
        col_subset = [
            'AccountID',
            'CashDescription',
            self.moyr,
            self.pm_moyr,
            'Change',
            'Strategy',
            'Simplex Map',
            'ABN Map'
        ]
        final = dropped_cols[col_subset]

        self.rename_for_final(final)
        return final
        
    def run_positions(self) -> None:
        positions = self.get_positions_data()
        positions_pivot = self.get_positions_pivot(positions)
        self.get_category_sumnmary(positions_pivot)

    def get_positions_data(self) -> pd.DataFrame:
        data = self.clean_positions_data()
        data['Unique Name'] = self.get_unique_name_col(data)
        data.to_csv(self.save_to + '/positions.csv', index=False)
        return data
    
    def clean_positions_data(self) -> pd.DataFrame:
        positions = self.cm_position
        positions['Strike Price'] = positions['Strike Price'].astype(np.float64)
        positions['Expiry Date'] = positions['Expiry Date'].astype(np.int64)
        positions[['Expiry Date', 'Put Call', 'Strike Price']] = positions[['Expiry Date', 'Put Call', 'Strike Price']].fillna('')
        return positions
        
    def get_unique_name_col(self, data: pd.DataFrame) -> pd.Series:
        unique_name = pd.Series()
        for i, row in data.iterrows():
            unique_name.loc[i] = self.create_unique_name(row)
        return unique_name 
        
    def create_unique_name(self, pos_df_row: pd.Series) -> str:
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
    
    def get_positions_pivot(self, data: pd.DataFrame) -> pd.DataFrame:
        pivot = data.pivot_table(values=['Mark to Market Value', 'OTE'], index='Unique Name', aggfunc='sum')
        pivot = pivot.reset_index(drop=False)
        pivot[['Mark to Market Value', 'OTE']] = pivot[['Mark to Market Value', 'OTE']].fillna(0)
        pivot['Category']= pivot.apply(lambda row: self.get_category(row), axis=0, raw=False)
        pivot['Total Category'] = pivot['Mark to Market Value'] + pivot['OTE']
        pivot.to_csv(self.save_to + '/positions_pivot.csv', index=False)
        return pivot

    def get_category(self, row: pd.Series) -> str:
        if row['ote'] != 0:
            return 'OTE'

        asset = self.get_asset_class(row["Unique Name"])
        if row['Mark to Market Value'] > 0:
            return "Long " + asset
        elif row['Mark to Market Value'] < 0:
            return "Short " + asset
            
    def get_asset_class(self, unique_name: str) -> str:
        if "Futures" in unique_name:
            if "Put" in unique_name or "Call" in unique_name:
                return "Futures Option"
            else:
                return "Futures"
        elif "Put" in unique_name or "Call" in unique_name:
            return "Option"
        else:
            return "Stock" 

    def get_category_sumnmary(self, pivot: pd.DataFrame) -> pd.DataFrame:
        categories = pivot.pivot_table(values = 'Total Value', index = 'Category', aggfunc = 'sum')
        categories = categories.reset_index(drop=False)
        self.drop_na_categories(categories)
        categories.to_csv(self.save_to + '/positions_by_category.csv', index=False)
    
    def drop_na_categories(self, data: pd.DataFrame) -> None:
        data.fillna(0, inplace=True)
        na_rows = data.loc[data['Total Value'] == 0].index
        data.drop(index=na_rows, inplace=True)
        
    def grab_files(self, year, month) -> tuple[pd.DataFrame, pd.DataFrame]:
        if self.t_minus_month == 12 and month == 12:
            file_grabber = AbnFileGrabber(year, month)
            position = file_grabber.main()[1]
            csv_cash = AbnFileGrabber(year, 12).AbnEoyFile()
        else:
            file_grabber = AbnFileGrabber(year, month)
            csv_cash, position = file_grabber.main()

        
        return (csv_cash, position)
        
    def run_cash(self, year, month) -> tuple[pd.DataFrame, pd.DataFrame]:
        cash_files = AbnCash(year, month, self.trading_path + '/' + self.moyr)
        eqt_data, mics_data = cash_files.main()
        
        return (eqt_data, mics_data)
        
    def get_mapping_files(self, google_drive_root='C:/gdrive') -> tuple[pd.DataFrame, pd.DataFrame]:
        abn_files_path = google_drive_root + '/Shared drives/accounting/patrick_data_files/abn_month_end'
        ledger_mapping = pd.read_csv(abn_files_path + '/ABN_ledger_mapping.csv')
        account_mapping = pd.read_csv(abn_files_path + '/ABN_account_mapping.csv')

        return (ledger_mapping, account_mapping)
    
    def interest_data(self, t_plus_eqt: pd.DataFrame, t_plus_mics: pd.DataFrame) -> pd.DataFrame:
        phrases = ['AB INT', 'SHORT STOCK', 'HAIRCUT', 'FUT CAP INT']
        mask = '|'.join(phrases)
        
        eqt_int = t_plus_eqt[t_plus_eqt['Description'].str.contains(mask)]
        mics_int = t_plus_mics[t_plus_mics['Description'].str.contains(mask)]
        
        eqt_int = eqt_int[['DateEntered', 'Account', 'Amount', 'Description']]
        mics_int = mics_int[['DateEntered', 'Account', 'Amount', 'Description']]

        all_int = pd.concat([eqt_int, mics_int])
        
        return all_int
    
    def run_misc_breakdown(self) -> None:
        self.misc_breakdown(self.year, self.month)
        
    def misc_breakdown(self, year, month) -> None:
        df = self.run_cash(year, month)[0]
        df.loc[df['LedgerNumber'] == 8200].to_csv(self.save_to + '/misc_breakdown.csv')
    
def script_wrapper(year, month) -> None:
    me_obj = AbnMonthEnd(int(year), int(month))
    me_obj.main()
