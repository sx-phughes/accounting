import os, sys, traceback
import pandas as pd
from datetime import datetime
sys.path.append('C:\\gdrive\\My Drive\\code_projects')
from baycrest.BaycrestSplitter import BaycrestSplitter
from payables.test_payables_je import run_payables
from patrick_functions.AbnCash import AbnCash
from patrick_functions.OrganizeBAMLfiles import BAMLFileMover
from patrick_functions import UnzipFiles
sys.path.append('C:\\gdrive\\My Drive\\code_projects\\cm_exchange_fees')
from cm_exchange_fees.ExchangeFeesDownload import ExchangeFeesDownload
sys.path.append('C:\\gdrive\\My Drive\\code_projects\\abn_month_end')
from abn_month_end import test
sys.path.append('C:\\gdrive\\My Drive\\code_projects\\nacha')
from nacha import NachaMain
sys.path.append('C:\\gdrive\\My Drive\\code_projects\\update_vendors')
from update_vendors.main import update_vendor
sys.path.append('C:\\gdrive\\My Drive\\code_projects\\me_transfers')
from me_transfers import MeTransfers

def cls():
    os.system('cls')

class PatEngine:
    def __init__(self):
        self.settings = self.init_settings()
    
    def get_setting(self, id):
        return self.settings['Value'][list(self.settings['ID'].values()).index(id)]
    
    def set_setting(self, id, new_value):
        self.settings['Value'][list(self.settings['ID'].values()).index(id)] = new_value
        self.save_settings()
    
    def save_settings(self):
        pd.DataFrame(self.settings).to_csv('C:/gdrive/My Drive/settings.csv', index=False)
    
    def init_settings(self):
        if os.path.exists('C:/gdrive/My Drive/settings.csv'):
            df = pd.read_csv('C:/gdrive/My Drive/settings.csv')
            data = df.to_dict()
        else:
            data = {'ID': ['userroot', 'googledriveroot'],
                    'Value': ['C:/Users/' + os.getlogin(), 'C:/gdrive/My Drive']}
            pd.DataFrame(data).to_csv('C:/gdrive/My Drive/settings.csv', index=False)
        
        return data
            
    def view_settings(self):
        os.system('cls')
        
        for i in range(len(self.settings['ID'])):
            curr_id = self.settings['ID'][i]
            print(f'{str(i+1)}. {curr_id}: {self.get_setting(curr_id)}')
        print('\n\n')
        print('Please select a setting to update, or enter to exit:')
        option = input('>\t')
        
        if option:
            print('Please input new value:')
            new_val = input('>\t')
            self.set_setting(self.settings['ID'][int(option)-1], new_val)
            print('Settings Updated')
            print('Hit enter to continue')
            input()
            self.view_settings()
        else:
            self.main_menu()
    
    def menu(self, menu_title, options: dict, return_to: list):
        os.system('cls')
        options[return_to[0]] = return_to[1]
        
        while True:
            os.system('cls')
            print(menu_title)
            
            for i in range(len(options.keys())):
                print(f'{i+1}. {list(options.keys())[i]}')
                
            print('Please select an option by number:')
            option = int(input('>\t'))
        
            if option in range(1, len(options.keys())+1):
                try:
                    options[list(options.keys())[option-1]]()
                except(KeyError, NameError, FileNotFoundError, ValueError, PermissionError, FileExistsError, IndexError, TypeError):
                    print('Function encountered error:')
                    print(traceback.format_exc())
                    input('Press enter to return to menu\n>\t')
                    
                    
                    
            else:
                print('That is not a valid option')
                os.system('cls')
         
         
                
    ############################################
    # Menu Functions ###########################
    ############################################
    
    def main_menu(self):
        
        options = {'Baycrest': self.run_baycrest,
                   'ABN Cash Files': self.run_abn_cash,
                   'BOFA Just Div Files': self.run_baml_div_files,
                   'Month-End Related Functions': self.me_menu,
                   'Unzip Files in Folder': self.unzip_files,
                   'Payables': self.payables,
                   'Update Vendor Value': self.run_update_vendor,
                   'Settings': self.view_settings
        }
        
        self.menu('Main Menu', options, ['Exit Program', self.exit])
    
    def me_menu(self):
        options = {
            'ME Transfers': self.me_transfers,
            'ABN Month End': self.abn_me,
            'Organize BAML ME Files': self.run_baml_files,
            'Get CM Exchange Fee Files': self.cm_exchange,
        }
        
        self.menu('Month-End Functions', options, ['Main Menu', self.main_menu])
    
    def payables(self):
        
        options = {
            'Create Payables Payment Files': self.nacha,
            'Create Paybles JE Files': self.payables_jes
        }
        
        self.menu('Payables Menu', options, ['Main Menu', self.main_menu])
    
    
    
    ############################################
    # Script Functions #########################
    ############################################ 
        
    def me_transfers(self):
        cls()
        
        date = {'Year': '', 'Month': '', 'Day': ''}
        for unit in date.keys():
            date[unit] = int(input(f'Input ME {unit}:\n>\t'))
        
        save_path = input('Input desired save path (default is downloads):\n>\t')
        if save_path == '':
            save_path = f'{self.get_setting('userroot')}/Downloads'
        
        dt = datetime(date['Year'], date['Month'], date['Day'])
        
        MeTransfers.run_abn_tables(dt, save_path)
        MeTransfers.run_baml_table(dt, save_path)
        
        print(f'ABN and BofA ME Transfers Saved to {save_path}')
        
        
    def run_update_vendor(self):
        cls()
        
        print('Update Vendor Value in AP Central DB')
        
        update_vendor(self.get_setting('googledriveroot').replace('/My Drive', ''))
        
        self.main_menu()
    
    def exit(self):
        os.system('cls')

        print('Exit program?')
        ans = input('y/n\n>\t')
        if ans == 'y':
            sys.exit()
        
    def run_baycrest(self):
        os.system('cls')
        
        print('Baycrest IX-IDB Splitter')
        
        print('File Path:')
        f_path = input('>\t')
        print('Save Path:')
        s_path = input('>\t')

        file = BaycrestSplitter(f_path, s_path)
        file.run()
        
        self.main_menu()
        
    def run_abn_cash(self):
        os.system('cls')
        
        print('ABN Cash Blog')
        
        print('Month')
        month = int(input('>\t'))
        print('Year')
        year = int(input('>\t'))
        
        cash = AbnCash(month=month, year=year)
        cash.main()
        
        print(f'Saved to {cash.save_path}')
        
        input('Press enter to continue')
        
        self.main_menu()
    
    def abn_me(self):
        os.system('cls')
        
        print('ABN Month End Process')
        
        month = int(input('Closing month:\n>\t'))
        year = int(input('Closing month year:\n>\t'))
        test.main(year, month)
        
        print('ABN Month End files completed')
        input('Press enter to continue')

        self.main_menu()
        
        
    def run_baml_files(self):
        os.system('cls')

        print('Organize BAML Files into BAML ME Folder')

        print('Month:')
        month = int(input('>\t'))
        print('Year:')
        year = int(input('>\t'))

        BAMLFileMover(year, month).main()

        print('Files moved')
        input('Press enter to contiunue')
        self.main_menu()

    def run_baml_div_files(self):
        os.system('cls')

        print('Run BOFA Div files only')

        print('Month:')
        month = int(input('>\t'))
        print('Year:')
        year = int(input('>\t'))

        BAMLFileMover(year, month).just_div_files()

        print('Div Files Processed')
        input('Press enter to contiunue')
        self.main_menu()
    
    def unzip_files(self):
        os.system('cls')

        print('Unzip all .zip/.gz/.xz files in a directory')

        print('Directory path:')
        zip_path = input('>\t')
        print('Save Path:')
        save_path = input('>\t')
        print('Delete archive files? (y/n)')
        yn = input('>\t')

        if yn == 'y':
            yn = True
        else:
            yn = False
        
        unzipper = UnzipFiles.UnzipFiles(zip_path, save_path)
        unzipper.main(delete_zip=yn)
        
        print('Files unzipped to ' + save_path)
        input('Press enter to continue')
        
        self.main_menu()
        
    def cm_exchange(self):
        os.system('cls')
        
        print('Download all CM exchange fee files from CBOE and off2.s')
        
        print('Download path (no trailing backslash):')
        dl_path = input('>\t')

        print('Exchange Fee Month:')
        month = int(input('>\t'))
        
        print('Exchange Fee Year:')
        year = int(input('>\t'))
        
        print('Skip CBOE downloads? (y/n)')
        skip_cboe = input('>\t')
        
        downloader = ExchangeFeesDownload(month, year, dl_path)
        
        if skip_cboe == 'n':
            downloader.main()
        else:
            downloader.not_cboe_files()
        
        print('Files saved to ' + self.get_setting('userroot') + '/Downloads')
        input('Press enter to continue')

        self.main_menu()
    
    def nacha(self):
        os.system('cls')
        
        NachaMain.nacha_main(self.get_setting('userroot'))
        
        print('NACHA Files Saved to Downloads')
        input('Press enter to continue')

        self.main_menu()
        
    def payables_jes(self):
        os.system('cls')
        
        print('Create payables JEs')
        
        run_payables(self.get_setting('userroot'))
        
        print('Payables JEs saved to Downloads')
        input('Press enter to return to menu options\n>\t')