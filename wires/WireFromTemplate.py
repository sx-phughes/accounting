import re, math
from datetime import datetime
import pandas as pd
from Fields import fields

company_ids = {
        'Holdings': '816680961',
        'Investments': '644684771',
        'Technologies': '559711101',
        'Trading': '885007310'
    }
company_names = {
        'Holdings': 'SIMPLEX HOLDINGS LLC',
        'Investments': 'SIMPLEX INVESTMENTS LLC',
        'Technologies': 'SIMPLEX TECHNOLOGIES',
        'Trading': 'SIMPLEX TRADING, LLC'
    }
    
company_abas = {
        'Holdings': '071000013',
        'Investments': '071000013',
        'Technologies': '071000013',
        'Trading': '071000013'
}


company_ids2 = {                        # Company Names
        'Holdings': '9680961001',       # Mishkin 961
        'Investments': '9684771001',    # S I 4771
        'Technologies': '9711101001',   # Simplex 1101
        'Trading': '9007310001'         # Simplex 7310
}

