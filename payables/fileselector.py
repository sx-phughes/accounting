import os, re
from payables.invoice import Invoice

def get_sorted_files(path):
    path = 'C:/Users/phughes_simplextradi/Downloads'

    files = os.listdir(path)

    files_paths = {os.path.getmtime(path + f'/{i}'): path + f'/{i}' for i in files}

    keys_list = []

    for i in files_paths.keys():
        keys_list.append(i)
        
    sorted_keys = sorted(keys_list, reverse=True)

    sorted_files = [files_paths[key] for key in sorted_keys]
    
    return sorted_files

def file_selector(path, invoice_f:Invoice):
    
    def list_files(path):
        sorted_files = get_sorted_files()
        
        for i in range(len(sorted_files)):
            print(f'{i}: {sorted_files[i]}')
        
        return sorted_files
    
    files_list = list_files(path)
    
    print('\nSelect the file you wish to proceed with, or \'refresh\' to reload files')
    
    selection_complete = False
    
    while not selection_complete:
        file_selection = input('>\t')
        if re.search(r'\d', file_selection):
            selection_complete = True
        elif file_selection == 'refresh':
            files_list = list_files()

    file_selection = int(file_selection)

    file_path = files_list[file_selection]
    
    invoice_f.add_file(file_path)
    
    return invoice_f