import AbnMonthEnd

month = int(input('Closing month:\n>\t'))
year = int(input('Closing month year:\n>\t'))


now = AbnMonthEnd.AbnMonthEnd(year,month)
cm_cash, cm_position = now.grab_files(year, month)
pm_cash, pm_position = now.grab_files(2024, month-1)
ledger_mapping, account_mapping = now.get_mapping_files()
data_df = now.data_tab(cm_cash, pm_cash, ledger_mapping, account_mapping)

data_df.to_csv('./data_df_test.csv', index=False)

positions, pivot, categories = now.positions_tab(cm_position)

save_stem = f'C:/gdrive/Shared drives/accounting/Simplex Trading/{str(year)}/{str(year)+str(month)}/ABN'

positions.to_csv(save_stem + '/positions_df_test.csv')
pivot.to_csv(save_stem + '/positions-pivot_df_test.csv')
categories.to_csv(save_stem + '/positions-by-category_df_test.csv')