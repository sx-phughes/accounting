from MonthEnd.ExchangeFees.cboe_fees_dl import get_cboe_fees
from MonthEnd.ExchangeFees.exchange_fees_ssh import get_exchange_fees
        
def ExchangeFeesDownload(year, month, download_path, pull_cboe):
    if pull_cboe == 'y':
        get_cboe_fees(year, month, download_path, True)
    
    get_exchange_fees(year, month, download_path)
