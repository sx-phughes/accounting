import os, re, time
import pandas as pd

os.chdir('C:/gdrive/Shared drives/accounting/Projects/Index Allocations')
done = False
while not done:
    try:
        files = os.listdir()
        idb_files = filter(lambda x: re.search(r'\d{6}', x), files)


        master_df = pd.DataFrame()
        for i in idb_files:
            master_df = pd.concat([master_df, pd.read_csv(i)])
            master_df = master_df.reset_index(drop=True)
            
        master_df.sort_values('data_date')

        master_pivot = pd.pivot_table(master_df, 'trade_fee', 'broker', 'data_month', aggfunc='sum')
        master_pivot = master_pivot.reset_index()
        
        full_broker_list = list(master_pivot['broker'].values)
        
        temp_master_pivot = master_pivot.loc[(master_pivot['broker'].str.endswith('X', na=False)) | (master_pivot['broker'].isin(['XFA', 'XFAA', 'XFAF', 'XFAL', 'XFAS', 'WEXF']))].copy(deep=True)
        ix_only_brokers = list(temp_master_pivot['broker'].values)
        
        brokers_to_add_back = []
        for i in ix_only_brokers:
            if i[-1] == 'X':
                broker_root = i[:-1]
                for j in full_broker_list:
                    if broker_root in j and j not in ix_only_brokers:
                        brokers_to_add_back.append(j)
                    else:
                        continue
            else:
                continue
        
        all_needed_brokers = ix_only_brokers + brokers_to_add_back
        needed_brokers_pivot = master_pivot.loc[master_pivot['broker'].isin(all_needed_brokers)]
        needed_brokers_pivot = needed_brokers_pivot.set_index('broker', drop=True)

        #### Finishing ####
        with pd.ExcelWriter('./IDB Summary File.xlsx') as writer:
            master_df.to_excel(writer, 'Master DF', index=False)
            master_pivot.to_excel(writer, 'Pivoted', index=True)
            needed_brokers_pivot.to_excel(writer, 'Needed Brokers', index=True)
        
        done = True
    except PermissionError as e:
        print('Permission Error: Please close the file.')
        print('Waiting three seconds and trying again.')
        time.sleep(3)