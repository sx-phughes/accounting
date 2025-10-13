import pandas as pd
    
def get_path() -> None:
    """Get path to baycrest file from user
    """
    global file_path
    file_path = input('Input path to file:\n>\t') 

def get_file() -> pd.DataFrame:
    """Reads baycrest invoice spreadsheet into excel

    Returns:
        pd.DataFrame: Dirty baycrest invoice table
    """
    df = pd.read_excel(file_path)
    return df

def rename_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Renames columns to significant headers
    
    Helper function for clean_table

    Args:
        data (pd.DataFrame): Baycrest invoice data

    Returns:
        pd.DataFrame: Baycrest invoice data w new headers
    """
    col_names = data.columns.values
    first_row = data.iloc[0].values
    renamer = {i: j for i, j in zip(col_names, first_row)}
    renamed_cols = data.rename(columns=renamer)
    drop_col_row = renamed_cols.drop(data.index[0]).reset_index(drop=True)
    return drop_col_row

def fix_dates(data: pd.DataFrame) -> pd.DataFrame:
    """Rolls dates down to fill out date column
    
    Helper function for clean_table

    Args:
        data (pd.DataFrame): Baycrest invoice data

    Returns:
        pd.DataFrame: Baycrest invoice data w good date col
    """
    last_date = 0
    for i, row in data.iterrows():
        if not pd.isna(row['Date']):
            last_date = row['Date']
        else:
            data.loc[i, 'Date'] = last_date
    return data

def remove_blank_col(table: pd.DataFrame) -> pd.DataFrame:
    columns = table.columns.values.tolist()
    drop_list = []
    for col in columns:
        if table[col].empty:
            drop_list.append(col)
        else:
            continue
    table = table.drop(columns=drop_list)
    return table

def clean_table() -> pd.DataFrame:
    """Cleans baycrest invoice 
    Removes junk rows, renames columns, fixes dates

    Returns:
        pd.DataFrame: Cleaned baycrest invoice table
    """
    df = get_file()
    top_rows_dropped = df.drop(df.index[0:17]).reset_index(drop=True)
    columns_renamed = rename_columns(top_rows_dropped)
    dates_fixed = fix_dates(columns_renamed)
    nulls_dropped = dates_fixed.loc[dates_fixed['Trader'].isna() == False]
    blanks_removed = remove_blank_col(nulls_dropped)

    return blanks_removed

def make_f_names() -> str:
    """Returns a new file name for modified invoice file
    """
    return file_path.split('.')[0] + '_split.xlsx'

def export_tables() -> None:
    """Exports tables to file
    """
    with pd.ExcelWriter(make_f_names()) as writer:
        split_tables[0].to_excel(
            excel_writer=writer, sheet_name='IDB Trades', index=False
        )
        split_tables[1].to_excel(
            excel_writer=writer, sheet_name='IX Trades', index=False
        )

def split_table(df: pd. DataFrame, symbol_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Splits table based on criteria for IX trades

    Args:
        df (pd.DataFrame): clean Baycrest invoice data
        symbol_col (str): name for column containing underlying symbol data

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: tuple(IDB_trades, IX_trades)
    """
    idb_copy = df.copy(deep=True)

    ix_trades = df.loc[(df[symbol_col].str.contains('SP')) & (df[symbol_col] != '2SPY')]
    idb_trades = idb_copy.drop(ix_trades.index)
    return (idb_trades, ix_trades)

def splitter() -> None:
    """Automated splitter function
    """
    get_path()
    trades = clean_table()

    global split_tables
    split_tables = split_table(trades, 'Symbol')

    export_tables()
    input()