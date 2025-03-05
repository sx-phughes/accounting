#### Planning ####

## Files Needed ##
#   1. yyyymmdd-2518-C2518-CSVCASH_AC.csv.zip
#   2. yyyymmdd-2518-C2518-POSITION.csv.zip
#   3. Closing month cash files
#   4. T+1 cash files
#       a. EQTCASH_yyyymmdd.CSV
#       b. MICS_Cash_20240501.csv

from abn_month_end.FileGrabber import AbnFileGrabber
from AbnBase import *
from patrick_functions.AbnCash import AbnCash
from datetime import datetime
import re
import pandas as pd


class AbnMonthEnd(AbnBase):
    def __init__(self, year: int, month: int):
        super().__init__(year, month)
        self.save_to = f'{self.trading_path}/{self.moyr}'
        
    def main(self):
        cm_csv_cash, cm_position = self.grab_files(self.year, self.month)
        pm_csv_cash, pm_position = self.grab_files(self.t_minus_year, self.t_minus_month)
        
        t_plus_eqt, t_plus_mics = self.run_cash(self.t_plus_year, self.t_plus_month)
        
        ledger_mapping, account_mapping = self.get_mapping_files()
        
        interest_data = self.interest_data(t_plus_eqt, t_plus_mics)
        
        interest_w_strat = pd.merge(interest_data, account_mapping[['ACCOUNT', 'Strategy']], 'left', left_on='Account', right_on='ACCOUNT',)
        
        data_tab_df = self.data_tab(cm_csv_cash, pm_csv_cash, ledger_mapping, account_mapping)
        
        positions, pivot, categories = self.positions_tab(cm_position)
        
        self.misc_breakdown(self.year, self.month).to_csv(self.save_to + '/misc_breakdown.csv', index=False)
        interest_data.to_csv(self.save_to + '/interest_data.csv', index=False)
        data_tab_df.to_csv(self.save_to + '/data_df.csv', index=False)
        positions.to_csv(self.save_to + '/positions_df.csv', index=False)
        pivot.to_csv(self.save_to + '/positions-pivot_df.csv', index=False)
        categories.to_csv(self.save_to + '/positions-by-category_df.csv', index=False)
        
        return data_tab_df
        
        
    def data_tab(self, cm_cash: pd.DataFrame, pm_cash: pd.DataFrame, ledger_map: pd.DataFrame, account_map: pd.DataFrame):
        # Copy required data from CSV_CASH files PM & CM
        data_df_pm = pm_cash[['Account Name', 'Cash Title', 'Opening Balance']].copy()
        data_df_cm = cm_cash[['Account Name', 'Cash Title', 'Opening Balance']].copy()
        
        # Add Concat columns to dfs
        data_df_cm['Concat'] = data_df_cm['Account Name'] + data_df_cm['Cash Title']
        data_df_pm['Concat'] = data_df_pm['Account Name'] + data_df_pm['Cash Title']
            
        # Pivot both tables to remove duplicates
        data_df_pm = data_df_pm.pivot_table(values='Opening Balance', index=['Account Name', 'Cash Title', 'Concat'], aggfunc='sum')
        data_df_cm = data_df_cm.pivot_table(values='Opening Balance', index=['Account Name', 'Cash Title', 'Concat'], aggfunc='sum')
        data_df_pm = data_df_pm.reset_index(drop=False)
        data_df_cm = data_df_cm.reset_index(drop=False)        
        
        cm_concat = list(data_df_cm['Concat'].values)
        
        curr_concats = list(ledger_map['ABN Map'].values)

        diff_concat = [i for i in cm_concat if i not in curr_concats]
        
        data_df_cm_diffs = data_df_cm[data_df_cm['Concat'].isin(diff_concat)].copy()
        data_df_cm_diffs = data_df_cm_diffs.drop(columns='Opening Balance')
        ledger_map_additions = self.input_new_ledger_mappings(data_df_cm_diffs)
        
        
        ledger_map = pd.concat([ledger_map, ledger_map_additions])
        ledger_map = ledger_map.reset_index(drop=True)
        ledger_map.to_csv('C:/gdrive/Shared drives/accounting/patrick_data_files/abn_month_end/ABN_ledger_mapping.csv', index=False)
        
        pm_moyr = datetime(self.t_minus_year, self.t_minus_month, 1).strftime('%Y%m')
        cm_renamer = {'Opening Balance': self.moyr}
        pm_renamer = {'Opening Balance': pm_moyr}        
        
        data_df_cm = data_df_cm.rename(columns=cm_renamer)
        data_df_pm = data_df_pm.rename(columns=pm_renamer)
        
        data_df = ledger_map.merge(data_df_pm, how='left', left_on='ABN Map', right_on='Concat')
        # AccountID, CashDescription, ABN Map, Simplex Map, Account Name, Cash Title, pm_moyr, Concat
        data_df[['Account Name', 'Cash Title']] = data_df[['Account Name', 'Cash Title']].fillna('no match')
        # Validating merge
        for i, row in data_df.iterrows():
            if row['AccountID'] == row['Account Name'] and row['CashDescription'] == row['Cash Title']:
                continue
            elif row['Account Name'] == 'no match' or row['Cash Title'] == 'no match':
                continue
            else:
                print(f'Bad Match\n\t{row['AccountID']} // {row['Account Name']} dtype({type(row['Account Name'])})')
                print(f'\t{row['CashDescription']} // {row['Cash Title']} dtype({type(row['Cash Title'])})')
                
        data_df = data_df.drop(columns=['Account Name', 'Cash Title', 'Concat'])
        
        data_df = data_df.merge(data_df_cm, how='left', left_on='ABN Map', right_on='Concat')
        data_df[['Account Name', 'Cash Title']] = data_df[['Account Name', 'Cash Title']].fillna('no match')
        # Validating merge
        for i, row in data_df.iterrows():
            if row['AccountID'] == row['Account Name'] and row['CashDescription'] == row['Cash Title']:
                continue
            elif row['Account Name'] == 'no match' or row['Cash Title'] == 'no match':
                continue
            else:
                print(f'Bad Match\n\t{row['AccountID']} // {row['Account Name']} dtype({type(row['Account Name'])})')
                print(f'\t{row['CashDescription']} // {row['Cash Title']} dtype({type(row['Cash Title'])})')
        
        data_df = data_df.drop(columns=['Account Name', 'Cash Title', 'Concat'])
        
        both_na_index = data_df[(data_df[pm_moyr].isna()) & (data_df[self.moyr].isna())].index
        data_df = data_df.drop(both_na_index)
        
        data_df[[pm_moyr, self.moyr]] = data_df[[pm_moyr, self.moyr]].fillna(0)
        data_df[pm_moyr] = data_df[pm_moyr].mask(data_df['CashDescription'].str.contains('margin', flags=re.IGNORECASE), 0)
        data_df[self.moyr] = data_df[self.moyr].mask(data_df['CashDescription'].str.contains('margin', flags=re.IGNORECASE), 0)
        
        data_df['Change'] = data_df[self.moyr] - data_df[pm_moyr]
        
        data_df = data_df.merge(account_map, 'left', left_on='AccountID', right_on='ACCOUNT')
        data_df = data_df.drop(columns=['ACCOUNT', 'Description'])
        
        data_df = data_df[['AccountID', 'CashDescription', self.moyr, pm_moyr, 'Change', 'Strategy', 'Simplex Map', 'ABN Map']]
        
        data_df_renamer = {
            'Simplex Map': 'Mapping',
            'ABN Map': 'Concatenation',
            self.moyr: datetime.strptime(self.moyr + '01', '%Y%m%d').strftime('%b %Y\t'),
            pm_moyr: datetime.strptime(pm_moyr + '01', '%Y%m%d').strftime('%b %Y\t')
        }
        data_df = data_df.rename(columns=data_df_renamer)
        
        return data_df
        
    def input_new_ledger_mappings(self, diffs_df:pd.DataFrame):
        diffs_df_new = []
        for i, row in diffs_df.iterrows():
            print(f'{row.iloc[0]} // {row.iloc[1]}')
            print('Input new ledger mapping:')
            new_mapping = input('>\t')
            
            diffs_df_new.append(new_mapping)
        
        diffs_df['Ledger Mapping'] = diffs_df_new
        renamer = {'Account Name': 'AccountID', 'Cash Title': 'CashDescription', 'Concat': 'ABN Map', 'Ledger Mapping': 'Simplex Map'}
        
        diffs_df = diffs_df.rename(columns=renamer)
        input('\n\nClose ledger mapping file if open, enter to continue')
        
        return diffs_df
    
    def positions_tab(self, cm_positions: pd.DataFrame):
        cm_positions['Unique Name'] = ''
        cm_positions[['Strike Price', 'Expiry Date']] = cm_positions[['Strike Price', 'Expiry Date']].fillna(0)
        cm_positions['Put Call'] = cm_positions['Put Call'].fillna('')
        cm_positions['Strike Price'] = cm_positions['Strike Price'].astype(float)
        cm_positions['Expiry Date'] = cm_positions['Expiry Date'].astype(int)
        cm_positions[['Expiry Date', 'Put Call', 'Strike Price']] = cm_positions[['Expiry Date', 'Put Call', 'Strike Price']].fillna('')
        
        un_col_no = list(cm_positions.columns.values).index('Unique Name')
        
        for i, row in cm_positions.iterrows():
            unique_name = self.create_unique_name(row)

            cm_positions.iloc[[i], [un_col_no]] = unique_name
        
        pos_pivot = cm_positions.pivot_table(values=['Mark To Market Value', 'OTE'], index='Unique Name', aggfunc='sum')
        pos_pivot = pos_pivot.reset_index(drop=False)
        pos_pivot[['Mark To Market Value', 'OTE']] = pos_pivot[['Mark To Market Value', 'OTE']].fillna(0)
        
        ## Categorizing
        pos_pivot[['Asset Class', 'Futures', 'Long/Short', 'Category']] = ''
        
        pos_pivot['Asset Class'] = pos_pivot['Asset Class'].mask(pos_pivot['OTE'] != 0, 'OTE')
        pos_pivot['Futures'] = pos_pivot['Futures'].mask((pos_pivot['OTE'] == 0) & (pos_pivot['Unique Name'].str.contains('Futures')), 'Futures')
        pos_pivot['Asset Class'] = pos_pivot['Asset Class'].mask((pos_pivot['OTE'] == 0) & (pos_pivot['Unique Name'].str.contains('Put|Call', flags=re.IGNORECASE)), 'Option')
        
        stock_mask = (pos_pivot['OTE'] != 0) | (pos_pivot['Unique Name'].str.contains('Futures|Put|Call', flags=re.IGNORECASE))
        pos_pivot['Asset Class'] = pos_pivot['Asset Class'].where(stock_mask, 'Stock')
        
        pos_pivot['Long/Short'] = pos_pivot['Long/Short'].mask((pos_pivot['OTE'] == 0) & (pos_pivot['Mark To Market Value'] > 0), 'Long')
        pos_pivot['Long/Short'] = pos_pivot['Long/Short'].mask((pos_pivot['OTE'] == 0) & (pos_pivot['Mark To Market Value'] < 0), 'Short')
        
        pos_pivot[['Asset Class', 'Long/Short', 'Futures']] = pos_pivot[['Asset Class', 'Long/Short', 'Futures']].fillna('')
        
        pos_pivot['Category'] = pos_pivot['Category'].mask(pos_pivot['Asset Class'] == 'OTE', pos_pivot['Asset Class'])
        
        pos_pivot['Category'] = pos_pivot['Category'].where((pos_pivot['Asset Class'] == 'OTE') & (pos_pivot['Futures'] == 'Futures'), pos_pivot['Long/Short'] + ' ' + pos_pivot['Asset Class'])
        pos_pivot['Category'] = pos_pivot['Category'].where((pos_pivot['Asset Class'] == 'OTE') & (pos_pivot['Futures'] != 'Futures'), pos_pivot['Long/Short'] + ' ' + pos_pivot['Futures'] + ' ' + pos_pivot['Asset Class'])
        
        pos_pivot['Total Value'] = pos_pivot['Mark To Market Value'] + pos_pivot['OTE']
        
        pivot_by_category = pos_pivot.pivot_table(values = 'Total Value', index = 'Category', aggfunc = 'sum')
        pivot_by_category = pivot_by_category.reset_index(drop=False)
        pivot_by_category = pivot_by_category.fillna(0)
        pivot_by_category = pivot_by_category.drop(pivot_by_category[pivot_by_category['Total Value']==0].index)
        
        return (cm_positions, pos_pivot, pivot_by_category)
        
    def create_unique_name(self, pos_df_row):
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
        
        
    def grab_files(self, year, month):
        if self.t_minus_month == 12 and month == 12:
            ## NEED TO DO EOY FILES
            file_grabber = AbnFileGrabber(year, month)
            position = file_grabber.main()[1]
            csv_cash = AbnFileGrabber(year, 12).AbnEoyFile()
        else:
            file_grabber = AbnFileGrabber(year, month)
            csv_cash, position = file_grabber.main()

        
        return (csv_cash, position)
        
    def run_cash(self, year, month):
        cash_files = AbnCash(year, month, self.trading_path + '/' + self.moyr)
        eqt_data, mics_data = cash_files.main()
        
        return (eqt_data, mics_data)
        
    def get_mapping_files(self, google_drive_root='C:/gdrive'):
        abn_files_path = google_drive_root + '/Shared drives/accounting/patrick_data_files/abn_month_end'
        ledger_mapping = pd.read_csv(abn_files_path + '/ABN_ledger_mapping.csv')
        account_mapping = pd.read_csv(abn_files_path + '/ABN_account_mapping.csv')

        return (ledger_mapping, account_mapping)
    
    def interest_data(self, t_plus_eqt: pd.DataFrame, t_plus_mics: pd.DataFrame):
        phrases = ['AB INT', 'SHORT STOCK', 'HAIRCUT', 'FUT CAP INT']
        mask = '|'.join(phrases)
        
        eqt_int = t_plus_eqt[t_plus_eqt['Description'].str.contains(mask)]
        mics_int = t_plus_mics[t_plus_mics['Description'].str.contains(mask)]
        
        eqt_int = eqt_int[['DateEntered', 'Account', 'Amount', 'Description']]
        mics_int = mics_int[['DateEntered', 'Account', 'Amount', 'Description']]

        all_int = pd.concat([eqt_int, mics_int])
        
        return all_int
    
    def misc_breakdown(self, year, month):
        df = self.run_cash(year, month)[0]
        
        return df.loc[df['LedgerNumber'] == 8200].copy()