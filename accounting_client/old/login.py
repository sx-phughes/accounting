from datetime import datetime
import os, csv, hashlib, getpass, time
   
def create_account():
    print('Please input your desired username:')
    un = input('>>>\t')
    gtg = False
    while not gtg:
        print(f'Is this correct: {un} (y/n)')
        yn = input('>>>\t')
        
        if yn == 'y':
            gtg = True
        elif yn == 'n':
            print('Please input another username:')
            un = input('>>>\t')
        else:
            print('The option you\'ve selected is invalid.')
    
    print('Please input your desired password:')
    pw = getpass.getpass('>>>\t')
    print('Please input your desired password again:')
    pw2 = getpass.getpass('>>>\t')

    gtg = False
    while not gtg:
        if pw == pw2:
            gtg = True
        else:
            gtg = False
            print('The passwords you entered do not match.')
            print('Please try again.')
            print('Please input your desired password:')
            pw = getpass.getpass('>>>\t')
            print('Please input your desired password again:')
            pw2 = getpass.getpass('>>>\t')
    
    for i in range(4):
        print('\n')
    
    print('Your account is being created...')
    print('Please wait.')
    
    un = bytes(un, 'utf-8')
    pw = bytes(pw, 'utf-8')
    
    hashed = hashlib.sha512()
    hashed.update(un)
    hashed.update(pw)
    
    headers = ['hash']
    if not os.path.exists('./lib/hashes.csv'):
        with open('./lib/hashes.csv', 'x') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
    
    with open('./lib/hashes.csv', 'a') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writerow({'hash': hashed.hexdigest()})
        
    print('Your account has been created. Please log in.')
        
def log_in():
    os.system('cls')
    logged_in = False
    tries = 0
    while not logged_in:
        print('Username:')
        un = input('>>>\t')
        print('Password:')
        pw = getpass.getpass('>>>\t')
        
        hashed = hashlib.sha512()
        
        un = bytes(un, 'utf-8')
        pw = bytes(pw, 'utf-8')
        
        hashed.update(un)
        hashed.update(pw)
        
        with open('./lib/hashes.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['hash'] == hashed.hexdigest():
                    logged_in = True
                    break
                else:
                    continue
            
            if not logged_in:
                tries += 1
                display = 3 - tries
                print('Your username and password didn\'t match any we have on file.')
                print('Please try again.')
                print(f'Warning: You have {display} more tries until the system locks for 1 hour')
                
            if tries >= 3:
                print('You\'ve failed to enter a correct username and password combination three times now.')
                print('Three tries is the maximum number of allowable attempts.')
                print('\nThis program will now abort')
                for i in range(5,0,-1):
                    print(i)
                    time.sleep(1)
                exit()
    
    return logged_in

def log_in_prompt():
    os.system('cls')
    good_choice = False
    while not good_choice:
        print('Log-in (1) or create account (2)?')
        print('Please enter the number for the option you\'d like')
        choice = int(input('>>>\t'))
        
        if choice == 1:
            logged_in = log_in()
            good_choice = True
            pass
        elif choice == 2:
            create_account()
        else:
            print('The choice you\'ve made is not an option.')
            print('Please select again.')
            choice = input('>>>\t')
            
    return logged_in

def create_log_in_file():
    if not os.path.exists('./lib/logins.csv'):
        with open('./lib/logins.csv', 'x') as f:
            fieldnames = ['指数', '时间']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()

def log_login():
    with open ('./lib/logins.csv', 'a') as log:
        reader = csv.DictReader(log)
        x = 0
        for row in reader:
            x += 1
        writer = csv.DictWriter(log)
        writer.writerow({'指数': x, '时间': datetime.now().strftime('%d/%m/%Y, %H:%M:%S')})

def get_last_login():
    with open('./lib/logins.csv', 'r') as log:
        reader = csv.DictReader(log)
        for row in reader:
            last_time = row['时间']
            
    return last_time