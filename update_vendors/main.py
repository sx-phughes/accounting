import pandas as pd
import re

def search_for_vendor(vendors_df) -> int:
    while True:
        vendor_search = input('Input vendor name to search:\n>\t')
        search_df = vendors_df.loc[vendors_df['Vendor'].str.match(vendor_search, case=False, flags=re.IGNORECASE)]
        print('Search Results:', search_df['Vendor'])
        print('\n')
        
        print('Select number for vendor to edit, enter to search again:')
        
        try:
            vendor_index = int(input('\t>'))
            break
        except ValueError:
            vendor_index = ''
            
    return vendor_index

def print_vendor_info(vendor_row: pd.Series):
    for i in range(len(vendor_row)):
        print(f'{str(i)})\t{vendor_row.index[i]}: {vendor_row.iloc[i]}')
        
def update_value(df: pd.DataFrame, row: int, col: int, new_val):
    df.loc[row, col] = new_val

def save_df(df: pd.DataFrame, gdrive_root: str):
    vendors_path = gdrive_root + '/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx'
    with pd.ExcelWriter(vendors_path, 'xlsxwriter') as writer:
        df.to_excel(writer, 'Vendors')

def open_vendor_sheet(gdrive_root: str):
    vendors_path = gdrive_root + '/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx'
    vendors_df = pd.read_excel(vendors_path, 'Vendors', dtype=str)
    return vendors_df
    
def update_vendor(gdrive_root: str):
    vendors_df = open_vendor_sheet(gdrive_root)
    vendor_i = search_for_vendor(vendors_df)
    
    print_vendor_info(vendors_df.iloc[vendor_i])
    item_to_update = int(input('Input index of item to update:\n>\t'))
    new_val = input('Enter new value:\n>\t')
    
    update_value(vendors_df, vendor_i, item_to_update, new_val)
    save_df(vendors_df, gdrive_root)

def add_vendor(gdrive: str):
   vendors = open_vendor_sheet(gdrive)
   vendors.loc[len(vendors.index)] = get_new_vendor_info() 
   save_df(vendors, gdrive)
   
def get_new_vendor_info():
    prompts = [
        'Vendor',
        'Company',
        'Expense Category',
        'Approver',
        'Payment Type',
        'QB Mapping',
        'Account Mapping'
    ]

    ach_prompts = [
        'ACH ABA',
        'ACH Account Number',
        'ACH Vendor Name'
    ]

    responses = {}
    for i in prompts:
        val = input(f'{i}: ')
        responses.update({i: val})
    
    if responses['Payment Type'] == 'ACH':
        for i in ach_prompts:
            val = input(f'{i}: ')
            responses.update({i: val})
    else:
        for i in ach_prompts:
            responses.update({i: ''})
    
    return responses