import pypdf, re
import pandas as pd
from datetime import datetime

def BamlReader2(f_path: str):
    f = pypdf.PdfReader(f_path)

    # Get pages with money line data
    num_pages = len(f.pages)
    
    account_lines = []
    
    account_pattern = r'644-\d{5}-D\d'

    for page_num in range(num_pages):
        reader = f.pages[page_num]
        text_lines = reader.extract_text().split('\n')
        for line in text_lines:
            if re.search(account_pattern, line):
                account_lines.append(line)
    
    # Debug
    # for i in account_lines:
    #     print(i)
    # input()
    
    # Clean data of extra spaces, convert numbers to proper format, recombine lines
    
    # Substitute out spaces from each line and replace with delimiter //
    no_space_needed_lines = [re.subn(r'\s{2,}', '//', line)[0] for line in account_lines]
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
    
    # # Debug
    # for i in new_lines:
    #     print(i)
    # input()
    
    # Convert data to df
    headers = [
        'Account No.',
        'Account Name',
        'SD Bal',
        'TD Bal',
        'TD Opt Val',
        'TD STK/BD Val',
        'Equity'
    ]
    
    data = {i: [] for i in headers}

    for i in range(1, len(new_lines)):
        for j in range(len(headers)):
            data[headers[j]].append(new_lines[i][j])

    # print(data)
    
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
    
    # print("Equities")
    # print(files[0])
    # print("\n\n Futures")
    # print(files[1])
    # input()

    return files

def EtMonthEnd(year, month):
    yrmo = datetime(year=year,month=month,day=1).strftime('%Y%m')
    path = f'C:/gdrive/My Drive/ET Payout Reports/{yrmo} - ET Payout Traders Report.xlsx'
    file = pd.read_excel(path, 'Transfer Check')
    file = file.fillna(0)
    # new_headers = file.iloc[0].to_list()
    # renamer = {old: new for old, new in zip(file.columns.to_list(), new_headers)}
    # file = file.rename(columns=renamer).drop(index=0).reset_index(drop=True)
    
    totals_i = file.loc[file['Account'] == 'Totals'].index[0]
    drop_index = file.iloc[totals_i:].index
    file = file.drop(index=drop_index).reset_index(drop=True)
    file = file.drop(index=file.loc[file['Transfer'] == 0].index).reset_index(drop=True)

    return file
