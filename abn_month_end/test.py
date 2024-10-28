import AbnMonthEnd

now = AbnMonthEnd.AbnMonthEnd(2024,9)
cm_cash, cm_position = now.grab_files(2024, 9)
# pm_cash, pm_position = now.grab_files(2024, 7)
# ledger_mapping, account_mapping = now.get_mapping_files()
# data_df = now.data_tab(cm_cash, pm_cash, ledger_mapping, account_mapping)

# data_df.to_csv('./data_df_test.csv')

positions, pivot, categories = now.positions_tab(cm_position)

save_stem = 'C:/gdrive/Shared drives/accounting/Simplex Trading/2024/202409/ABN'

positions.to_csv(save_stem + '/positions_df_test.csv')
pivot.to_csv(save_stem + '/positions-pivot_df_test.csv')
categories.to_csv(save_stem + '/positions-by-category_df_test.csv')