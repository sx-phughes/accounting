"""Module containing classes to move and process BofA end-of-month files for 
the monthly close
"""

# Standard imports
import os
import shutil
import re
import pandas as pd
from datetime import datetime

# Package imports
from MonthEnd.Bofa import comb_headers 

class BAMLFileMover:
    save_path = 'C:/gdrive/Shared drives/accounting/Simplex Trading'
    search_path = 'C:/gdrive/Shared drives/Clearing Archive/BOFA_Archive'
    
    def __init__(self, year: int, month: int):
        """Initializes BAMLFileMover object

        Creates path values for processing activity at BofA and creates
        necessary directories
        """
        self.year = year
        self.month = month
        self.ym_folder = datetime(self.year, self.month, 1).strftime('%Y%m')
        self.bofa_folder = BAMLFileMover.save_path \
                   + '/' \
                   + str(self.year) \
                   + '/BOFA/' \
                   + self.ym_folder
        
        stems_to_check = [
            f'/{str(self.year)}/BOFA/{self.ym_folder}/HCFiles',
            f'/{str(self.year)}/BOFA/{self.ym_folder}/Files',
            f'/{str(self.year)}/BOFA/{self.ym_folder}/DivFiles'
        ]
        
        for i in stems_to_check:
            if os.path.exists(BAMLFileMover.save_path + i):
                continue
            else:
                os.makedirs(BAMLFileMover.save_path + i)
        
        all_folders = os.listdir(BAMLFileMover.search_path)
        self.folders = list(filter(lambda x: self.ym_folder in x, all_folders))
        
    def main(self):
        """function to run full month-end process"""
        self.getFileNames()
        self.copyFiles()
        self.process_hc()
        self.process_bookkeeping()
        self.process_comb()
        self.process_gl()
        
    def just_div_files(self):
        """function to run only dividend detail files"""
        self.getFileNames()
        self.copyFiles()
        self.process_bookkeeping()
    
    def getFileNames(self):
        """Gets all data file names for given month"""
        patterns = [
           ['WSB806TZ.COMBFI26.CSV.{date}', '%Y%m%d', 'comb'], 
           ['644.644.RBH_SUM_CSV.{date}.csv', '%Y.%m.%d', 'hc'], 
           ['WSB863TW.CST478BK.CSV.{date}', '%Y%m%d', 'div']
        ]
        
        self.hc_files: list[str] = []
        self.div_files: list[str] = []
        self.comb_files: list[str] = []
        
        for i in self.folders:
            for j in patterns:
                f_date = datetime.strptime(i, '%Y%m%d')
                formatted_file_name = j[0].format(date=f_date.strftime(j[1]))
                full_file_path = BAMLFileMover.search_path \
                           + f'/{i}/{formatted_file_name}'
                
                if j[2] == 'comb':
                    self.comb_files.append(full_file_path)
                elif j[2] == 'hc':
                    self.hc_files.append(full_file_path)
                elif j[2] == 'div':
                    self.div_files.append(full_file_path)
                    
        
                    
    def copyFiles(self):
        """Copies data files to BofA working directories"""
        files_list: list[list[list[str] | str]]= [
            [self.hc_files, 'HCFiles', ''],
            [self.div_files, 'DivFiles', '.csv'],
            [self.comb_files, 'Files', '.csv']
        ]
        
        
        for i in files_list:
            old_paths = i[0]
            dest_folder = i[1]
            suffix = str(i[2])
            new_paths: list[str] = []
            
            for j in old_paths:
                f_name = str(j).split('/')[-1]
                new_name = f_name + suffix
                new_path = self.bofa_folder + f'/{dest_folder}/{new_name}'
                new_paths.append(new_path)
            
            for j in list(zip(old_paths, new_paths)):
                try:
                    shutil.copyfile(j[0], j[1])
                except FileNotFoundError:
                    continue
                
    def process_comb(self):
        """Process daily comb files for daily fee values"""
        files = os.listdir(self.bofa_folder + '/Files')
        files_with_path = [self.bofa_folder + '/Files/' + i for i in files]
        
        use_columns = [
            'Account',
            'E1Y Exec. Fees - Stocks',
            'E1Y Exec. Fees - Options',
            'E1Y SEC Fees Stocks',
            'E1Y SEC Fees Options',
            'OCC Fees',
            'Business Date'
        ]
        summary_df = pd.DataFrame(columns=use_columns)
        
        for file in files_with_path:
            df = pd.read_csv(file, names=comb_headers.headers)

            df = df[use_columns]
            
            summary_df = pd.concat([summary_df, df])
            
        summary_df.to_csv(self.bofa_folder + '/Fees_Table.csv',index=False)
    
    def process_hc(self):
        """Process daily haircut files to a monthly summary table"""
        files = os.listdir(self.bofa_folder + '/HCFiles')
        files_with_path = [self.bofa_folder + '/HCFiles/' + i for i in files]
        
        hc_summary = pd.DataFrame(columns = ['Date', 'HC Prop'])
        
        for file in files_with_path:
            df = pd.read_csv(file)
            df = df[
               (df['Category'] == 'Gross Haircuts') 
               & (df['AccountType'] == 'Proprietary')
            ]

            df = df.reset_index()
            
            if len(df) == 0:
                pattern = r'[\d]{4}.[\d]{2}.[\d]{2}'
                date = re.search(pattern, file).string
                formatted_date = datetime.strptime(date, '%Y.%m.%d')
                
                new_row = [formatted_date, 0]
            else:
                date = df['RunDate'].loc[0]
                rbh = df['OffsetGroup'].sum()
                
                new_row = [date, rbh]
                
            hc_summary.loc[len(hc_summary.index)] = new_row 
            
        hc_summary.to_csv(self.bofa_folder + '/HC_Table.csv', index=False)
        
    def process_gl(self):
        """Creates table for tracking GL changes for use in month-end workflow

        GL changes include daily PL change, GL change, and equity
        """
        files = os.listdir(self.bofa_folder + '/Files')
        files_with_path = [self.bofa_folder + '/Files/' + i for i in files]
        
        use_cols = [
            'Account',
            'PL Change',
            'GL Change',
            'Todays Equity',
            'Business Date'
        ]
        
        gl_summary = pd.DataFrame(columns = use_cols)
        
        for file in files_with_path:
            df = pd.read_csv(file,names=comb_headers.headers)
            
            df = df[use_cols]
            
            gl_summary = pd.concat([gl_summary, df])
            
        gl_summary.to_csv(self.bofa_folder + '/GL_Table.csv')
        
    def process_bookkeeping(self):
        """Processes bookkeeping for month-end workflow
        
        GL Detail files for mapping short stock interest, assessed balance 
        interest, pm exchange fees, transfers, and other ledger entries to 
        appropriate accounts.

        Dividend process creates dividend summary table for use in month-end
        workflows as well as a full dividend detail for audit purposes
        """
        files = os.listdir(self.bofa_folder + f'/DivFiles')
        files_with_path = [self.bofa_folder + f'/DivFiles/' + i for i in files]
        
        # GL Detail Table for use in month-end spreadsheet
        gl_detail = pd.DataFrame(columns=comb_headers.div_headers)

        # Dividend table for use in month-end process
        div_sum_df = pd.DataFrame(
           columns=[
                'Date',
                'Divs Received',
                'Divs Paid',
                'Divs ReceivedMM',
                'Divs PaidMM'
            ]
        )

        # Dividend table with full detail
        all_div_df = pd.DataFrame(columns=comb_headers.div_headers)
        
        for file in files_with_path:
            df = pd.read_csv(
                file, 
                names=comb_headers.div_headers, 
                low_memory=False
            )
            gl_detail = self.get_gl_details(df, gl_detail)
            all_div_df = self.get_div_detail(df, all_div_df)
            div_sum_df = self.get_div_summary(df, div_sum_df)

        # Saves full month summary files to disk
        gl_detail.to_csv(
            self.bofa_folder + '/GL_Detail_Table.csv', 
            index=False
        )
        div_sum_df.to_csv(
            self.bofa_folder + '/Dividends_Table.csv', 
            index=False
        )
        all_div_df.to_csv(
            self.bofa_folder 
            + f'/Full_Div_Summary_{str(self.year)}'
            + f'{str(self.month)}.csv',
            index=False
        )
        
    def get_gl_details(self, i_df, gl_det_df):
        """concats daily GL activity to monthly summary table for use in
        month-end workflow"""
        gl_det_i = i_df.loc[i_df['Type of Entry'].isin([
                                                    'INTE',
                                                    'FSD', 
                                                    'WCK', 
                                                    'FPE',
                                                    'GJE', 
                                                    'JE', 
                                                    'INTI'
                                                ])].copy()
        
        gl_det_df = self.concat_empty_dfs(gl_det_i, gl_det_df)
        
        return gl_det_df

    def get_div_detail(self, i_df, div_detail_df):
        """concats daily dividend detail file to monthly dividend summary
        table"""
        div_df = i_df[
            (i_df['Origin Code'] != 'DIVP') 
            & (i_df['Origin Code'] == 'DV')
        ].copy()
        
        div_detail_df = self.concat_empty_dfs(div_df, div_detail_df)

        return div_detail_df 

    def get_div_summary(self, i_df, div_summary_df):
        """concats daily dividend summary data from daily table to monthly
        summary table for use in month-end workflow
        """
        div_df = i_df[
            (i_df['Origin Code'] != 'DIVP') 
            & (i_df['Origin Code'] == 'DV')
        ].copy()
        date = i_df['Business Date'].loc[0]

        acct_type = {
            1: 'prop',
            2: 'mm'
        }
        pl_type = {
            3: 'inc',
            4: 'exp'
        }
        data = {i * j: '' for i in acct_type for j in pl_type } 

        for i in range(1,3):
            for j in range(3,5):
                if i ==1:
                    acct_mask = (div_df['Account #'] == '64498315D3')
                else:
                    acct_mask = (div_df['Account #'] == '64440300D4')

                if j == 3:
                    val_mask = (div_df['Amount'] > 0)
                else:
                    val_mask = (div_df['Amount'] < 0)

                ij_total = div_df.loc[(acct_mask) & (val_mask), 'Amount'].sum()
                data[i*j] = ij_total

        new_row = [date] + [data[key] for key in data.keys()]
        print(new_row)
        div_summary_df.loc[len(div_summary_df.index)] = new_row 
        return div_summary_df

    def concat_empty_dfs(self, i_df, main_df):
        """function to concatenate a componenent dataframe to a cumulative
        dataframe when one or both may be empty
        """
        if not i_df.empty and not main_df.empty:
            main_df = pd.concat([main_df, i_df])
        elif not i_df.empty and main_df.empty:
            main_df = i_df.copy()
        
        return main_df


# Wrapper functions for script manager

def file_mover_wrapper(year: int, month: int):
    mver = BAMLFileMover(year, month)
    mver.main()
    
def div_file_wrapper(year: int, month: int) -> None:
    mver = BAMLFileMover(year, month)
    mver.div_files()
