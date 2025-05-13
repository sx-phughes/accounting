import os
import pandas as pd
import re
import pypdf
from MonthEnd.Abn.Base import get_archive_date_path
from MonthEnd.Abn.EoyExtractPageText import *

def convert_to_eoy_cash(year: int, pm_cash: pd.DataFrame):
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

    dir = get_archive_date_path(day=31)

    f_pattern = r'[\w_\d]*DPR_SU_EOY.pdf'

    proper_files = get_ABN_pdfs(year, 12, f_pattern)

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
    csv_cash = pm_cash
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

def get_ABN_pdfs( f_pattern):
    dir_path = get_archive_date_path()

    files = os.listdir(dir_path)

    proper_files = list(filter(lambda x: re.search(f_pattern, x), files))

    return proper_files