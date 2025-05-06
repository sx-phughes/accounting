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
sftpUsername, sftpPassword = ('', '')

def get_exchange_fees(year: int, month: int, download_path: str) -> None:
    global year_month 
    year_month = datetime(year, month, 1).strftime('%Y-%m')
    
    global ssh
    ssh = connect_to_ssh()
    download_from_sftp(download_path)
    ssh.close()

    unzipper = UnzipFiles(download_path, download_path)
    unzipper.main(delete_zip=True)

def download_from_sftp(download_path: str) -> None:
    files_to_copy = get_files_to_copy() 
    sftp = ssh.open_sftp()

    for f in files_to_copy:
        fName = f.split('/')[-1]
        sftp.get(f, download_path + '/' + fName)

    sftp.close()
    
def get_files_to_copy() -> list[str]:
    files = []
    for path in file_dict.keys():
        for file_mask in file_dict[path]:
            foundFile = search_for_file(path, file_mask)
            if foundFile:
                files.append(foundFile)
    return files

def search_for_file(path: str, file_pattern: str) -> str:
    search_path = f'{root}{path}{file_pattern}*'
    
    filesToSearch = getFilesInDir(search_path)
    
    curr_files = []
    for f in filesToSearch:
        checkFile(f, curr_files)

    try:
        file = curr_files[-1]
    except IndexError:
        file = None

    return file

def checkFile(fileName: str, curr_files: list):
    date_str1 = year_month
    date_str2 = date_str1.replace('-', '')

    if re.search(date_str1, fileName):
        curr_files.append(fileName)
    elif re.search(date_str2, fileName):
        curr_files.append(fileName)

def getFilesInDir(path: str):
    stdin, stdout, stderr = ssh.exec_command(f'ls {path}')
    stdOutOutput = stdout.read().decode('utf-8')
    
    filesInDir = stdOutOutput.split('\n')

    return filesInDir

def connect_to_ssh() -> paramiko.SSHClient:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    source_ip = 'off2.s'
    un, pw = checkAuth()

    ssh.connect(source_ip, username=un, password=pw)

    return ssh

def checkAuth() -> tuple[str, str]:
    "Check for username and password, set them, and return them"""
    global sftpUsername, sftpPassword
    if not sftpUsername and not sftpPassword:
        sftpUsername = getUsername()
        sftpPassword = getPassword()
        
    return (sftpUsername, sftpPassword)

def getUsername() -> str:
    un = input('Please input off2.s Username:\n>\t')
    return un

def getPassword() -> str:
    pw = input('Please input off2.s Password:\n>\t')
    return pw
