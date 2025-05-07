from patrick_functions.DateFunctions import last_biz_day
from zipfile import ZipFile
import pandas as pd
from MonthEnd.Abn.AbnBase import AbnBase
import re, pypdf, os
from MonthEnd.Abn.EoyExtractPageText import *
from datetime import datetime

## Files Needed ##
#   1. yyyymmdd-2518-C2518-CSVCASH_AC.csv.zip
#   2. yyyymmdd-2518-C2518-POSITION.csv.zip


class MonthlyStatement:
    index = {}

    def __init__(self, path, file_name):
        self.path = path
        self.fname = file_name

    def __str__(self):
        return self.fname

    @property
    def account(self):
        return self._account
    
    @account.setter
    def account(self, account):
        MonthlyStatement.index.update({account: self})
        self._account = account
    
    @property
    def date(self):
        return self._date
    
    @date.setter
    def date(self, date):
        self._date = datetime.strptime(date, '%Y%m%d')  

    @property
    def margin(self):
        return self._margin
    
    @margin.setter
    def margin(self, margin):
        self._margin = margin

    @property
    def abn_num(self):
        return self._abn_num
    
    @abn_num.setter
    def abn_num(self, num):
        self._abn_num = num



class AbnFileGrabber(AbnBase):
    def __init__(self, year, month):
        super().__init__(year, month)
        
        self.last_biz_day = last_biz_day(year, month)
        # self.moyr = self.last_biz_day.strftime('%Y%m')
        self.date_str = self.last_biz_day.strftime('%Y%m%d')
        
    def main(self):
        self.get_file_dirs()
        self.unzip()
        
        return (pd.read_csv(self.csvcash, low_memory=False), pd.read_csv(self.position, low_memory=False))
    
    def get_file_dirs(self):
        self.csvcash_name = f'{self.date_str}-2518-C2518-CSVCASH_AC.csv.zip'
        self.position_name = f'{self.date_str}-2518-C2518-POSITION.csv.zip'
        
        self.csvcash_zip = self.archive_path + f'/{self.date_str}/{self.csvcash_name}'
        self.position_zip = self.archive_path + f'/{self.date_str}/{self.position_name}'

    def unzip(self):
        paths_list = [[self.csvcash_zip, self.csvcash_zip.split('/')[-1].replace('.zip', ''), self.trading_path + '/' + self.moyr],
                      [self.position_zip, self.position_zip.split('/')[-1].replace('.zip', ''), self.trading_path  + '/' + self.moyr]]
        
        
        for i in paths_list:
            with ZipFile(i[0], 'r') as zip:
                zip.extract(i[1], i[2])
                
        self.csvcash = paths_list[0][2] + '/' + paths_list[0][1]
        self.position = paths_list[1][2] + '/' + paths_list[1][1]

    def archive_date_path(self, day=0):
        if day == 0:
            date_str = last_biz_day(self.year, self.month).strftime('%Y%m%d')
        else:
            date_str = datetime(self.year, self.month, day).strftime('%Y%m%d')

        dir_path = self.archive_path + '/' + date_str

        return dir_path
    
    def get_ABN_pdfs(self, f_pattern):
        dir_path = self.archive_date_path()

        files = os.listdir(dir_path)

        proper_files = list(filter(lambda x: re.search(f_pattern, x), files))

        return proper_files

    def get_account_file_mapping(self):

        dir_path = self.archive_date_path()
        
        f_pattern = r'[\w_\d]*([A-Z]{4})\_(\d{10})_DPR_SU.pdf'
        
        proper_files = self.get_ABN_pdfs(f_pattern)
        
        os.chdir(dir_path)

        account_file_mapping = {}

        count = 0

        for f in proper_files:
            count += 1
            pdf = pypdf.PdfReader(f)
            first_page = pdf.pages[0]
            
            account_name = get_account_name(first_page)
            
            search = re.search(f_pattern, f)
            account_type = search.group(1)
            file_map_i = re.search(f_pattern, f).group(2)

            print(f'{count}: {account_type} account {account_name} has file index {file_map_i}')

            account_file_mapping.update({account_name: [account_type, file_map_i]})
        
        return account_file_mapping
    
    def get_abn_pdf_monthly_statement(self, account, account_file_mapping):
            dir_path = self.archive_date_path()

            f_pattern = rf'[\w_\d]*{account_file_mapping[account][0]}\_{account_file_mapping[account][1]}_DPR_SU.pdf'

            try:
                f_name = list(filter(lambda f_name: re.search(f_pattern, f_name), os.listdir(dir_path)))[0]
            except:
                f_name = ''

            return (dir_path, f_name)
    
    def AbnEoyFile(self):
        ##### PROCESS NOTES #####
        # MARK TO MARKET OPTIONS LONG/SHORT ARE NETTED TO MARK TO MARKET OPTIONS
        # MARK TO MARKET UNSETTLED LONG/SHORT STOCK ARE NETTED TO MARK TO MARKET UNSETTLED STOCK
        # MARK TO MARKET UNSETTLED LONG/SHORT PREFSTOCK ARE NETTED TO MARK TO MARKET UNSETTLED PREFSTOCK
        #   ADD PRIOR VALUES FOR THESE TO THE RESULTING FILE AND ZERO OUT THE NETTED CATEGORIES
        #
        # GROSS PROFIT OR LOSS IS A FUTURES ONLY CATEGORY AND IS NETTED INTO BALANCE PREVIOUS YEAR
        #   THIS CAN STAY UNTOUCHED
        #
        # OPEN TRADE EQUITY IS LISTED AS OPEN TRADE EQUITY FUTURES BUT STAYS THE SAME
        #   THIS NEEDS TO BE RENAMED FOR VALUES TO COME THROUGH

        dir = self.archive_date_path(day=31)

        f_pattern = r'[\w_\d]*DPR_SU_EOY.pdf'

        proper_files = self.get_ABN_pdfs(self.year, 12, f_pattern)

        os.chdir(dir)

        dfs = []
        count = 0

        for f in proper_files:
            count += 1
            pdf = pypdf.PdfReader(f)
            pages = pdf.pages
            page_nums = get_page_nos(pages)

            for num in page_nums:
                page_obj = pages[num]
                df = get_data_table(f, page_obj)
                dfs.append(df)

        summary_df = pd.concat(dfs)

        initial_line_drops = [
            'CASH POSITON',
            'NET LIQUIDATION',
            'NET PROFIT & LOSS'
        ]

        drop_index = summary_df.loc[summary_df['Cash Title'].isin(initial_line_drops)].index
        summary_df = summary_df.drop(index=drop_index).reset_index(drop=True)
        summary_df.loc[summary_df['Cash Title'].str.contains('MARGIN'), 'New'] = 0
        total_sum = summary_df['New'].sum()

        summary_df.to_csv('C:/Users/phugh/Downloads/summary_df.csv')


        ## + Formatting rules to make = to normal cash file ##
        csv_cash, position = self.main()
        csv_cash.loc[csv_cash['Cash Title'].str.contains('MARGIN'), 'Opening Balance'] = 0
        csv_cash_total = csv_cash['Opening Balance'].sum()

        ## Check 1 ##
        if round(total_sum, 0) != round(csv_cash_total, 0):
            raise ValueError('Total Sum and CSVCASH Sum are not equal', f'Total Sum: {total_sum}', f'CSVCASH Sum: {csv_cash_total}')

        line_items_to_keep = [
            'MARK TO MARKET OPTIONS LONG',
            'MARK TO MARKET OPTIONS SHORT',
            'MARK TO MARKET UNSETTLED LONG STOCK',
            'MARK TO MARKET UNSETTLED SHORT STOCK',
            'MARK TO MARKET UNSETTLED LONG PREFSTOCK',
            'MARK TO MARKET UNSETTLED SHORT PREFSTOCK'
        ]

        mark_to_market = csv_cash.loc[csv_cash['Cash Title'].isin(line_items_to_keep)].copy()
        mark_to_market = mark_to_market[['Account', 'Cash Title', 'Opening Balance']]
        mark_to_market = mark_to_market.rename(columns={'Opening Balance', 'New'})
        mark_to_market['Change'] = 0
        mark_to_market['Old'] = mark_to_market['New']
        mark_to_market['Month to Date'] = 0
        mark_to_market['f_name'] = 'CSVCASH'

        line_items_to_drop = [
            'MARK TO MARKET OPTIONS',
            'MARK TO MARKET UNSETTLED STOCK',
            'MARK TO MARKET UNSETTLED PREFSTOCK'
        ]

        rows_to_drop = summary_df.loc[summary_df['Cash Title'].isin(line_items_to_drop)].index
        summary_without_net_mtm = summary_df.drop(index=rows_to_drop).copy()
        summary_with_split_mtm = pd.concat([summary_without_net_mtm, mark_to_market])

        new_summary = summary_with_split_mtm.mask(summary_with_split_mtm['Cash Title'] == 'OPEN TRADE EQUITY FUTURES', 'OPEN TRADE EQUITY')

        new_summary_final = new_summary.rename(columns={'New': 'Opening Balance'})
        final_checksum = new_summary_final['Opening Balance'].sum()

        ## Check 2 ##
        if round(csv_cash_total, 0) != round(final_checksum, 0):
            raise ValueError('Final Check Sum and CSVCASH Sum are not equal', f'Final Check Sum: {final_checksum}', f'CSVCASH Sum: {csv_cash_total}')
        

        return new_summary_final

        
            