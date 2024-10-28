from CreditCardData import CreditCardData
import os, re
from abc import ABC

class CCSearchEngine(ABC):
    def __init__(self):
        print('Credit Card Data Search Engine v0.1')
        print('Loading Credit Card Data')
        self.data = CreditCardData()
    
    def launch_program(self):
        self.main_menu()

    def main_menu(self):
        os.system('cls')
        
        options = {'Search by keyword': self.keyword_search,
                   'Search by date': self.date_search,
                   'Search by memo': self.memo_search,
                   'Set save directory': self.save_directory,
                   'Close program': self.close}
        
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
            
    def memo_search(self):
        os.system('cls')
        while True:
            print('Search by memo')
            print('Please enter the memo you\'d like to search by, or "<<main>>" to return to main menu:')
            memo = input('>\t')
            
            if memo == '<<main>>':
                self.main_menu()
            else:
                self.data.search_by_memo(memo)
            
            print(self.data.search_results)
            print('\n\nWould you like to save these results? (y/n)')
            y_n = input('>\t')
            
            if y_n == 'y':
                self.data.save_data(self.data.search_results)
            else:
                os.system('cls')
                
    def keyword_search(self):
        os.system('cls')
        while True:
            print('Search by keyword')
            print('Please enter the keyword you\'d like to search by, or "<<main>>" to return to main menu:')
            keyword = input('>\t')
            
            if keyword == '<<main>>':
                self.main_menu()
            else:
                self.data.search_by_description(keyword)
            
            print(self.data.search_results)
            print('\n\nWould you like to save these results? (y/n)')
            y_n = input('>\t')
            
            if y_n == 'y':
                self.data.save_data(self.data.search_results)
            else:
                os.system('cls')
                
    def date_search(self):
        os.system('cls')
        while True:
            print('Search by date')
            print('Please enter the dates you\'d like to search by, or "<<main>>" to return to main menu\n')
            min_date = ''
            max_date = ''
            
            while not min_date:
                print('Minimum Date (mm/dd/yyyy):')
                min_date = self.date_check(input('>\t'))
            
            while not max_date:
                print('Maximum Date (mm/dd/yyyy):')
                max_date = input('>\t')
            
            if min_date == 'na':
                self.data.search_by_date(max_date=max_date)
            elif max_date == 'na':
                self.data.search_by_date(min_date=min_date)
            else:
                self.data.search_by_date(min_date, max_date)
            
            print('\n\nWould you like to save these results? (y/n)')
            y_n = input('>\t')
            
            if y_n == 'y':
                self.data.save_data(self.data.search_results)
            else:
                os.system('cls')
            
    def date_check(self, date):
        if re.search(r'\d{2}/\d{2}/\d{4}', date):
            return re.search(r'\d{2}/\d{2}/\d{4}', date).string
        elif re.search(r'na', date):
            return 'na'
            
    
    def save_directory(self):
        os.system('cls')
        print('Please input save directory using forward slashes:')
        new_save_path = input('>\t')
        self.data.set_save_path(new_save_path)
        self.main_menu()
    
    def close(self):
        os.system('cls')
        print('Are you sure you want to close the program? (y/n)')
        y_n = input('>\t')
        if y_n == 'y':
            exit()
        else:
            self.main_menu()