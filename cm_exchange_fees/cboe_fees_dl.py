import requests
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
cboeUsername, cboePassword = None, None

def get_cboe_fees(year: int, month: int, download_path: str):
    """Download CBOE Exchange Fee Files

    Params:
        year: int, year to get invoices from
        month: int, month to get invoices from
        download_path: str, path to save invoices to

    Returns: None
    """
    global downloadPath
    downloadPath = download_path

    global moyr 
    moyr = getMonthYear(year, month)
        
    updateMpids()

    mpids = uniqueSxMpids()

    getInvoices(mpids)


def getInvoices(mpids: list):
    """Download CBOE Invoices for given list of MPIDs"""
    for exch in exchanges:
        getInvoicesByExchange(mpids, exch)

def getInvoicesByExchange(mpids: list, exchangeCode: str):
    """Download invoices from a specific CBOE exchange for a list of MPIDs"""
    for mpid in mpids:
        getInvoicesBySuffix(exchangeCode, mpid)

def getInvoicesBySuffix(exchangeCode: str, mpid: str):
    """Download invoices for a given CBOE exchange and MPID"""
    for suffix in suffixes:
        downloadInvoice(mpid, exchangeCode, suffix) 

def downloadInvoice(mpid: str, exchangeCode: str, suffix: str):
    """Download fees invoice for a specific MPID and CBOE exchange with a
    potential suffix
    """
    fileName = constructInvoiceName(mpid, exchangeCode, suffix)
    url = constructUrl(exchangeCode)
    un, pw = checkAuth()

    file = makeRequest(url, fileName, un, pw)
    if file:
        saveFile(file)

def constructInvoiceName(mpid, exchangeCode, suffix):
    return mpid + moyr + suffix + '-' + exchangeCode

def constructUrl(code):
    exchangeUrlId = exchangeUrlIdentifiers[exchanges.index(code)]
    exchangeUrl = f'https://www.batstrading.com/{exchangeUrlId}/account/files/\
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
        cboeUsername = getUsername()
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

def updateMpids():
    """Update Simplex MPID listing and write to disk"""
    mpidsData = getNewMpids()
    print('Updating CBOE MPIDs data...')
    writeNewMpids(mpidsData)

def writeNewMpids(mpidsData):
    with open(mpidFileName, 'wb') as file:
        file.write(mpidsData)

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

def getSxMpidsList():
    sxMpids = getSxMpids()
    return sxMpids['IMID'].values.tolist() 

def getSxMpids():
    cboeMpids = getCboeMpids()
    sxMask = (cboeMpids['firmName'] == 'SIMPLEX TRADING LLC')
    sxMpids = cboeMpids.loc[sxMask]
    return sxMpids.copy()

def getCboeMpids():
    mpids = pd.read_csv(mpidFileName, sep='|')
    cboeExchangeCodes = ['BZXOP', 'EDGXOP', 'CBOE', 'C2']
    cboeMask = (mpids['exchangeID'].isin(cboeExchangeCodes))
    cboe = mpids.loc[cboeMask]
    return cboe.copy()
