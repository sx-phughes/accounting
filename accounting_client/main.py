import login, home, os

def startup():
    os.system('cls')
    print('Welcome to Simplex Accounting Systems v0.1\n')
    print('\n\n\n\n')
    print('Press enter to continue')
    input('')
    logged_in = False
    while not logged_in:
        logged_in = login.log_in_prompt()
    
            
startup()
home.home()