from cm_exchange_fees.cboe_fees_dl import get_cboe_fees
from cm_exchange_fees.exchange_fees_ssh import get_exchange_fees
        
def ExchangeFeesDownload(year, month, download_path, pull_cboe, cboe_un, cboe_pw, off2s_un, off2s_pw):
    if pull_cboe:
        get_cboe_fees(year, month, download_path, cboe_un, cboe_pw)
    
    get_exchange_fees(year, month, download_path, off2s_un, off2s_pw)