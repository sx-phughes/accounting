"""Module for loading QB general ledger data to new GL data"""

# Standard Imports
import pandas as pd
import numpy as np

# Package Imports
import Entry
import Ledger
import Account


def is_csv(path: str):
    if path.split('.')[-1] == 'csv':
        return True
    else:
        return False
    
def load_ledger(path: str):
    if is_csv(path):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path,pd.ExcelFile(path).sheet_names[0])

    return df

def clean_ledger(gl_df: pd.DataFrame):
    gl_df = gl_df.drop(index=gl_df.index[0:2]).reset_index(drop=True)
    
    new_col_names = gl_df.iloc[0].to_list()
    new_col_names[0] = 'Journal ID'
    old_col_names = gl_df.columns.to_list()
    
    renamer = {old: new for old, new in zip(old_col_names, new_col_names)}
    
    df = gl_df.rename(columns=renamer)
    df = df.drop(index=df.index[0]).reset_index(drop=True)
    
    id_total_rows = df[df['Journal ID'].str.match(r'Total', na=False)].index
    df = df.drop(index=id_total_rows).reset_index(drop=True)
    
    id_rows = df[df['Journal ID'].str.match(r'\d{4}', na=False)].index
    
    for i in range(len(id_rows)):
        curr_id_row = id_rows[i]
        curr_je_id = df['Journal ID'].iloc[curr_id_row]
        
        if id_rows[i] == id_rows[-1]:
            df.loc[curr_id_row:, 'Journal ID'] = curr_je_id
            continue
        
        last_curr_id_row = id_rows[i+1] - 1
        df.loc[curr_id_row:last_curr_id_row, 'Journal ID'] = curr_je_id
    
    drop_blanks = df[df['Transaction date'].str.match(r'TOTAL', na=True)].index
    df = df.drop(index=drop_blanks).reset_index(drop=True)
    
    df['Transaction date'] = df['Transaction date'].astype(str)
    df[['Month', 'Day', 'Year']] = df['Transaction date'].str.split('/', expand=True)

    return df

def get_qb_to_gl_mapping(company: str):
    path = \
    'C:/gdrive/Shared drives/accounting/patrick_data_files/new_gl/accounts.csv'
    df = pd.read_csv(path)
    co_df = df.loc[df['company'] == Account.seg1_vals[company]].copy()
    qb_accts = co_df['qb_mapping'].to_list()
    gl_accts = co_df['account'].to_list()
    mapping = {qb: gl for qb, gl in zip(qb_accts, gl_accts)}
    
    return mapping

def str_to_float(str_num):
    if isinstance(str_num, str):
        no_comma = str_num.replace(',', '')
        floated = np.float64(no_comma)
        return floated
    elif np.isnan([str_num])[0]:
        return str_num
    else:
        raise TypeError('Value is neither string nor NaN. Value: ', str_num)

def make_jes(df: pd.DataFrame, company: str):
    unique_journals = df['Journal ID'].unique().tolist()
    
    journal_objs = []
    qb_mapping = get_qb_to_gl_mapping(company)
    
    for je_id in unique_journals:
        journal = Entry.Entry()
        je_id_view = df[df['Journal ID'] == je_id]
        journal.date = np.array(
            [
                np.int64(je_id_view['Year'].iloc[0]),
                np.int64(je_id_view['Month'].iloc[0]),
                np.int64(je_id_view['Day'].iloc[0])
            ]
        )

        print(je_id_view)        
        for row_id in je_id_view.index:
            print(row_id)
            row = df.iloc[row_id]
            line = Entry.EntryLine(
                account=qb_mapping[np.int64(row['Distribution account number'])],
                debit=str_to_float(row['Debit']),
                credit=str_to_float(row['Credit']),
                line_desc=row['Line description'],
                vendor=row['Name']
            )
            journal.add_line(line)
        
        journal_objs.append(journal)
    
    return journal_objs

def make_ledger_obj(journals: list[Entry.Entry]):
    gl = Ledger.Ledger()
    
    for journal in journals:
        gl = gl.add_entry(journal)
    
    return gl