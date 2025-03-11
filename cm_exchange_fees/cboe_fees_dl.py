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