import pypdf, re
import pandas as pd
from datetime import datetime

def BamlMonthEndStmtReader(f_path: str):
    f = pypdf.PdfReader(f_path)

    # Get pages with money line data
    num_pages = len(f.pages)
    moneyline_pages = {}

    for i in range(num_pages):
        reader = f.pages[i]
        if 'MONEY LINE' in reader.extract_text():
            moneyline_pages[i] = reader.extract_text()

    # Get relevant money line data from each page
    needed_lines = []

    for i in range(len(moneyline_pages.keys())):
        i_key = list(moneyline_pages.keys())[i]
        split_text = moneyline_pages[i_key]
        split_text = split_text.split('\n')

        start = 0
        end = 0
        for j in range(len(split_text)):

            if 'MONEY LINE' in split_text[j]:
                start = j + 1
            elif 'TOTAL' in split_text[j] and start != 0:
                end = j
                break
            else:
                continue
        
        for j in range(start, end):
            needed_lines.append(split_text[j])

    # Clean data of extra spaces, convert numbers to proper format, recombine lines
    
    # Substitute out spaces from each line and replace with delimiter //
    no_space_needed_lines = [re.subn(r'\s{2,}', '//', line)[0] for line in needed_lines]
    new_lines = []
    
    # Iterating through each line of text
    for i in range(len(no_space_needed_lines)):
        # Strip whitespace from lines and split by delimiter
        row_vals = no_space_needed_lines[i].strip().split('//')

        # Iterate through each value in the row
        for j in range(len(row_vals)):
            # Remove any commas
            j_val = row_vals[j].replace(',','')

            # Match negative numbers and switch negative sign spot
            if re.match(r'^\d+.\d{2}-$', j_val):
                j_val = '-' + j_val.replace('-', '')
            
            # Replace cleaned data in the row
            row_vals[j] = j_val

        # Some rows have an empty string at the end - remove this value
        if '' in row_vals:
            row_vals.remove('')
        
        # Append to clean lines list
        new_lines.append(row_vals)
    
    # Remove extra header lines
    pop_lines = []
    
    for i in range(1, len(new_lines)):
        if 'ACCOUNT' in new_lines[i][0]:
            pop_lines.append(i)

    for i in sorted(pop_lines, reverse=True):
        new_lines.pop(i)

    # Convert data to df
    headers = new_lines[0]
    data = {i: [] for i in headers}

    for i in range(1, len(new_lines)):
        for j in range(len(headers)):
            data[headers[j]].append(new_lines[i][j])

    df = pd.DataFrame(data)

    return df


def AbnMonthEndStatements(date: str):
    abn_root = f'C:/gdrive/Shared drives/Clearing Archive/ABN_Archive/{date}'
    eqt_account_path = f'/EQTBAL_{date}.csv'
    fut_file_path = f'/MICS_Bal_{date}.csv'

    files = [
        pd.read_csv(abn_root + eqt_account_path),
        pd.read_csv(abn_root + fut_file_path)
    ]

    return files

def EtMonthEnd(month, year):
    yrmo = datetime(year=year,month=month,day=1).strftime('%Y%m')
    path = f'C:/gdrive/My Drive/ET Payout Reports/{yrmo} - ET Payout Traders Report.xlsx'
    file = pd.read_excel(path, 'Transfer Check')
    file = file.fillna(0)

    return file