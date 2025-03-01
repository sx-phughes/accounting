from FileGrabber import AbnFileGrabber
import shutil, os, re
import pandas as pd

def rename_files():
    dir_path = 'C:/gdrive/Shared drives/accounting/Simplex Trading/Audit/2024/JE Selections/2 - Seldom Use/ABN Monthly Statements'

    strategy_mapping = pd.read_csv('C:/gdrive/Shared drives/accounting/patrick_data_files/abn_month_end/ABN_account_mapping.csv')
    year = 2024

    big_month_grabber = AbnFileGrabber(year, 12)
    print('Getting account-to-file mapping...')
    account_mapping = big_month_grabber.get_account_file_mapping()

    renamer = {account_no[0] + '_' + account_no[1]: file_index for file_index, account_no in account_mapping.items()}
    # print(renamer)
    # print(f'renamer length: {str(len(renamer.keys()))}')

    # input()

    f_pattern = r'(\d{8})[\w_\d]*([A-Z]{4})_(\d{10})_DPR_SU.pdf'
    # Date = 1
    # Margin type = 2
    # ABN Account Code = 3

    pwd = os.getcwd()

    os.chdir(dir_path)

    for file in os.listdir():
        search = re.search(f_pattern, file)

        if search:
            date = search.group(1)
            margin_type = search.group(2)
            account_index = search.group(3)
            account_no = renamer[margin_type + '_' + account_index]

            account_strategy_i = strategy_mapping.loc[strategy_mapping['ACCOUNT'] == account_no, 'Strategy'].index[0]
            account_strategy = strategy_mapping.iloc[account_strategy_i, 1]


            new_name = f'{date}_{account_strategy}_{account_no}_Monthly Statement.pdf'

            shutil.move(file, new_name)

    os.chdir(pwd)

def grab_files():
    files_to_grab = {
        1: ['695CS1U', '695CS5Q', '695CS2M', '695CS3S', '695CS2P', '695CS8R', '695C10S', '695CS00', '8131SICSH'], # 9
        2: ['695CS9S', '695M622', '695M679', '695MMXZ', '8131SIMP7', '813M473'], # 6
        8: ['695CS9S'], # 1
        9: ['695CS1U', '695CS5Q', '695CS2M', '695CS3S', '695CS2P', '695CS8R'], # 6
        11: ['695M622', '695M679', '695MMXZ', '8131SIMP7', '813M473', '695M915', '6901SIMP9'], # 7
        12: ['695M915', '6901SIMP9', '695C10S', '695CS00', '8131SICSH'] # 5
    } # 34 account statements

    year = 2024
    copy_dir = 'C:/Users/phugh/Downloads'

    max_month = max(list(files_to_grab.keys()))
    print(f'\nMax month is {max_month}\n')

    big_month_grabber = AbnFileGrabber(year, max_month)
    print('Getting account-to-file mapping...')
    account_mapping = big_month_grabber.get_account_file_mapping()
    for i in account_mapping.keys():
        print(f'Account {i} has file index {account_mapping[i][0]}_{account_mapping[i][1]}')

    for month in files_to_grab.keys():
        print(f'\n\nInitializing file grabber for {year}-{month}')
        grabber = AbnFileGrabber(year, month)

        for account in files_to_grab[month]:
            print(f'\nGetting statement name for account {account}')
            stmt_path, stmt_f_name = grabber.get_abn_pdf_monthly_statement(account, account_mapping)

            src_path = stmt_path + '/' + stmt_f_name
            dest_path = copy_dir + '/' + stmt_f_name

            print(f'Copying file {stmt_f_name} from {stmt_path} to {copy_dir}')

            if stmt_f_name:
                shutil.copy(src_path, dest_path)
                print('File copied')
            else:
                print(f'File for account {account} in month {month} not found')


rename_files()