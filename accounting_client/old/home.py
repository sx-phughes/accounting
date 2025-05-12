import os, time

def home():
    os.system('cls')
    get_option()
    
def print_options(return_num: bool = False):
    options = {1: 'Make Journal Entry',
               2: 'Input Invoice',
               3: 'Run Report',
               4: 'Log Out'}
    
    if return_num:
        return len(options)
    else:
        for key, val in options.items():
            print(f'{str(key)}. {val}')

def get_option():
    gtg = False
    while not gtg:
        os.system('cls')
        print_options()
        print('Please select an option from the above list')
        print('Input the number of the option you\'d like and hit enter.')
        acceptable_answers = range(1, print_options(True)+1)
        option = int(input('>>>\t'))
        if option in acceptable_answers:
            print('That option is still in dev.')
            # change to true to move on
            gtg = False
        else:
            print('That option is not acceptable.')
            time.sleep(7)
            gtg = False
    
    return option