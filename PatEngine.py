# Standard imports
import os
import re
import traceback
import inspect
import pandas as pd

# Package Imports
from baycrest import BaycrestSplitter
from payables import PayablesJes
from patrick_functions import AbnCash
from bofa_month_end import OrganizeBAMLfiles
from patrick_functions import UnzipFiles
from cm_exchange_fees import ExchangeFeesDownload
from abn_month_end import AbnMonthEnd
from nacha import NachaMain
from nacha import BlankBatch
import update_vendors.main as UpdateVendors
from me_transfers import MeTransfers
from basic_payables import os_interface


def cls():
    """Shortcut to clear screen"""
    os.system('cls')
    

# Settings Class for controlling directory variables    
class Settings:
    """Settings class for use in PatEngine class"""
    def __init__(self):
        # Check for settings file, otw create
        if os.path.exists('C:/gdrive/My Drive/settings.csv'):
            df = pd.read_csv('C:/gdrive/My Drive/settings.csv')
            data = df.to_dict()
        else:
            data = {
                'ID': [
                    'userroot',
                    'googledriveroot'
                ],
                'Value': [
                    'C:/Users/' + os.environ['HOMEPATH'].split('\\')[-1],
                    'C:/gdrive/My Drive'
                ]
            }
        
        self._data = data
        self.save_settings()
    
    def __getitem__(self, setting):
        return self._data['Value'][self._data['ID'].index(setting)]
    
    def __setitem__(self, setting, value):
        self._data['Value'][self._data['ID'].index(setting)] = value
    
    # Save to disk
    def save_settings(self):
        pd.DataFrame(self._data).to_csv('C:/gdrive/My Drive/settings.csv', index=False)
    
    # Return a series of the settings keys
    @property        
    def vals(self):
        return self._data['ID']


class PatEngine:
    def __init__(self):
        self.settings = Settings()
    
    def menu(
        self,
        menu_title: str, 
        options: dict,
        return_to: str,
        do_settings: bool = False
    ):
        """Primary menu function for managing and running scripts

        Args:
            menu_title (str): title of the menu screen to be generated
            options (dict): Dictionary of 
                {
                    function/script name: [
                        script screen title string,
                        list of fn or singular functions
                    ]
                }
            return_to (str): option to describe the 
                previous screen if current menu is left
            do_settings (bool, optional): Boolean for whether or not this is 
                going to be used for settings. Defaults to False.

        Returns:
            None 
        """
        os.system('cls')
        options[return_to] = None
        
        while True:
            os.system('cls')
            print(menu_title)
            self.print_options(options) 
            print('Please select an option by number:')
            option = self.get_option_selection(options) 

            if option == len(options.keys()) or option == '':
                break
            elif do_settings:
                self.update_settings()            
            else:
                self.do_option(option, options)
                input()

    def do_option(self, option: int, options: dict) -> None:
        """Run user input option"""
        try:
            self.run_selection(option, options)            
        except (
            KeyError, NameError, FileNotFoundError, ValueError,
            PermissionError, FileExistsError, IndexError, TypeError
        ):
            self.function_encountered_error()                

    def function_encountered_error(self):
        """Messages for when function encounters error"""
        print('Function encountered error:')
        print(traceback.format_exc())
        input('Press enter to return to menu\n>\t')
        
    def run_selection(self, option: int, options: dict):
        """Get function from list of options and run function or initialize
        next menu
        """
        selection = list(options.items())[option - 1]
        if hasattr(selection[1], '__call__'):
            selection[1]()
        else:
            self.function_wrapper(selection[1][0], selection[1][1])

    def get_option_selection(self, options: dict):
        """Loop for getting a valid option selection"""
        option = 0 
        while not option:
            option = self.get_option_input(options)
        return option

    def get_option_input(self, options: dict):
        num_options = len(list(options.keys()))
        selection = input('>\t')
        validated = self.validate_option(selection, num_options)
        return validated

    def validate_option(self, selection: str, num_options: int):
        """Confirm option is an integer and in range of options"""
        if re.match(r'\d+', selection):
            integer_selection = int(selection)
            if integer_selection <= num_options:
                return integer_selection
        print('Bad option!')

    def update_settings(self):
        new_val = input('Please input new value for setting:\n>\t')
        # self.settings[self.settings.vals[option]] = new_val
        print('Settings updated')
        print('Press enter to return to main menu')

    def print_options(self, options: dict):
        """Print menu options to screen"""
        for i in range(len(options.keys())):
            print(f'{i+1}. {list(options.keys())[i]}')

    def run_f(self, fn):
        """Run function with standard UI for inputs"""
        if inspect.getfullargspec(fn).args:
            self.run_fn_with_args(fn)
        else:
            fn()

    def run_fn_with_args(self, fn):
        input_dict = {}
        args = inspect.getfullargspec(fn).args
        default_args = inspect.getfullargspec(fn).defaults

        print('Params: ', args)
        print('Defaults: ', default_args)

        for arg in args:
            self.get_arg(arg, input_dict)
        
        fn(**input_dict)
        
    def get_arg(self, arg: str, arg_storage: dict):
        """Get argument value from user"""
        print(f'Input value for parameter {arg}: ') 
        val = input('>\t')
        typed_val = self.type_val(val)
        arg_storage.update({arg: typed_val})
        
    def type_val(self, val):
        """Convert user input to an integer"""
        if re.match(r'\d+', val):
            return int(val)
        else:
            return val
         
    def function_wrapper(self, screen_header, functions):
        """Wrapper to manage multiple functions on a separate screen with
        title
        """
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
        """Options to be displayed on opening screen"""
        options = {
            'Baycrest': [
                'Split Baycrest invoice by IDB and IX',
                BaycrestSplitter.splitter
            ],
            'ABN Cash Files': [
                'Run ABN Cash Blotter',
                AbnCash.script_wrapper
            ],
            'BOFA Just Div Files': [
                'Pull Full Dividend Summary from BofA Data',
                OrganizeBAMLfiles.div_file_wrapper
            ],
            'Month-End Related Functions':
                self.me_menu,
            'Unzip Files in Folder': [
                'Unzip Files in a Folder',
                UnzipFiles.script_wrapper
            ],
            'Payables':
                self.payables,
            'Update Vendor Value': [
                'Update a value in the vendor database',
                UpdateVendors.update_vendor
            ],
            'Add a Vendor': [
                'Add a New Vendor',
                UpdateVendors.add_vendor
            ],
            'Create custom NACHA batch': [
                'Process custom NACHA batch',
                BlankBatch.process_file
            ],
            'Settings':
                self.settings_menu
        }
        
        self.menu('Main Menu', options, 'Exit Program')
    
    def settings_menu(self):
        """Settings options"""
        options = {
            f'{val}: {data}': '' for val, data in 
                zip(
                    self.settings.vals,
                    [self.settings[name] for name in self.settings.vals]
                )
        }
        
        self.menu('Settings', options, 'Main Menu', True)
        
    
    def me_menu(self):
        """Sub-menu options for month-end-specific functions"""
        options = {
            'ME Transfers': [
                'Create Month-End Transfer Journals',
                MeTransfers.run_ME_Transfers
            ],
            'ABN Month End': [
                'Run ABN Month End Process - \
                process data files and save to CM directory',
                AbnMonthEnd.script_wrapper
            ],
            'Organize BAML ME Files': [
                'Move BofA ME Data Files and Process to Summary Files',
                OrganizeBAMLfiles.file_mover_wrapper
            ],
            'Get CM Exchange Fee Files': [
                'Fetch Exchange Fees Files for a Given Month',
                ExchangeFeesDownload.ExchangeFeesDownload
            ],
        }
        
        self.menu('Month-End Functions', options, 'Main Menu')
    
    def payables(self):
        """Sub-menu options for running payables-related scripts"""
        options = {
            'Input Payables': [
                'Manage Payables Workbook: view/input/remove',
                os_interface.__main__
            ],
            'Create Payables Payment Files': [
                'Create NACHA files for a Payables Batch',
                NachaMain.nacha_main
            ],
            'Create Paybles JE Files': [
                'Create Payables JE files for upload to QB',
                PayablesJes.run_payables
            ]
        }
        
        self.menu('Payables Menu', options, 'Main Menu')
