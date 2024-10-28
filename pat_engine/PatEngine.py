import os, sys
from abc import ABC
sys.path.append('C:\\gdrive\\My Drive\\code_projects')
from baycrest.BaycrestSplitter import BaycrestSplitter
from patrick_functions.AbnCash import AbnCash
from patrick_functions.OrganizeBAMLfiles import BAMLFileMover
from patrick_functions import UnzipFiles
sys.path.append('C:\\gdrive\\My Drive\\code_projecs\\cm_exchange_fees')
from cm_exchange_fees.ExchangeFeesDownload import ExchangeFeesDownload

class PatEngine(ABC):
    def __init__(self):
        pass
    
    def main_menu(self):
        os.system('cls')
        
        options = {'Baycrest': self.run_baycrest,
                   'ABN Cash Files': self.run_abn_cash,
                   'Organize BAML ME Files': self.run_baml_files,
                   'Get CM Exchange Fee Files': self.cm_exchange,
                   'Unzip Files in Folder': self.unzip_files}
        
        while True:
            print('Main Menu')
            
            for i in range(len(options.keys())):
                print(f'{i+1}. {list(options.keys())[i]}')
            
            print('Please select an option by number:')
            option = int(input('>\t'))
            
            if option in range(1, len(options.keys())+1):
                options[list(options.keys())[option-1]]()
            else:
                print('That is not a valid option')
                os.system('cls')
                
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
        
        cash = AbnCash(month=month, year=year).main()
        
        print('Saved to Google Drive')
        
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
        
        print('Files saved to ' + dl_path)
        input('Press enter to continue')

        self.main_menu()
