import pandas as pd
import os, re, csv

# Set path variables
payables_path = 'C:/gdrive/Shared drives/accounting/payables'
code_path = 'C:/gdrive/My Drive/code_projects/payables2'

# Import standard vendor table
vendors_table = pd.read_excel('C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx','Vendors')
std_vendor_names = vendors_table['Vendor'].values

# for each payables file,
#   find Vendor, invoice #, amount cols
#   standardize names --> 'invoiceno', 'vendor', 'amount'
#   add columns --> 'uniqueid', 'processdate', 'invoicemonth','amendment', 'is_paid', 'date_paid', 'filepaths'
#       uniqueid = vendor + invoiceno
#       processdate = payables file date
#       invoicemonth = payables file month
#       amendment = False
#       is_paid = True
#       date_paid = payables file date
#       file_paths = vendor + ' - ' + invoiceno.replace('/','_')
#           check for pdf and excel files (xlsx, xls, csv)

def get_file_paths(years=[2023, 2024, 2025]):
    '''
    Function to get file paths for the payables batch spreadsheets. \n 
    Years set to '23, '24, and '25 by default.
    '''
    os.chdir(payables_path)

    payables_file_paths = {}

    # Get File Names
    for i in years:
        folders = os.listdir(f'./{i}')
        folders = list(filter(lambda x: re.match(fr'{i}\d\d', x), folders))
        
        # Debug
        # for j in folders:
        #     print(j)

        for yrmo in folders:
            yrmo_path = f'./{i}/{yrmo}'
            payables = os.listdir(yrmo_path)

            if int(yrmo) < 202310:
                # For months before 202310 - filter yr_mo files for .xlsm files and add the path of the file to the payables_file_paths list
                payables = list(filter(lambda x: re.search('.xlsm', x), payables))
                payables_w_yrmo = {yrmo: yrmo_path + '/' + path for path in payables}
                payables_file_paths.update(payables_w_yrmo)
            else:
                # For months 202310 and later, need to find payables batch folders
                payables_dates = tuple(filter(lambda x: re.search(r'\d{4}-\d{2}-\d{2}', x), payables))

                # Create a dict of payables dates and paths
                payables_date_dict = {payable_date: [f'{yrmo_path}/{payable_date}/' + file for file in os.listdir(yrmo_path+f'/{payable_date}')] for payable_date in payables_dates}
                
                # Iterate through each payable batch date - can use tuple here bc tuple is keys for the dict
                for date in payables_dates:
                    
                    # Search each file path in the resultant list of directory files for .xlsm files (these are the payables files) and append matches to the file_paths list
                    for file in payables_date_dict[date]:
                        search = re.search('.xlsm', file)
                        if search:
                            payables_file_paths.update({date: search.string})
                        else:
                            continue
            

            # Debug
            # for j in payables:
            #     print(j)
            
    # Debug
    # for j in payables_file_paths:
    #     print(j)
    data_dict = {
        'date': [i for i in payables_file_paths.keys()],
        'path': [payables_file_paths[i] for i in payables_file_paths.keys()]
    }

    # Save point
    pd.DataFrame(data_dict).to_csv(code_path + '/data_collection/payable_file_paths.csv', index=False)

    return payables_file_paths

def read_saved_paths():
    '''
    Reads in saved payables batch file paths\n
    Returns: dict for use in concat_payables_files
    '''
    df = pd.read_csv(code_path + '/data_collection/payable_file_paths.csv', dtype={'date': str, 'path': str})
    date_vals = df['date'].values
    path_vals = df['path'].values
    
    return {date: path for date, path in zip(date_vals, path_vals)}

def concat_payables_files(payables_file_paths: dict):
    '''
    Get all payables data to one table and save to csv.\n
    payables_file_paths = dict of payables path in format date: path\n
        paths will be relative references rooted in payables folder
    '''
    # Change wd to payables folder
    os.chdir(payables_path)

    # Define main_table
    main_table = pd.DataFrame(columns=['yrmo', 'Vendor', 'Invoice #', 'Amount'])

    # Concat each payables table to main_table
    for i in range(len(payables_file_paths.keys())):
        working_key = list(payables_file_paths.keys())[i]
        i_payables_file = pd.read_excel(payables_file_paths[working_key], 'Invoices', usecols=['Vendor', 'Invoice #', 'Amount'], dtype={'Vendor': str, 'Invoice #': str})
        i_payables_file = i_payables_file.dropna(axis=0, how='all')
        i_payables_file['yrmo'] = str(working_key)

        # Debug
        # if working_key == '2024-12-31':
        #     print(working_key)
        #     i_payables_file.to_csv(code_path + '/data_collection/2024-12-31 payables.csv')

        main_table = pd.concat([main_table, i_payables_file])
    
    # Rename columns to std col names
    renamer = {
            'Vendor': 'vendor',
            'Invoice #': 'invoiceno',
            'Amount': 'amount'
        }
    main_table = main_table.rename(columns=renamer)
    
    # Main_table save to csv
    main_table.to_csv(code_path + '/data_collection/all_data.csv', index=False)


def standardize_vendor_names(main_table: pd.DataFrame):
    '''
    Function to standardize the vendor names to the central vendors list.\n
    main_table = all payables batch data created by function concat_payables_files
    '''
    # Get unique vendor names
    vendor_names = list(main_table['vendor'].drop_duplicates().dropna().values)

    search_keys = {}
    # Creating search keys for each vendor
    for i in range(len(vendor_names)):
        # Debug
        # print(vendor_names[i])
        
        search_keys[vendor_names[i]] = [vendor_names[i]]

        # Adding split up vendor name to search by keyword in case full match doesn't work
        split_sorted = sorted(vendor_names[i].split(' '), key=lambda x: len(x), reverse=True)
        if len(split_sorted) > 1:
            for group in split_sorted:
                letters_only = re.search(r'[A-Za-z]*', group)
                if letters_only:
                    search_keys[vendor_names[i]].append(letters_only.group())
                else: 
                    continue

        # Debug
        # print(search_keys)

    # Create dict for matches
    match_dict = {
        'orig_vendor_name': [],
        'matched_vendor_name': []
    }

    # Beginning search for key match
    for i in search_keys.keys():
        # Trim standard vendor names to size - filter by first letter
        x_std_vendor_names = list(filter(lambda x: re.match(fr'^{search_keys[i][0][0]}[\w]*', x, flags=re.IGNORECASE), std_vendor_names))

        # Search for a match and break when one is found, continue to next i_vendor_name
        # Using each key in order...
        match = False
        for i_key in search_keys[i]:

            # Then by each vendor in the shortened list...
            for x_std_name in x_std_vendor_names:

                # Scan for an RE match
                scan = re.search(i_key, x_std_name, flags=re.IGNORECASE)

                # If a match is found, add it to the vendor list, set match = True, break the loop
                if scan:
                    match_dict['orig_vendor_name'].append(i)
                    match_dict['matched_vendor_name'].append(scan.string)

                    # vendor_names[vendor_names.index(i)] = [vendor_names[vendor_names.index(i)], scan.string]
                    
                    # Debug
                    print(f'Match found for vendor name {str(list(search_keys.keys()).index(i)+1)} of {str(len(search_keys.keys()))}')
                    
                    match = True
                    break
                else:
                    # Otherwise, continue to next vendor name

                    continue
        
            # Check if a match is made, if so, break the loop and move to next dirty vendor name
            if match:
                break
            else:
                continue
        
        if not match:
            match_dict['orig_vendor_name'].append(i)
            match_dict['matched_vendor_name'].append('NO MATCH FOUND')

    pd.DataFrame(match_dict).to_csv(code_path + '/data_collection/Vendor Matches.csv', index=False)
            




        


#   add columns --> 'uniqueid', 'processdate', 'invoicemonth','amendment', 'is_paid', 'date_paid', 'filepaths'
#       uniqueid = vendor + invoiceno
#       processdate = payables file date
#       invoicemonth = payables file month
#       amendment = False
#       is_paid = True
#       date_paid = payables file date
#       file_paths = vendor + ' - ' + invoiceno.replace('/','_')
#           check for pdf and excel files (xlsx, xls, csv)