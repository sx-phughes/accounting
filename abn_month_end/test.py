import AbnMonthEnd

month = int(input('Closing month:\n>\t'))
year = int(input('Closing month year:\n>\t'))


now = AbnMonthEnd.AbnMonthEnd(year, month)
cm_cash, cm_position = now.grab_files(year, month)

if month == 1:
    pm_cash, pm_position = now.grab_files(year-1, 12)
else:
    pm_cash, pm_position = now.grab_files(year, month-1)

ledger_mapping, account_mapping = now.get_mapping_files()
data_df = now.data_tab(cm_cash, pm_cash, ledger_mapping, account_mapping)

positions, pivot, categories = now.positions_tab(cm_position)

save_stem = 'C:/gdrive/Shared drives/accounting/Simplex Trading/2024/202409/ABN'

data_df.to_csv(save_stem + '/data_df_test.csv', index=False)
positions.to_csv(save_stem + '/positions_df_test.csv', index=False)
pivot.to_csv(save_stem + '/positions-pivot_df_test.csv', index=False)
categories.to_csv(save_stem + '/positions-by-category_df_test.csv', index=False)