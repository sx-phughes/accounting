# Standard imports
import os, sys, traceback, inspect
import pandas as pd
from datetime import datetime


# PATH Updates
sys.path.append('C:\\gdrive\\My Drive\\code_projects')
sys.path.append('C:\\gdrive\\My Drive\\code_projects\\cm_exchange_fees')
sys.path.append('C:\\gdrive\\My Drive\\code_projects\\abn_month_end')
sys.path.append('C:\\gdrive\\My Drive\\code_projects\\nacha')
sys.path.append('C:\\gdrive\\My Drive\\code_projects\\update_vendors')
sys.path.append('C:\\gdrive\\My Drive\\code_projects\\me_transfers')

# Package Imports
from baycrest import BaycrestSplitter
from payables import run_payables
from patrick_functions import AbnCash
from patrick_functions import OrganizeBAMLfiles
from patrick_functions import UnzipFiles
from cm_exchange_fees import ExchangeFeesDownload
from abn_month_end import AbnMonthEnd
from nacha import NachaMain
from nacha import BlankBatch
import update_vendors.main as UpdateVendors
from me_transfers import MeTransfers




# Timesaver function for clearing screen
def cls():
    os.system('cls')
    

# Settings Class for controlling directory variables    
class Settings:
    def __init__(self):
        if os.path.exists('C:/gdrive/My Drive/settings.csv'):
            df = pd.read_csv('C:/gdrive/My Drive/settings.csv')
            data = df.to_dict()
        else:
            data = {'ID': ['userroot', 'googledriveroot'],
                    'Value': ['C:/Users/' + os.environ['HOMEPATH'].split('\\')[-1], 'C:/gdrive/My Drive']}
        
        self._data = data
        self.save_settings()
    
    def __getitem__(self, setting):
        return self._data['Value'][self._data['ID'].index(setting)]
    
    def __setitem__(self, setting, value):
        self._data['Value'][self._data['ID'].index(setting)] = value
        
    def save_settings(self):
        pd.DataFrame(self._data).to_csv('C:/gdrive/My Drive/settings.csv', index=False)
    
    @property        
    def vals(self):
        return self._data['ID']


# Main class for managing scripts
class PatEngine:
    def __init__(self):
        self.settings = Settings()
    
    def menu(self, menu_title, options: dict, return_to: str, do_settings: bool=False):
        os.system('cls')
        options[return_to[0]] = None
        
        while True:
            os.system('cls')
            print(menu_title)
            
            for i in range(len(options.keys())):
                print(f'{i+1}. {list(options.keys())[i]}')
        
            print('Please select an option by number:')
            option = int(input('>\t'))
        
            if option in range(1, len(options.keys())):
                
                if do_settings:
                    
                    new_val = input('Please input new value for setting:\n>\t')
                    self.settings[self.settings.vals[option]] = new_val
                    print('Settings updated')
                    print('Press enter to return to main menu')
                else:
                    
                    try:
                        selection = list(options.items())[option - 1]
                        
                        self.function_runner(selection[1][0], selection[1][1])
                    except(KeyError, NameError, FileNotFoundError, ValueError, PermissionError, FileExistsError, IndexError, TypeError):
                        print('Function encountered error:')
                        print(traceback.format_exc())
                        input('Press enter to return to menu\n>\t')
                        
            elif option == len(options.keys()) or option == '':
                break
            
            else:
                print('That is not a valid option')
                os.system('cls')
                
    def function_runner(self, screen_header, functions):
        # Inputs to be formatted in 2D array - [[val_name, default], etc.]
        
        print(screen_header)
        
        for f in functions:
            input_dict = {}
            
            for arg, default in zip(inspect.getfullargspec(f).args, inspect.getfullargspec(f).defaults):
                print(f'Input value for parameter {arg} (default={default}):')
                val = input('>\t')
                input_dict.update({arg, val})
            
            f(**input_dict)


       
    ############################################
    # Menu Functions ###########################
    ############################################
    def main_menu(self):
        
        options = {'Baycrest': BaycrestSplitter.split,
                   'ABN Cash Files': AbnCash.script_wrapper,
                   'BOFA Just Div Files': self.run_baml_div_files,
                   'Month-End Related Functions': self.me_menu,
                   'Unzip Files in Folder': UnzipFiles.script_wrapper,
                   'Payables': self.payables,
                   'Update Vendor Value': UpdateVendors.update_vendor,
                   'Create custom NACHA batch': BlankBatch.process_file,
                   'Settings': self.settings_menu
        }
        
        self.menu('Main Menu', options, 'Exit Program')
    
    def settings_menu(self):
        
        options = {f'{val}: {data}': '' for val, data in zip(self.settings.vals, [self.settings[name] for name in self.settings.vals])}
        
        self.menu('Settings', options, 'Main Menu', True)
        
    
    def me_menu(self):
        options = {
            'ME Transfers': ['Create Month-End Transfer Journals', MeTransfers.run_ME_Transfers],
            'ABN Month End': AbnMonthEnd.script_wrapper,
            'Organize BAML ME Files': OrganizeBAMLfiles.script_wrapper,
            'Get CM Exchange Fee Files': ExchangeFeesDownload.ExchangeFeesDownload,
        }
        
        self.menu('Month-End Functions', options, 'Main Menu')
    
    def payables(self):
        
        options = {
            'Create Payables Payment Files': NachaMain.nacha_main,
            'Create Paybles JE Files': run_payables.run_payables
        }
        
        self.menu('Payables Menu', options, 'Main Menu')
    
    
    
    ############################################
    # Script Functions #########################
    ############################################ 
    # def me_transfers(self):
    #     cls()
        
    #     date = {'Year': '', 'Month': '', 'Day': ''}
    #     for unit in date.keys():
    #         date[unit] = int(input(f'Input ME {unit}:\n>\t'))
        
    #     save_path = input('Input desired save path (default is downloads):\n>\t')
    #     if save_path == '':
    #         save_path = f'{self.settings['userroot']}/Downloads'
        
    #     dt = datetime(date['Year'], date['Month'], date['Day'])
        
    #     MeTransfers.run_abn_tables(dt, save_path)
    #     MeTransfers.run_baml_table(dt, save_path)
        
    #     print(f'ABN and BofA ME Transfers Saved to {save_path}')
        
        
    # def run_update_vendor(self):
    #     cls()
    #     print('Update Vendor Value in AP Central DB')
    #     update_vendor(self.settings['googledriveroot'].replace('/My Drive', ''))
        
    # def run_baycrest(self):
    #     cls()
        
    #     print('Baycrest IX-IDB Splitter')
        
    #     print('File Path:')
    #     f_path = input('>\t')
    #     print('Save Path:')
    #     s_path = input('>\t')

    #     file = BaycrestSplitter(f_path, s_path)
    #     file.run()
        
    # def run_abn_cash(self):
    #     cls()
        
    #     print('ABN Cash Blog')
        
    #     print('Month')
    #     month = int(input('>\t'))
    #     print('Year')
    #     year = int(input('>\t'))
        
    #     cash = AbnCash(month=month, year=year)
    #     cash.main()
        
    #     print(f'Saved to {cash.save_path}')
        
    #     input('Press enter to continue')
    
    # def abn_me(self):
    #     cls()
        
    #     print('ABN Month End Process')
        
    #     month = int(input('Closing month:\n>\t'))
    #     year = int(input('Closing month year:\n>\t'))
    #     AbnMonthEnd(year, month).main()
        
    #     print('ABN Month End files completed')
    #     input('Press enter to continue')
        
        
    # def run_baml_files(self):
    #     cls()

    #     print('Organize BAML Files into BAML ME Folder')

    #     print('Month:')
    #     month = int(input('>\t'))
    #     print('Year:')
    #     year = int(input('>\t'))

    #     BAMLFileMover(year, month).main()

    #     print('Files moved')
    #     input('Press enter to contiunue')

    # def run_baml_div_files(self):
    #     cls()

    #     print('Run BOFA Div files only')

    #     print('Month:')
    #     month = int(input('>\t'))
    #     print('Year:')
    #     year = int(input('>\t'))

    #     BAMLFileMover(year, month).just_div_files()

    #     print('Div Files Processed')
    #     input('Press enter to contiunue')
    
    # def unzip_files(self):
    #     cls()

    #     print('Unzip all .zip/.gz/.xz files in a directory')

    #     print('Directory path:')
    #     zip_path = input('>\t')
    #     print('Save Path:')
    #     save_path = input('>\t')
    #     print('Delete archive files? (y/n)')
    #     yn = input('>\t')

    #     if yn == 'y':
    #         yn = True
    #     else:
    #         yn = False
        
    #     unzipper = UnzipFiles.UnzipFiles(zip_path, save_path)
    #     unzipper.main(delete_zip=yn)
        
    #     print('Files unzipped to ' + save_path)
    #     input('Press enter to continue')
        
    # def cm_exchange(self):
    #     cls()
        
    #     print('Download all CM exchange fee files from CBOE and off2.s')
        
    #     print('Download path (no trailing backslash):')
    #     dl_path = input('>\t')
    #     print('Exchange Fee Month:')
    #     month = int(input('>\t'))
    #     print('Exchange Fee Year:')
    #     year = int(input('>\t'))
    #     print('Skip CBOE downloads? (enter to skip)')
    #     skip_cboe = input('>\t')
        
        
    #     ExchangeFeesDownload(month, year, dl_path, bool(skip_cboe), )
        
        
    #     if not skip_cboe:
    #         print('Input CBOE Username:')
    #         username = input('>\t')
    #         print('Input CBOE Password:')
    #         pw = input('>\t')
            
    #         downloader.cboe_files(username, pw)


    #     print('Input SSH Username:')
    #     ssh_un = input('>\t')
    #     print('Input SSH Password:')
    #     ssh_pw = input('>\t')

    #     downloader.other_exchange_files(ssh_un, ssh_pw)
        
    #     print('Files saved to ' + dl_path)
    #     input('Press enter to continue')
    
    # def nacha(self):
    #     cls()
        
    #     NachaMain.nacha_main(self.get_setting('userroot'))
        
    #     print('NACHA Files Saved to Downloads')
    #     input('Press enter to continue')
        
    # def payables_jes(self):
    #     cls()
        
    #     print('Create payables JEs')
        
    #     run_payables(self.settings['userroot'])
        
    #     print('Payables JEs saved to Downloads')
    #     input('Press enter to return to menu options\n>\t')
    
    # def custom_nacha(self):
    #     cls()
        
    #     print('Create Blank Nacha Batch')
        
    #     f_path = input('Input full path to file with ACH info:\n>\t')
    #     save_to = input('Input desired save location, including file name:\n>\t')
    #     vd = datetime.strptime(input('Input desired value date in format mm/dd/yyyy:\n>\t'), '%m/%d/%Y')
    #     company = BlankBatch.nacha_company_selector()
    #     trx_line_note = input('Input note to include with transactions:\n>\t')
    #     batch_description = input('Input batch description (e.g., \'Payables\', \'Reimbursements\', etc.):\n>\t')
        
    #     print('Processing file...')
    #     BlankBatch.process_file(
    #         src_path=f_path,
    #         save_path=save_to,
    #         company_name=company,
    #         value_date=vd,
    #         trx_note=trx_line_note,
    #         batch_descr=batch_description
    #     )
    #     print('NACHA File created and saved to {save_to}'.format(save_to=save_to))
    #     input('Press enter to continue')