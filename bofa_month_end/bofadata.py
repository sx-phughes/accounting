import os
import pandas as pd
from itertools import *
from comb_headers import comb_headers
from div_headers import div_headers

archive = 'C:/gdrive/Shared drives/Clearing Archive/BOFA_Archive'

comb = 'WSB806TZ.COMBFI26.CSV.{date}'
div = 'WSB863TW.CST478BK.CSV.{date}'
hc = '644.644.RBH_SUM_CSV.{date}.csv'

class BOFAData(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
        
    def get_data(self):
        self.get_directories()
        self.get_combfiles()
        self.get_divfiles()
        self.get_hc_data()
    
    def date_to_path(self, date_str: str):
        parts = date_str.split('-')
        year = parts[0]
        month = parts[1]
        day = parts[2]
        
        return year + month + day
    
    def date_to_hc_date(date_str: str):
        year = date_str[:4]
        month = date_str[4:6]
        day = date_str[6:]
        
        return '.'.join([year, month, day])
    
    def get_directories(self):
        folders = os.listdir(archive)
        
        curr_month_folders = list(filter(lambda x: x[:6] == self.date_to_path(self.start)[:6]))
        
        curr_month_folders = sorted(curr_month_folders)
        self.curr_directories = curr_month_folders
        
    def get_combfiles(self):
        comb_file_paths = []
        for i in self.curr_directories:
            f_name = comb.format(date=i)
            full_path = archive + '/' + i + '/' + f_name
            comb_file_paths.append(full_path)
        self.comb_paths = comb_file_paths
        
        comb_data = pd.read_csv(archive + '/' + self.curr_directories[-1] + '/' + comb.format(date=self.curr_directories[-1]))
        
        main_fee_df = pd.DataFrame()
        
        for i in comb_file_paths:
            temp_df_headers = pd.DataFrame(columns=comb_headers)
            temp_df = pd.read_csv(i)
            
            temp_df = pd.concat([temp_df_headers, temp_df])
            temp_df = temp_df[['Account', 'E1Y Exec. Fees - Stocks', 'E1Y Exec. Fees - Options', 'E1Y SEC Fees Stocks ', 'E1Y SEC Fees Options', 'OCC Fees', 'Business Date ']]
            
            main_fee_df = pd.concat([main_fee_df, temp_df])
        
        self.comb_data = comb_data
        self.fees_df = main_fee_df
            
    def get_divfiles(self):
        div_file_paths = []
        for i in self.curr_directories:
            f_name = div.format(date=i)
            full_path = archive + '/' + '/' + f_name
            div_file_paths.append(full_path)
        
        summary_data = {'Date': [],
                        'Divs Received': [],
                        'Divs Paid': [],
                        'Divs ReceivedMM': [],
                        'Divs PaidMM': []}
        
        combined_dfs = pd.DataFrame()
        for i in div_file_paths:
            # Transaction Category --> Origin Code
            # Dividend Type --> Type of Entry
            # BAML Account --> Account #

            main_df_w_headers = pd.DataFrame(columns=div_headers)
            main_df = pd.read_csv(i)
            main_w_data_and_headers = pd.concat([main_df_w_headers, main_df])
            main_just_dv = main_w_data_and_headers.loc[main_w_data_and_headers['Origin Code'] == 'DV']
            
            combined_dfs = pd.concat([combined_dfs, main_just_dv])
            
            file_name = str.split(i, '/')[-1]
            file_date = file_name.split('.')[-1]
            
            divs_received = main_just_dv.loc[(main_just_dv['Amount'] > 0) & (main_just_dv['Type of Entry'] != 'DIVP') & (main_just_dv['Account #'] == '64498315D3'), 'Amount'].sum().value
            divs_paid = main_just_dv.loc[(main_just_dv['Amount'] < 0) & (main_just_dv['Type of Entry'] != 'DIVP') & (main_just_dv['Account #'] == '64498315D3'), 'Amount'].sum().value
            divs_received_MM = main_just_dv.loc[(main_just_dv['Amount'] > 0) & (main_just_dv['Type of Entry'] != 'DIVP') & (main_just_dv['Account #'] == '64440300D4'), 'Amount'].sum().value
            divs_paid_MM = main_just_dv.loc[(main_just_dv['Amount'] < 0) & (main_just_dv['Type of Entry'] != 'DIVP') & (main_just_dv['Account #'] == '64440300D4'), 'Amount'].sum().value
            
            summary_data['Date'].append(file_date)
            summary_data['Divs Received'].append(divs_received)
            summary_data['Divs Paid'].append(divs_paid)
            summary_data['Divs ReceivedMM'].append(divs_received_MM)
            summary_data['Divs PaidMM'].append(divs_paid_MM)

        fee_summary = pd.DataFrame(summary_data)
        self.fee_summary = fee_summary
        
        gl_detail_df = combined_dfs.loc[combined_dfs['Type of Entry'].isin(['GJE', 'JE', 'INTI', 'FPE', 'FSD', 'WCK', 'INTE'])]
        self.gl_detail_df = gl_detail_df
        
    def get_gldata(self):
        headers_df = pd.DataFrame(columns=comb_headers)
        
        main_df = pd.DataFrame()
        for i in self.comb_paths: 
            main_temp = pd.read_csv(i)
            temp_df = pd.concat([headers_df, main_temp])
            temp_df = temp_df[['Account', 'PL Change', 'GL Change', 'Todays Equity', 'Business Date ']]
            
            main_df = pd.concat([main_df, temp_df])
            
        self.gl_summary = main_df
        
    def get_hc_data(self):
        summary_data = {'Date': [],
                        'RBH Haircut': []}
        for i in self.curr_directories:
            hc_date = self.date_to_hc_date(i)
            f_name = hc.format(date=hc_date)
            full_path = archive + '/' + i + '/' + f_name
            temp_df = pd.read_csv(full_path)
            
            rbh = temp_df.loc[(temp_df['Category'] == 'Gross Haircuts') & (temp_df['AccountType'] == 'Proprietary'), 'OffsetGroup'].sum().value
            
            summary_data['Date'].append(f_name)
            summary_data['RBH Haircut'].append(rbh)
            
        summary_df = pd.DataFrame(summary_data)
        self.hc_data = summary_df