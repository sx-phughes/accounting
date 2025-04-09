import paramiko, re
from datetime import datetime
from patrick_functions.UnzipFiles import UnzipFiles

nasdaqExchanges = ['Gemini', 'MRX', 'PHLX', 'BXOP', 'ISE']
file_dict = {
    '/NASDAQ_SFTP/files/': [
        i + 'ChargeDetailsBilledAccountReport' for i in nasdaqExchanges
    ],
    '/AMEX_ARCA_S3_SFTP/monthly/': [
        'SIMPLEX_FEES_PILLAR_AMEX',
        'SIMPLEX_ARCA_FEES_PILLAR_ARCA'
    ],
    '/MIAX_SFTP/monthly/': [
        'SETT_trade_fee',
        'pearl_SETT_trade_fee',
        'emerald_SETT_trade_fee'
    ]
}
root = '/home/simplex'
sftpUsername, sftpPassword = None, None

def get_exchange_fees(year, month, download_path, un, pw):
    global year_month 
    year_month = datetime(year, month, 1).strftime('%Y-%m')
    
    ssh = connect_to_ssh()
    download_from_sftp(ssh, download_path)
    ssh.close()

    unzipper = UnzipFiles(download_path, download_path)
    unzipper.main(delete_zip=True)

def download_from_sftp(ssh, download_path):
    files_to_copy = get_files_to_copy() 
    sftp = ssh.open_sftp()

    for f in files_to_copy:
        sftp.get(f, download_path + '/' + f_name)

    sftp.close()
    
def get_files_to_copy():
    files = []
    for path in file_dict.keys():
        for file_mask in file_dict[path]:
            foundFile = search_for_file(path, file_mask)
            if foundFile:
                files.append(foundFile)
    return files

def search_for_file(path, file_pattern):
    search_path = f'{root}{path}{file_mask}*'
    
    filesToSearch = getFilesInDir(search_path)
    
    curr_files = []
    for f in f_list:
        checkFile(f)

    try:
        file = curr_files[-1]
    except IndexError:
        file = None

    return file

def checkFile(fileName, curr_files: list):
    date_str1 = year_month
    date_str2 = date_str1.replace('-', '')

    if re.search(date_str1, fileName):
        curr_files.append(f)
    elif re.search(date_str2, fileName):
        curr_files.append(f)

def getFilesInDir(path):
    stdin, stdout, stderr = ssh.exec_command(f'ls {search_path}')
    stdOutOutput = stdout.read().decode('utf-8')
    
    filesInDir = stdOutOutput.split('\n')

    return filesInDir

def connect_to_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    source_ip = 'off2.s'
    un, pw = checkAuth()

    ssh.connect(source_ip, username=un, password=pw)

    return ssh

def checkAuth():
    "Check for username and password, set them, and return them"""
    if sftpUsername is None and sftpPassword is None:
        sftpUsername = getUsername()
        sftpPassword = getPassword()
        
    return (sftpUsername, sftpPassword)

def getUsername():
    un = input('Please input CBOE Username:\n>\t')
    return un

def getPassword():
    pw = input('Please input CBOE Password:\n>\t')
    return pw
