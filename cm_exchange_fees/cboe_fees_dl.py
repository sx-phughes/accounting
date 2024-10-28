import requests
import pandas as pd

def get_cboe_fees(year, month, download_path):
    
    if month < 10:
        moyr = '0' + str(month) + str(year)[-2:]
    else:
        moyr = str(month) + str(year)[-2:]
        
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

    invoices = {'ZO': {'url': zo_url,
                    'inv': []},
                'XO': {'url': xo_url,
                    'inv': []},
                'C1': {'url': c1_url,
                    'inv': []},
                'C2': {'url': c2_url,
                    'inv': []}
                }

    print('Creating list of invoices to search...')
    for id in mpids:
        for code in exch_codes:
            invoice = f'{id}{moyr}-{code}.csv'
            invoices[code]['inv'].append(invoice)

    exchange_code_dict = {'ZO': 'BZX Options',
                          'XO': 'EDGX Options',
                          'C1': 'CBOE Options',
                          'C2': 'C2 Options'}
    
    for code in list(invoices.keys()):
        curr_url = invoices[code]['url']
        
        print(f'Searching for {exchange_code_dict[code]} invoices...')
        
        for invoice in invoices[code]['inv']:
            a_invoice = invoice.split('-')
            a_invoice[0] = a_invoice[0]+'a'
            a_invoice = '-'.join(a_invoice)
            
            orig_response = requests.get(curr_url + invoice, auth=('cchiu@simplexinvestments.com', 'simplex123*'))
            a_response = requests.get(curr_url + a_invoice, auth=('cchiu@simplexinvestments.com', 'simplex123*'))
            
            if orig_response.status_code == 200:
                good_invoice = invoice
                good_response = orig_response
            elif a_response.status_code == 200:
                good_invoice = a_invoice
                good_response = a_response
            else:
                continue
            
            print('Downloading ' + good_invoice)
                
            with open(download_path + '/'+ good_invoice, 'wb') as file:
                file.write(good_response.content)