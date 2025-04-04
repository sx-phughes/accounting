<<<<<<< HEAD
import requests
import re
import os
import pandas as pd
from datetime import datetime


# Global Variable Declarations
exchanges = ( 'ZO', 'XO', 'C1', 'C2' )
exchangeUrlIdentifiers = ( 'opt','exo','cone','ctwo' )
exchangeDescriptions = ( 
    'BZX Options',
    'EDGX Options',
    'CBOE Options',
    'C2 Options'
)
mpidUrl = 'https://files.catnmsplan.com/firm-data/IMID_Daily_List.txt'
mpidFileName = 'all_exch_mpids.csv'
suffixes = ('', 'a')
cboeUsername, cboePassword = None

def get_cboe_fees(year: int, month: int, download_path: str):
    """Download CBOE Exchange Fee Files

    Params:
        year: int, year to get invoices from
        month: int, month to get invoices from
        download_path: str, path to save invoices to

    Returns: None
    """
    global downloadPath = download_path

    global moyr = getMonthYear(year, month)
        
    updateExchangeCodes()

    mpids = uniqueSxMpids()

    getInvoices(mpids)


def getInvoices(mpids: list):
    """Download CBOE Invoices for given list of MPIDs"""
    for exch in exchanges:
        getInvoicesByExchange(mpids, exch)

def getInvoicesByExchange(exchangeCode, mpids):
    """Download invoices from a specific CBOE exchange for a list of MPIDs"""
    for mpid in mpids:
        getInvoicesBySuffix(exchangeCode, mpid)

def getInvoicesBySuffix(exchangeCode, mpid):
    """Download invoices for a given CBOE exchange and MPID"""
    for suffix in suffixes:
        downloadInvoice(mpid, exchangeCode, suffix) 

def downloadInvoice(mpid, exchangeCode, suffix):
    """Download fees invoice for a specific MPID and CBOE exchange with a
    potential suffix
    """
    fileName = constructInvoiceName(mpid, exchangeCode, suffix)
    url = constructUrl(exchangeCode)
    un, pw = checkAuth()

    file = makeRequest(url, fileName, un, pw)
    if file:
        save_file(file)

def constructInvoiceName(mpid, exchangeCode, suffix):
    return mpid + moyr + suffix + '-' + exchangeCode

def constructUrl(code):
    exchangeUrlId = exchangeUrlIdentifiers[exchanges.index(code)]
    exchangeUrl = f'https://www.batstrading.com/{exchangeUrlID}/account/files/\
            invoice/'
    return exchangeUrl

def makeRequest(url, invoice, un, pw):
    """Make HTTP request for an invoice"""
    response = requests.get(url + invoice, auth=(un, pw))

    if response.status_code == 200:
        return response.content
    else:
        return None

def checkAuth():
    "Check for username and password, set them, and return them"""
    if cboeUsername is None and cboePassword is None:
        global cboeUsername
        cboeUsername = getUsername()
        global cboePassword
        cboePassword = getPassword()
        
    return (cboeUsername, cboePassword)

def getUsername():
    un = input('Please input CBOE Username:\n>\t')
    return un

def getPassword():
    pw = input('Please input CBOE Password:\n>\t')
    return pw

def saveFile(fileObject, fileName):
    with open(downloadPath + '/' + fileName) as f:
        f.write(fileObject)

def getMonthYear(year, month):
    return datetime(year, month, 1).strftime('%m%Y')

def updateMpids()
    """Update Simplex MPID listing and write to disk"""
    mpidsData = getNewMpids()
    print('Updating CBOE MPIDs data...')
    writeNewMpids(mpidsData)

def writeNewMpids(mpidsData):
    with open(mpidFileName, 'wb') as file:
        file.write(exchangeCodes)

def getNewMpids():
    response = requests.get(mpidUrl)
    return response.content

def uniqueSxMpids():
    """Return a list of unique Simplex MPIDs used on CBOE"""
    allValues = getSxMpidsList()
    uniqueValues = []
    for val in allValues:
        if val not in uniqueValues:
            uniqueValues.append(val)

    return uniqueValues

def getSxMpidsList()
    sxMpids = getSxMpids()
    return sxMpids['IMID'].values.to_list() 

def getSxMpids()
    cboeMpids = getCboeMpids()
    sxMask = (cboeMpids['firmName'] == 'SIMPLEX TRADING LLC')
    sxMpids = cboeMpids.loc[sxMask]
    return sxMpids.copy()

def getCboeMpids()
    mpids = pd.read_csv(mpidFileName, sep='|')
    cboeExchangeCodes = ['BZXOP', 'EDGXOP', 'CBOE', 'C2']
    cboeMask = (mpids['exchangeID'].isin(cboeExchangeCodes))
    cboe = mpids.loc[cboeMask]
    return cboe.copy()
=======
import requests, re, os
import pandas as pd
from datetime import datetime

def get_old_mpids(curr_year, curr_month):
    months = range(1,13)[:(curr_month-1)]
    moyrs_to_search = [datetime(curr_year, month, 1).strftime('%Y%m') for month in months]
    path = 'C:/gdrive/Shared drives/accounting/Simplex Trading/2025/Exchange Fees/{moyr}/Prelim'
    file_pattern = r'([A-Z]{4})\d{4}a?-([ZO|XO|C1|C2])\.csv'
    
    exch_codes = ['ZO', 'XO', 'C1', 'C2']
    mpid_dict = {exch: [] for exch in exch_codes}
    
    for moyr in moyrs_to_search:
        for file in os.listdir(path.format(moyr=moyr)):
            match = re.match(file_pattern, file)
            if match:
                mpid_dict[match.group(2)].append(match.group(1))
            else:
                continue
            
    return exch_codes

def get_file(url, invoice, un, pw):
    a_invoice = invoice.split('-')
    a_invoice[0] = a_invoice[0]+'a'
    a_invoice = '-'.join(a_invoice)
    
    orig_response = requests.get(url + invoice, auth=(un, pw))
    a_response = requests.get(url + a_invoice, auth=(un, pw))
    
    if orig_response.status_code == 200:
        invoice_name = invoice
        response_obj = orig_response
    elif a_response.status_code == 200:
        invoice_name = a_invoice
        response_obj = a_response
    else:
        return (None, None)
    
    return (invoice_name, response_obj)

def save_file(dl_path, fname, http_response):
    print('Downloading ' + fname)
                
    with open(dl_path + '/'+ fname, 'wb') as file:
        file.write(http_response.content)

def get_cboe_fees(year, month, download_path, un, pw):
    moyr = datetime(year, month, 1).strftime('%m%y')
        
    exch_codes_url = 'https://files.catnmsplan.com/firm-data/IMID_Daily_List.txt'

    response = requests.get(exch_codes_url)
    print('Getting current list of CBOE MPIDs...')
    with open('all_exch_mpids.csv', 'wb') as file:
        file.write(response.content)
        
    exch_codes = pd.read_csv('all_exch_mpids.csv', sep='|')
    cboe_codes = exch_codes[exch_codes['exchangeID'].isin(['BZXOP', 'EDGXOP', 'CBOE', 'C2'])]
    sx_codes = cboe_codes[cboe_codes['firmName'] == 'SIMPLEX TRADING, LLC']

    codes = sx_codes['IMID'].values

    mpids = []
    for i in codes:
        if i not in mpids:
            mpids.append(i)
        else:
            continue

    zo_url = 'https://www.batstrading.com/opt/account/files/invoice/'
    xo_url = 'https://www.batstrading.com/exo/account/files/invoice/'
    c1_url = 'https://www.batstrading.com/cone/account/files/invoice/'
    c2_url = 'https://www.batstrading.com/ctwo/account/files/invoice/'

    exch_codes = ['ZO', 'XO', 'C1', 'C2']
    urls = [zo_url, xo_url, c1_url, c2_url]
    
    invoices = {code: {'url': url, 'inv': [], 'downloaded': []} for code, url in zip(exch_codes, urls)}

    # print('Fetching prior month MPIDS...')
    # pm_mpids = get_old_mpids(year, month)
    # file_count = 0
    
    # for exch in pm_mpids.keys():
    #     url = invoices[exch]['url']
        
    #     for mpid in pm_mpids[exch]:
    #         inv = mpid + moyr + '-' + exch + '.csv'
    #         fname, response = get_file(url, inv, un, pw)

    #         if fname:
    #             save_file(download_path, fname, response)
    #             invoices[exch]['downloaded'].append(inv)
    #             file_count += 1
    #         else:
    #             continue
                
    # if sum([len(pm_mpids[exch] for exch in exch_codes)]) == file_count:
    #     return True
    
    print('Creating list of invoices to search...')
    for code in exch_codes:
        invoices[code] = [f'{id}{moyr}-{code}.csv' for id in mpids]

    exchange_code_dict = {'ZO': 'BZX Options',
                          'XO': 'EDGX Options',
                          'C1': 'CBOE Options',
                          'C2': 'C2 Options'}
    
    for exch_code in invoices.keys():
        curr_url = invoices[exch_code]['url']
        
        print(f'Searching for {exchange_code_dict[exch_code]} invoices...')
        
        for invoice in invoices[exch_code]['inv']:
            invoice_name, response = get_file(curr_url, invoice, un, pw)
            
            if invoice_name:
                save_file(download_path, invoice_name, response)
>>>>>>> 9325cd371a8bd70a67527f7fe426df02c9ee9e04
