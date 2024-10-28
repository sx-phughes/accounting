import os
from abc import ABC


class SimplexClient(ABC):
    def __init__(self):
        self.print_welcome_text()
        self.main_menu()
        
    def main_menu(self):
        exit = False
        
        while not exit:
            os.system('cls')

            categories = [
                'File System Management',       # for things like setting up a new payables month, rolling folders forward, etc
                'Data Processing',              # BOFA/ABN ME accounting setup
                'Accounts Payable',             # payables client
                'Exit'
            ]
            
            functions = [
                self.file_sys,
                self.process_data,
                self.payables,
                self.quit
            ]
            
            self.print_header('Main Menu')
            
            option = self.option_select(categories)
            
            functions[option]()
            
    def print_welcome_text(self):
        os.system('cls')
        
        print('Welcome to the Simplex Accounting Assistant')
        print('version 0.0.1')
        print('\n\n\n\n')
        print('Press any key to continue')
        input()
        
        os.system('cls')
        
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
        
        
    def option_select(self, options_list):
        valid_choice = False
        
        while not valid_choice:
            for i in range(len(options_list)):
                print(f'{i}: {options_list[i]}')
            
            print('\nPlease input the number of the desired response')
            response = int(input('>\t'))
            
            if response not in range(len(options_list)):
                print('Please select a valid option')
                os.system('cls')
            else:
                valid_choice = True
        
        return response
    
    def file_sys(self):
        file_sys_exit = False
        
        while not file_sys_exit:
            os.system('cls')
            
            self.print_header('File System Management')
            
            options = [
                'New Payables Folder',
                'Roll Forward Month Folder',
                'Back to Main Menu'
            ]
            
            functions = [
                self.new_payables,
                self.roll_month
            ]
            
            option = self.option_select(options)
            
            if options[option] == 'Back to Main Menu':
                file_sys_exit = True
                break
            else:
                functions[option]()
    
    def process_data(self):
        pass
    
    def payables(self):
        pass
    
    def quit(self):
        pass
    
    def new_payables(self):
        os.system('cls')
        
        print('Create New Payables Folder')
        print('Input the year for the new folder')
        year = int(input('>\t'))
        print('\nInput the month number, with no leading zeroes')
        month = int(input('>\t'))
        
        os.system('cls')
        
        if month >= 10:
            monthyear = str(year) + str(month)
        else:
            monthyear = str(year) + '0' + str(month)
            
        print(f'Creating Payables Folder {monthyear}\n\n')
        
        payables_root = 'C:/gdrive/Shared drives/accounting/Payables'
        
        check_stems = [
            f'/{str(year)}',
            f'/{str(year)}/{monthyear}',
            f'//{str(year)}/{monthyear}/Broker Invoices',
            f'//{str(year)}/{monthyear}/CC',
            f'//{str(year)}/{monthyear}/Legal'
        ]
        
        for i in [payables_root + stem for stem in check_stems]:
            if os.path.exists(i):
                print(f'Path already exists: {i}')
                continue
            else:
                print(f'Creating path: {i}')
                os.mkdir(i)
        
        print('Payables folder created')
        print('\n\npress any key to continue')
        input()
        
    def roll_month(self):
        os.system('cls')
        
        print('Roll Forward File Structure')
        
        print('\n\nThis feature is still indevelopment')