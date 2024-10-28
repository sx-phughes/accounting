import os, datetime, time, shutil, zipfile, re
import payables.fileselector as fileselector
from payables.invoice import Invoice, invoice_constructor
import pandas as pd
from payables.vars import *

class PayableSession(object):
    def __init__(self):
        self.invoice_table = pd.DataFrame(columns=invoice_cols)
        self.welcome()
        self.main_menu()
        self._working_dir = 'C:/gdrive/My Drive/code_projects/payables/bin'
        self._invoice_search_dir = 'C:/Users/phughes_simplextradi/Downloads'
    
    def welcome(self):
        os.system('cls')
        
        print('Welcome to Pat\'s Payable Planner')        
        print('\tversion 0.0.1')
        print('\n\n\n\n')
        print('Press any key to continue...')
        input()
        
        os.system('cls')
        
        print('Would you like to load a previous session or start a new one?')
        print('\t1. Load previous')
        print('\t2. Start new')
        print('\n')
        start_option = int(input('>\t'))
        
        if start_option == 1:
            self.load_payables_file()
        elif start_option == 2:
            self.get_context()
        else:
            self.load_payables_file
            pass
        
    def get_context(self):
        year = int(input('Input the year:\n>\t'))
        self.year = year

        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        months = {month_num: month_name for month_num, month_name in zip(range(1,13), month_names)}

        print('\n\n')

        for i, j in months.items():
            print(f'{i}: {j}')
        print('\n\n')

        month = int(input('Input the month number:\t'))
        self.month = month

        monthyear = datetime.date(year, month, 1).strftime('%Y%m')

        path = f'C:/gdrive/Shared drives/accounting/Payables/{str(year)}/{monthyear}'
        self.main_path = path

        if not os.path.exists(path):
            os.mkdir(path)
            os.mkdir(path + '/Broker Invoices')
            os.mkdir(path + '/CC')

        os.chdir(path)

        folders = os.listdir()

        print('Please select a payables folder:')
        for i in range(len(folders)):
            list_num = i
            print(f'\t{list_num}: {folders[i]}')
        print(f'\t{len(folders)}: Create a new payables folder')

        folder_selection = int(input('>\t'))

        if folder_selection == (len(folders)):
            print('Please input day of month for new payables batch:')
            new_day = int(input('Day >\t'))
            
            new_folder_name = datetime.date(year,month,new_day).strftime('%Y-%m-%d')
            normal_invoice_path = path + f'/{new_folder_name}'
            os.mkdir(normal_invoice_path)
        else:
            normal_invoice_path = path + f'/{folders[folder_selection]}'
            

        self.folder_paths = {
            'invoice': normal_invoice_path,
            'broker': path + '/Broker Invoices',
            'cc': path + '/CC'
        }

    def main_menu(self):
        exit = False
        while not exit:
            os.system('cls')
            print('Payables Session')
            print(f'Year: {self.year}')
            print(f'Month: {self.month}')
            print(f'Working Folder: {self.main_path}')
            print('\n\n\n')
            print('Select an option:')
            
            options_text = [
                'Input Invoices',
                'View Invoices',
                'Export Payables Sheet',
                'Save Payables Session',
                'Settings',
                'Exit'
            ]

            option_selection = self.option_select(options_text)
            option_str = options_text[option_selection]
            
            if option_str == 'Input Invoices':
                self.input_invoices()
            elif option_str == 'View Invoices':
                self.view_invoices()
            elif option_str == 'Export Payables Sheet':
                pass
            elif option_str == 'Save Payables Session':
                pass
            elif option_str == 'Settings':
                self.settings()
            elif option_str == 'Exit':
                exit = True
                
    def option_select(self, options):
        selection = 'no'
        valid_input = False
        
        while not valid_input:
            if re.match(r'\d', selection) and int(selection) in range(len(options)):
                valid_input = True
            else:
                os.system('cls')
                print('Please select an option\n')
                
                for i in range(len(options)):
                    print(f'{i}: {options[i]}')
                    
                selection = input('>\t')
                
        return int(selection)
    
    def settings(self):
        exit_settings = False
        
        while not exit_settings:
            self.print_header('Settings')
            
            options = [
                'Change Working Directory',
                'Change Default Invoice Search Directory',
                'Back to Main Menu'
            ]
            
            dir_id = [
                'wd',
                'inv_src'
            ]
            
            selection = self.option_select(options)
            
            if options[selection] == 'Back to Main Menu':
                exit_settings = True
            else:
                self.change_directory(dir_id[selection])
    
    def change_directory(self, dir_id):
        print('Input new directory path:')
        path = input('>\t')
        
        if not os.path.exists(path):
            print('Please input a valid path')
            time.sleep(3)

        if dir_id == 'wd':
            self._working_dir = path
        elif dir_id == 'inv_src':
            self._invoice_search_dir = path
            
    def change_inv_search_dir(self):
        print('Input new working directory path:')
        path = input('>\t')
        if os.path.exists(path):
            self._working_dir = path
        else:
            print('Please input a valid path')
            time.sleep(3)
        
    def view_invoices(self):
        self.print_header('Current Invoices')
        print(self.invoice_table)
    
    def input_invoices(self):
        os.system('cls')
        
        print('Welcome to Invoice Input')
        print('\n\t Please follow the on-screen prompts to enter your invoices.')
        print('\n\n\t Press any key to continue')
        input()
        
        os.system('cls')
        
        exit = False
        invoices = []
        
        while not exit:            
            os.system('cls')
            
            curr_file = Invoice('New Invoice', self)
            
            print('Step 1: Input invoice data')
            curr_file.data_entry()
            
            confirmed_info = False
            
            while not confirmed_info:
                print('Is this information correct?')
                print(curr_file.vendor)
                print(curr_file.inv_num)
                print(curr_file.inv_date)
                print(curr_file.amount)
                print(curr_file.type)
                
                print('If correct, type y and enter')
                print('If incorrect, type n and enter')
                response = input('\n\t>')
                
                if response in yeses:
                    confirmed_info = True
                    break
                elif response in noes:
                    confirmed_info = False
                    os.system('cls')
                    curr_file.data_entry()
                elif response not in ['y', 'Y', 'yes', 'Yes', 'n', 'N', 'no', 'No']:
                    print('Please input a valid response')
            
            print('Step 2: Invoice file selection')
            file_selection_done = False
            while not file_selection_done:
                filled_invoice = fileselector.file_selector(self._invoice_search_dir, curr_file)
                
                print('Select another file? (y/n)')
                valid_response = False
                while not valid_response:
                    response = input('\n\t>')
                    if response in yeses:
                        valid_response = True
                    elif response in noes:
                        valid_response = True
                        file_selection_done = True
                    else:
                        print('Please input a valid response')
                    
            invoices.append(filled_invoice)
            
            os.system('cls')
            print('Select (1) Enter another invoice or (2) save and quit')
            valid_option = False
            while valid_option == False:
                continue_option = int(input('>\t'))
                if continue_option not in [1,2]:
                    valid_option = False
                    print('Please select a valid option: 1, or 2')
                if continue_option == 1:
                    valid_option = True
                    exit == False
                elif continue_option == 2:
                    valid_option = True
                    exit = True
                    break
            
        for i in invoices:
            for f in i.files:
                new_path = i.save_path + f'/{f['new_name']}.{f['ext']}'
                
                shutil.copyfile(f['path'], new_path)
                f['path'] = new_path
                
            self.invoice_table.loc[len(self.invoice_table.index)] = i.df_format()
        
        self.main_menu()
            
    def construct_session_file(self):
        sys_data = {
            'id': ['year', 'month', 'main_path', 'payables_path'],
            'data': [self.year, self.month, self.main_path, self.folder_paths['invoice']]
        }
        sys_data_df = pd.DataFrame(sys_data)
        invoice_data = self.invoice_table
        
        sys_data_df.to_csv(self.main_path + '/sys.csv', index=False)
        invoice_data.to_csv(self.main_path + '/invoices.csv', index=False)
        
        session_file_name = self.folder_paths['invoice'].split('/')[-1] + '_payable_session.pay'
        with zipfile.ZipFile(session_file_name, 'w') as f:
            f.write(self.main_path + '/sys.csv')
            f.write(self.main_path + '/invoices.csv')
    
    def load_payables_file(self):
        print('Please input the path to the session file you wish to open')
        path = input('>\t')
        
        with zipfile.ZipFile(path, 'r') as f:
            f.extract('sys.csv')
            f.extract('invoices.csv')
        
        sys_df = pd.read_csv('sys.csv')
        invoices_df = pd.read_csv('invoices.csv')
        
        os.remove('sys.csv')
        os.remove('invoices.csv')
        
        id_property_pairs = {
                'year': self.year,
                'month': self.month,
                'main_path': self.main_path,
                'payables_path': self.folder_paths['invoice']
            }
        
        for i, row in sys_df.iterrows():
            id_property_pairs[row['id']] = row['data']
            
        self.invoice_table = invoices_df.reset_index(drop=True)
        
        self.main_menu()
        
    def print_header(self, header_text):
        header_len = len(header_text)
        top_header_char = '-'
        low_header_char = '='
        
        top_border = ''
        low_border = ''
        
        for i in range(2*header_len):
            top_border += top_header_char
            low_border += low_header_char
        
        print(top_border)
        print(header_text)
        print(low_border)
        print('\n')