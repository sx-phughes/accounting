import cboe_fees_dl
from exchange_fees_ssh import get_exchange_fees

dl = "C:/Users/Patrick/Downloads"
yr = 2025
mo = 4

cboe_fees_dl.get_cboe_fees(yr, mo, dl, True)

# get_exchange_fees(yr, mo, dl)