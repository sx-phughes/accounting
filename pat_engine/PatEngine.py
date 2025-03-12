# Standard imports
import os, sys, traceback, inspect
import pandas as pd


# PATH Updates
sys.path.append(f'{os.environ['HOMEPATH']}\\accounting')
# sys.path.append('C:\\gdrive\\My Drive\\code_projects\\cm_exchange_fees')
# sys.path.append('C:\\gdrive\\My Drive\\code_projects\\abn_month_end')
# sys.path.append('C:\\gdrive\\My Drive\\code_projects\\nacha')
# sys.path.append('C:\\gdrive\\My Drive\\code_projects\\update_vendors')
# sys.path.append('C:\\gdrive\\My Drive\\code_projects\\me_transfers')


# Package Imports
from baycrest import BaycrestSplitter
from payables import PayablesJes
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
        options[return_to] = None
        
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
                        
                        if hasattr(selection[1], '__call__'):
                            selection[1]()
                        else:
                            self.function_wrapper(selection[1][0], selection[1][1])
                            
                    except(KeyError, NameError, FileNotFoundError, ValueError, PermissionError, FileExistsError, IndexError, TypeError):
                        print('Function encountered error:')
                        print(traceback.format_exc())
                        input('Press enter to return to menu\n>\t')
                        
            elif option == len(options.keys()) or option == '':
                break
            
            else:
                print('That is not a valid option')
                os.system('cls')
    def run_f(self, fn):
        input_dict = {}
        
        if inspect.getfullargspec(fn).args:
            
            for arg, default in zip(inspect.getfullargspec(fn).args, inspect.getfullargspec(fn).defaults):
                print(f'Input value for parameter {arg} (default={default}):')
                val = input('>\t')
                input_dict.update({arg, val})
            
            fn(**input_dict)
        
        else:
            fn()
        
        
    def function_wrapper(self, screen_header, functions):
        # Inputs to be formatted in 2D array - [[val_name, default], etc.]
        
        print(screen_header)
        if type(functions) == list:    
            for f in functions:
                self.run_f(f)
        else:
            self.run_f(functions)


       
    ############################################
    # Menu Functions ###########################
    ############################################
    def main_menu(self):
        
        options = {'Baycrest': ['Split Baycrest invoice by IDB and IX', BaycrestSplitter.split],
                   'ABN Cash Files': ['Run ABN Cash Blotter', AbnCash.script_wrapper],
                   'BOFA Just Div Files': ['Pull Full Dividend Summary from BofA Data', OrganizeBAMLfiles.div_file_wrapper],
                   'Month-End Related Functions': self.me_menu,
                   'Unzip Files in Folder': ['Unzip Files in a Folder', UnzipFiles.script_wrapper],
                   'Payables': self.payables,
                   'Update Vendor Value': ['Update a value in the vendor database', UpdateVendors.update_vendor],
                   'Create custom NACHA batch': ['Process custom NACHA batch', BlankBatch.process_file],
                   'Settings': self.settings_menu
        }
        
        self.menu('Main Menu', options, 'Exit Program')
    
    def settings_menu(self):
        
        options = {f'{val}: {data}': '' for val, data in zip(self.settings.vals, [self.settings[name] for name in self.settings.vals])}
        
        self.menu('Settings', options, 'Main Menu', True)
        
    
    def me_menu(self):
        options = {
            'ME Transfers': ['Create Month-End Transfer Journals', MeTransfers.run_ME_Transfers],
            'ABN Month End': ['Run ABN Month End Process - process data files and save to CM directory', AbnMonthEnd.script_wrapper],
            'Organize BAML ME Files': ['Move BofA ME Data Files and Process to Summary Files', OrganizeBAMLfiles.file_mover_wrapper],
            'Get CM Exchange Fee Files': ['Fetch Exchange Fees Files for a Given Month', ExchangeFeesDownload.ExchangeFeesDownload],
        }
        
        self.menu('Month-End Functions', options, 'Main Menu')
    
    def payables(self):
        
        options = {
            'Create Payables Payment Files': ['Create NACHA files for a Payables Batch', NachaMain.nacha_main],
            'Create Paybles JE Files': ['Create Payables JE files for upload to QB', PayablesJes.run_payables]
        }
        
        self.menu('Payables Menu', options, 'Main Menu')