import pandas as pd
    
def split(file_path: str):
    df = pd.read_excel(file_path)
    df = df.drop(df.index[0:17])

    col_names = df.columns.values
    first_row = df.iloc[0].values
    renamer = {i: j for i, j in zip(col_names, first_row)}
    df = df.rename(columns=renamer)
    df = df.drop(df.index[0])
    df = df.reset_index(drop=True)

    df = df.loc[df['Trader'].isna() == False].copy(deep=True)

    last_date = 0
    for i, row in df.iterrows():
        if not pd.isna(row['Date']):
            last_date = row['Date']
        else:
            df.loc[i, 'Date'] = last_date

    idb_copy = df.copy(deep=True)

    ix_trades = df.loc[df['Symbol'].str.contains('SP')]
    idb_trades = idb_copy.drop(ix_trades.index)

    parsed_f_name = file_path.split('.')[0] + ' - split.xlsx'
    full_save_path = parsed_f_name

    #####
    # Finishing
    ####
    with pd.ExcelWriter(full_save_path) as writer:
        idb_trades.to_excel(writer, 'IDB Trades', index=False)
        ix_trades.to_excel(writer, 'IX Trades', index=False)