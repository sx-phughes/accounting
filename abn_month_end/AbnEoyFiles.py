from EoyExtractPageText import get_data_table, get_page_nos
import os, re, pypdf
import pandas as pd

##### PROCESS NOTES #####
# MARK TO MARKET OPTIONS LONG/SHORT ARE NETTED TO MARK TO MARKET OPTIONS
# MARK TO MARKET UNSETTLED LONG/SHORT STOCK ARE NETTED TO MARK TO MARKET UNSETTLED STOCK
#   ADD PRIOR VALUES FOR THESE TO THE RESULTING FILE AND ZERO OUT THE NETTED CATEGORIES

# GROSS PROFIT OR LOSS IS A FUTURES ONLY CATEGORY AND IS NETTED INTO BALANCE PREVIOUS YEAR
# OPEN TRADE EQUITY IS LISTED AS OPEN TRADE EQUITY FUTURES BUT STAYS THE SAME



dir = 'C:/gdrive/Shared drives/Clearing Archive/ABN_Archive/20241231'

f_pattern = r'[\w_\d]*DPR_SU_EOY.pdf'

files = os.listdir(dir)

proper_files = filter(lambda x: re.search(f_pattern, x), files)


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

try:
    summary_df.to_csv('C:/gdrive/Shared drives/accounting/Simplex Trading/2025/ABN/EOY Cash File.csv', index=False)
except PermissionError:
    print('Close file before continuing')
    input()
finally:
    summary_df.to_csv('C:/gdrive/Shared drives/accounting/Simplex Trading/2025/ABN/EOY Cash File.csv', index=False)