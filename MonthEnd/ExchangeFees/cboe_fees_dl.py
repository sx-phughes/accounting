import requests
import re
import pandas as pd
import os
from datetime import datetime


# Global Variable Declarations
exchanges = ("ZO", "XO", "C1", "C2")
exchangeUrlIdentifiers = ("opt", "exo", "cone", "ctwo")
exchangeDescriptions = (
    "BZX Options",
    "EDGX Options",
    "CBOE Options",
    "C2 Options",
)
mpidUrl = "https://files.catnmsplan.com/firm-data/IMID_Daily_List.txt"
mpidFileName = "all_exch_mpids.csv"
suffixes = ("", "a")
cboeUsername, cboePassword = None, None
global debug
debug = False


def debugger(to_print: any) -> None:
    if debug:
        print(to_print)


def get_cboe_fees(
    year: int, month: int, download_path: str, debugger_on: bool
):
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
    moyr = datetime(year, month, 1).strftime("%m%y")

    updateMpids()
    debugger("Updated Mpids")

    mpids = getSxMpids()

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
        with open(downloadPath + "/" + fileName, "wb") as f:
            f.write(file)


def constructInvoiceName(mpid, exchangeCode, suffix):
    """Constructor for invoice file names."""

    return mpid + moyr + suffix + "-" + exchangeCode + ".csv"


def constructUrl(code):
    """Construct URL for HTML request."""

    global exchangeUrlIdentifiers, exchanges
    exchangeUrlId = exchangeUrlIdentifiers[exchanges.index(code)]
    exchangeUrl = (
        f"https://www.batstrading.com/{exchangeUrlId}/account/files/invoice/"
    )
    #     https://www.batstrading.com/opt/            account/files/invoice/SIMA1025-ZO.csv
    return exchangeUrl


def makeRequest(url, invoice, un, pw):
    """Make HTTP request for an invoice"""

    full_url = url + invoice
    response = requests.get(full_url, auth=(un, pw))
    my_req = requests.Request("GET", full_url, auth=(un, pw))
    if invoice == "SIMA1025-ZO.csv":
        prepped = my_req.prepare()
        print(prepped.url)

    if (
        response.status_code
        == 200
        # and b"<!DOCTYPE html>" not in response.content
    ):
        return response.content
    else:
        return None


def checkAuth():
    """Check for username and password, set them, and return them."""

    global cboeUsername, cboePassword
    if cboeUsername is None and cboePassword is None:
        cboeUsername = input("Please input CBOE Username:\n>\t")
        cboePassword = input("Please input CBOE Password:\n>\t")

    return (cboeUsername, cboePassword)


def updateMpids():
    """Update Simplex MPID listing and write to disk."""

    mpidsData = requests.get(mpidUrl)
    debugger("Updating CBOE MPIDs data...")
    with open(mpidFileName, "wb") as file:
        file.write(mpidsData.content)


def getSxMpids() -> pd.DataFrame:
    """Returns a list of unique Simplex MPIDs used on CBOE exchanges."""

    cboeMpids = getCboeMpids()
    sxMask = cboeMpids["firmName"].str.contains("SIMPLEX", flags=re.IGNORECASE)
    sxMpids = cboeMpids.loc[sxMask]
    uniqueMpids = sxMpids["IMID"].unique().tolist()
    return uniqueMpids


def getCboeMpids() -> pd.DataFrame:
    """Filters file of all MPIDS to those used on CBOE."""

    mpids = pd.read_csv(mpidFileName, sep="|")
    cboeExchangeCodes = ["BZXOP", "EDGXOP", "CBOE", "C2"]
    cboeMask = mpids["exchangeID"].isin(cboeExchangeCodes)
    cboe = mpids.loc[cboeMask]
    return cboe.copy()
