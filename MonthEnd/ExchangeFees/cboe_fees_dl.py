import requests
import re
import pandas as pd
import os
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
global debug
debug = False

def debugger(to_print: any) -> None:
    if debug:
        print(to_print)

def get_cboe_fees(year: int, month: int, download_path: str, debugger_on: bool):
    """Download CBOE Exchange Fee Files

    Params:
        year: int, year to get invoices from
        month: int, month to get invoices from
        download_path: str, path to save invoices to

    Returns: None
    """
    global debug
    debug = debugger_on 

    global downloadPath
    downloadPath = download_path

    global moyr 
    moyr = getMonthYear(year, month)
        
    updateMpids()
    debugger("Updated Mpids")

    mpids = uniqueSxMpids()

    getInvoices(mpids)


def getInvoices(mpids: list):
    """Download CBOE Invoices for given list of MPIDs"""
    for exch in exchanges:
        debugger(f"Getting invoices for {exch}...")
        getInvoicesByExchange(mpids, exch)

def getInvoicesByExchange(mpids: list, exchangeCode: str):
    """Download invoiices from a specific CBOE exchange for a list of MPIDs"""
    for mpid in mpids:
        debugger(f"Getting invoices for MPID {mpid}")
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
    debugger(fileName)
    url = constructUrl(exchangeCode)
    un, pw = checkAuth()

    file = makeRequest(url, fileName, un, pw)
    if file:
        debugger(f"Found invoice {fileName}, saving to disk...")
        saveFile(file, fileName)

def constructInvoiceName(mpid, exchangeCode, suffix):
    return mpid + moyr + suffix + '-' + exchangeCode + '.csv'

def constructUrl(code):
    global exchangeUrlIdentifiers, exchanges
    exchangeUrlId = exchangeUrlIdentifiers[exchanges.index(code)]
    exchangeUrl = \
    f'https://www.batstrading.com/{exchangeUrlId}/account/files/invoice/'
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
    global cboeUsername, cboePassword
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
    with open(downloadPath + '/' + fileName, 'wb') as f:
        f.write(fileObject)

def getMonthYear(year, month):
    return datetime(year, month, 1).strftime('%m%y')

def updateMpids():
    """Update Simplex MPID listing and write to disk"""
    mpidsData = getNewMpids()
    debugger('Updating CBOE MPIDs data...')
    writeNewMpids(mpidsData)

def writeNewMpids(mpidsData):
    # print(os.getcwd())
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
    sxMask = (cboeMpids['firmName'].str.contains(
        "SIMPLEX",
        flags=re.IGNORECASE
        )) 
    sxMpids = cboeMpids.loc[sxMask]
    return sxMpids.copy()

def getCboeMpids():
    mpids = pd.read_csv(mpidFileName, sep='|')
    cboeExchangeCodes = ['BZXOP', 'EDGXOP', 'CBOE', 'C2']
    cboeMask = (mpids['exchangeID'].isin(cboeExchangeCodes))
    cboe = mpids.loc[cboeMask]
    return cboe.copy()
