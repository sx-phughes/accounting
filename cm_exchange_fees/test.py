from cboe_fees_dl import get_cboe_fees
from exchange_fees_ssh import get_exchange_fees

dl = "C:/Users/phugh/Downloads"
yr = 2025
mo = 4

get_cboe_fees(yr, mo, dl)

get_exchange_fees(yr, mo, dl)