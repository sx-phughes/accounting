###############################################################################
# DEPRECATED ##################################################################
###############################################################################

# Standard imports
import os
import re
from datetime import datetime

exchanges = ['ZO', 'XO', 'C1', 'C2']
mpidsByExchange = {exch: [] for exch in exchanges}

def get_old_mpids(curr_year, curr_month):
    monthYears = moYrsToSearch(curr_year, curr_month)

    for moyr in moyrs_to_search:
        files = searchMonthYear(moyr)
        for f in files: 
            checkFile(f)

    return exchanges 

def searchMonthYear(monthYear):
    searchPath = f'C:/gdrive/Shared drives/accounting/Simplex Trading/2025/\
                  Exchange Fees/{monthYear}/Prelim'
    
    files = os.listdir(searchPath)

    return files

def checkFile(fileToCheck):
    file_pattern = r'([A-Z]{4})\d{4}a?-([ZO|XO|C1|C2])\.csv'
    match = re.match(filePattern, fileToCheck)
    if match:
        updateMpids(match)

def updateMpids(match)
    mpid = match.group(1)
    exchange = match.group(2)
    mpidsByExchange[exchange].append(mpid)

def moYrsToSearch(curr_year, curr_month):
    months = monthsToGet(curr_month)
    monthYears = [datetime(curr_year, month, 1).strftime('%Y%m') for month in
                  months]
    return monthYears

def monthsToGet(curr_month):
    return range(1,13)[:(curr_month - 1)]
