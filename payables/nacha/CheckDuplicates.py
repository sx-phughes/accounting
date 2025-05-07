import pandas as pd


def get_removal_option(trx_table: pd.DataFrame, duplicate: list):
    rows = trx_table.iloc[duplicate[1]]
    print(rows[['Vendor', 'Invoice #', 'Amount']])

    print('Please enter index of row to remove:')
    option = int(input('>\t'))

    return option


def check_duplicates(trx_table: pd.DataFrame):
    trx_table['Concat'] = trx_table['Vendor'] + trx_table['Invoice #'] + trx_table['Amount'].astype(str)

    print(trx_table.loc[trx_table.duplicated('Concat')])

    trx_table = trx_table.drop_duplicates('Concat', keep='first')
    trx_table = trx_table.drop(columns='Concat')

    return trx_table

    # values = list(trx_table['Concat'].values)
    # duplicates = []

    # for i in range(len(values)):
    #     val_count = values.count(values[i])
    #     indexes = []
    #     if values[i] in duplicates or val_count <= 1:
    #         continue
    #     else:
    #         start_count = 0

    #         for j in range(len(val_count)):
    #             index = values.index(values[i], start_count)
    #             indexes.append(index)

    #             start_count = index

    #         duplicates.append([values[i], indexes])

    # if len(duplicates) != 0:
    #     for i in duplicates:
    #         remove_i = get_removal_option(trx_table, i)

    #         trx_table = trx_table.drop_duplicates()