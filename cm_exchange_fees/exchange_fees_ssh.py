import paramiko, re
from patrick_functions.UnzipFiles import UnzipFiles


def get_exchange_fees(year, month, download_path):
    
    if month < 10:
        year_month = str(year) + '-0' + str(month)
    else:
        year_month = str(year) + '-' + str(month)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    source_ip = 'off2.s'
    user = 'sx'
    password = 'oldsx=2insecure'

    print('Connecting to off2.s')
    ssh.connect(source_ip, username=user, password=password)
    print('Connection to off2.s established')

    date_str1 = year_month
    date_str2 = date_str1.replace('-', '')

    root = '/home/simplex'

    file_dict = {'/NASDAQ_SFTP/files/': [i + 'ChargeDetailsBilledAccountReport' for i in ['Gemini', 'MRX', 'PHLX', 'BXOP', 'ISE']],
                '/AMEX_ARCA_S3_SFTP/monthly/': ['SIMPLEX_FEES_PILLAR_AMEX', 'SIMPLEX_ARCA_FEES_PILLAR_ARCA'],
                '/MIAX_SFTP/monthly/': ['SETT_trade_fee', 'pearl_SETT_trade_fee', 'emerald_SETT_trade_fee']}

    files_to_copy = []

    for path in list(file_dict.keys()):
        for file_mask in file_dict[path]:
            search_path = f'{root}{path}{file_mask}*'
            print('Searching ' + search_path)
            stdin, stdout, stderr = ssh.exec_command(f'ls {search_path}')
            f_str = stdout.read().decode('utf-8')
            
            f_list = f_str.split('\n')
            
            curr_files = []
            
            for f in f_list:
                if re.search(date_str1, f):
                    curr_files.append(f)
                    
                elif re.search(date_str2, f):
                    curr_files.append(f)
                    
                else:
                    continue
                
            # print(curr_files[-1].split('/')[-1])
            files_to_copy.append(curr_files[-1])

    print('Connecting SFTP')
    sftp = ssh.open_sftp()
    print('SFTP established')

    for f in files_to_copy:
        f_name = f.split('/')[-1]
        print('Copying ' + f_name + ' to local disk')
        sftp.get(f, download_path + '/' + f_name)

    print('Closing SSH')
    sftp.close()
    ssh.close()

    print('Unzipping and extracting archives...')
    unzipper = UnzipFiles(download_path, download_path)
    unzipper.main(delete_zip=True)
    
    #C:/gdrive/Shared drives/accounting/Simplex Trading/2024/202409/Exchange Fees/Prelim