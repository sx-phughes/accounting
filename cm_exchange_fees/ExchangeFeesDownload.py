from cm_exchange_fees.cboe_fees_dl import get_cboe_fees
from cm_exchange_fees.exchange_fees_ssh import get_exchange_fees
        
def ExchangeFeesDownload(year, month, download_path, pull_cboe):
    if pull_cboe == 'y':
        get_cboe_fees(year, month, download_path)
    
    get_exchange_fees(year, month, download_path)
