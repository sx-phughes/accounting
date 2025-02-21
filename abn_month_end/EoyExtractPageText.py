import os, re, pypdf
import pandas as pd

def get_page_nos(pages: list[pypdf.PageObject]):
    page_nos = []

    for i in range(len(pages)):
        text = pages[i].extract_text()
        str_to_search = '<------------- CASH TITLE ------------> <--- CASH POSITION --> <--- CASH POSITION --> <--- CASH POSITION --> <--- CASH POSITION -->'
        if str_to_search in text:
            page_nos.append(i)

    return page_nos




def get_data_table(f: str, page: pypdf.PageObject):
    text = page.extract_text()
    start_pos = text.find('DAILY POSITION REVIEW PER SUBACCOUNT')
    end_pos = text.find('END-OF-LIST')
    good_text = text[start_pos:end_pos]

    table_by_line = good_text.split('\n')

    # get account
    account_line = table_by_line[3]
    account_match = re.search(r'(ACCOUNT[\s]*:\s)([\d]*\s)([A-Z\d]*)', account_line) 
    account_name = account_match.group(3)
    print('Converting acount {account_name}'.format(account_name=account_name))
    
    # DEBUG
    # print(f'Account Name {account_name}\n')
    # print(good_text)

    # Get line items
    line_item_pattern = r'([\w\s/&()-]+)(\s*)((?<=\s)[\d,]*\.[\d]{2}\s[DC])(\s*)([\d,]*\.[\d]{2}\s[DC])(\s*)([\d,]*\.[\d]{2}\s[DC])(\s*)([\d,]*\.[\d]{2}\s[DC])?'
    table_dict = {
        'Cash Title': [],
        'New': [],
        'Change': [],
        'Old': [],
        'Month to Date': []
    }

    for line in table_by_line:
        # DEBUG
        # print('\n\nSearching line {line}...'.format(line=line[0:20]))

        search = re.search(line_item_pattern, line)
        if search:
            # DEBUG
            # print(f'account {account_name} found line {search.string}')

            relevant_groups = [1,3,5,7,9]
            for i in range(len(table_dict.keys())):
                table_dict[list(table_dict.keys())[i]].append(search.group(relevant_groups[i]))
        else:
            continue
            # print('No match found\n\n')

    for num_col in ['New', 'Change', 'Old', 'Month to Date']:
        nums_list = []
        for val in table_dict[num_col]:
            if not val:
                num_val = 0
            elif 'C' in val:
                num_val = round(float(val.replace(' C', '').replace(',','')),2)
            else:
                num_val = float(val.replace(' D', '').replace(',','')) * -1

            nums_list.append(num_val)
        
        table_dict[num_col] = nums_list
            
    
    df = pd.DataFrame(table_dict)
    df['Account'] = account_name
    cols = list(df.columns)
    cols.remove('Account')
    cols.insert(0, 'Account')
    df = df[cols]
    df['f_name'] = f

    df['Cash Title'] = df['Cash Title'].str.strip()

    return df