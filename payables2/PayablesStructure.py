import pandas as pd
import os, re, shutil
from datetime import datetime
        
class Invoice():
    _payables_dir = './payables_test_dir'
    vendors = pd.read_csv('C:/gdrive/My Drive/code_projects/payables2/vendors.csv')
    
    def __init__(self, invoiceno, vendor: str, invoicemonth, amount: float, **file_paths: str):
        self.invoiceno = str(invoiceno)
        self.vendor = self.check_vendor(vendor)
        self.uniquename = self.vendor + self.invoiceno
        self.invoicemonth = self.check_file_month(str(invoicemonth))
        self.amount = amount
        self.files: list[str] = []
        
        for i in list(file_paths.keys()):
            self.files.append(file_paths[i])
    
    def __str__(self) -> str:
        return f'Invoice object for {self.uniquename}'
    
    @property
    def vendor(self):
        return self._vendor
    
    @vendor.setter
    def vendor(self, vendor):
        self.uniquename = vendor + self.invoiceno
        self._vendor = vendor
        
    def df_row(self):
        if len(self.files) > 1:
            file_paths = ','.join(self.files)
        else:
            file_paths = self.files[0]
            
        invoice = [self.uniquename,
                   self.invoiceno,
                   self.vendor,
                   int(datetime.today().strftime('%Y%m%d')),
                   self.invoicemonth,
                   self.amount,
                   False,
                   False,
                   '',
                   file_paths]
        
        return invoice
    
    def check_file_month(self, invoicemonth):
        if re.match(r'\d{6}', invoicemonth):
            year = invoicemonth[0:4]
            month = invoicemonth[4:6]
            if re.match(r'20\d{2}', year):
                if int(month) <= 12 and int(month) > 0:
                    return invoicemonth
                else:
                    raise TypeError(f'Invoice month <{invoicemonth}> does not have valid month')
            else:
                raise TypeError(f'Invoice month <{invoicemonth}> does not have valid year')
        else:
            raise TypeError(f'Invoice month <{invoicemonth}> is not formatted in yyyymm')
    
    def organize_files(self):
        # get move-to dir
        # check move-to dir exists
        # if not, make move-to dir
        # create new file name
        # parse old file names, get extensions
        # construct new file names
        # move files to move-to dir
        # set new file paths to filepath in the df
        moveto_folder = str(self.invoicemonth)
        
        if not self.check_move_to_dir(moveto_folder):
            os.mkdir(Invoice._payables_dir + '/' + moveto_folder)
        
        new_file_name_root = self.format_new_file_name(f'{self.uniquename} - {self.invoiceno}')
        
        new_file_names = []
        
        for i in self.files:
            old_file_name = i.split('/')[-1]
            ext = old_file_name.split('.')[-1]
            new_file_name = new_file_name_root + '.' + ext
            new_file_names.append(Invoice._payables_dir + '/' + self.invoicemonth + '/' + new_file_name)
        
        for old, new in zip(self.files, new_file_names):
            shutil.copyfile(old, new)
            
        if len(new_file_names) > 1:
            new_files_string = ','.join(new_file_names)
        else:
            new_files_string = new_file_names[0]
            
        return new_files_string
    
    def check_vendor(self, vendor: str):
        vendors_list = list(self.vendors['Vendor'].values)
        matches = []
        
        for i in vendors_list:
            search = re.search(vendor, i, flags=re.IGNORECASE)
            if search:
                matches.append(search.string)
            else:
                continue
        
        if vendor in matches:
            return vendor
        else:
            print('Did not find exact vendor match\nDid you want to use one of the following?')
            for i in range(len(matches)):
                print(f'{i}: {matches[i]}')
            print('\nIf yes, enter the number of the intended vendor name:')
            selection = int(input('>\t'))
            
            return matches[selection]
    
    def check_move_to_dir(self, invoicemonth):
        if os.path.exists(Invoice._payables_dir + '/' + invoicemonth):
            return True
        else:
            return False
    
    def format_new_file_name(self, new_file_name: str):
        new_file_name = new_file_name.replace('/', '_')
        return new_file_name

class Amendment(Invoice):
    def __init__(self, amending_invoice: Invoice, invoiceno, new_amount: float, **file_paths: str):
        super().__init__(invoiceno, amending_invoice.vendor, amending_invoice.invoicemonth, new_amount, **file_paths)
        self.uniquename = amending_invoice.uniquename
        
    def df_row(self):
        if len(self.files) > 1:
            file_paths = ','.join(self.files)
        else:
            file_paths = self.files[0]
            
        invoice = [self.uniquename,
                   self.invoiceno,
                   self.vendor,
                   int(datetime.today().strftime('%Y%m%d')),
                   self.invoicemonth,
                   self.amount,
                   True,
                   False,
                   '',
                   file_paths]
        
        return invoice

class PayablesTable():
    cols = ['uniqueid', 'invoiceno', 'vendor', 'processdate', 'invoicemonth', 'amount', 'amendment', 'is_paid', 'date_paid','filepaths']
    
    def __init__(self):
        self.payables_table = pd.DataFrame(columns=PayablesTable.cols)
        self.vendors = pd.read_csv('C:/gdrive/My Drive/code_projects/payables2/vendors.csv')
        
    def add_invoice(self, invoice: Invoice):
        index = len(self.payables_table.index)
        data = invoice.df_row()
        self.payables_table.loc[index] = data
        new_paths = invoice.organize_files()
        
        self.payables_table.loc[index, 'filepaths'] = new_paths

    def consolidate_amendments(self, unqiueid):
        invoice_amendments_df = self.payables_table.loc[self.payables_table['uniqueid'] == unqiueid].copy(deep=True)
        invoice_amendments_df = invoice_amendments_df.sort_values(by='processdate', ascending=True)

        current_amount_due = invoice_amendments_df['amount'].values[-1]
        current_date = invoice_amendments_df['processdate'].values[-1]
        pmt_status = invoice_amendments_df['is_paid'].values[-1]
        current_invoice_no = invoice_amendments_df['invoiceno'].values[-1]

        summary_cols = ['invoicedate', 'invoicenumber', 'amount', 'paid']
        self.summary_cols = summary_cols
        summary_values = [current_date, current_invoice_no, current_amount_due, pmt_status]
        summary_data = {i: [j] for i, j in zip(summary_cols, summary_values)}
        if True in summary_data['paid']:
            summary_data['datepaid'] = [invoice_amendments_df['date_paid'].values[-1]]
        
        history_cols = ['date', 'action', 'amount_due']
        dates = [i for i in invoice_amendments_df['processdate'].values]
        actions = []
        for i in invoice_amendments_df['amendment'].values:
            if i == False:
                actions.append('Original invoice received')
            else:
                actions.append('Invoice amended')

        amount_due = [i for i in invoice_amendments_df['amount'].values]
        history_values = [dates, actions, amount_due]
        history_data = {i: j for i, j in zip(history_cols, history_values)}
        history_data = self.add_paid_line(history_data, summary_data)

        return (pd.DataFrame(summary_data), pd.DataFrame(history_data))
    
    def mark_paid(self, uniqueid, datepaid):
        unique_id_mask = self.payables_table['uniqueid'] == uniqueid
        self.payables_table['is_paid'] = self.payables_table['is_paid'].mask(unique_id_mask,True)
        self.payables_table['date_paid'] = self.payables_table['date_paid'].mask(unique_id_mask, datepaid)

    def get_unpaids(self):
        uniquenames = list(self.payables_table['uniqueid'].values)
        unique_uniquenames = []
        
        for i in uniquenames:
            if i not in unique_uniquenames:
                unique_uniquenames.append(i)
        
        summary_cols = self.summary_cols
        summary_df = pd.DataFrame(columns=summary_cols)
        vendors = []
        
        for i in unique_uniquenames:
            i_summary, i_history = self.consolidate_amendments(i)
            summary_df.loc[len(summary_df.index)] = i_summary.loc[0]
            vendor = self.payables_table.loc[self.payables_table['uniqueid'] == i, 'vendor'].values[0]
            vendors.append(vendor)
            
        unpaid_df = summary_df.copy()
        unpaid_df['vendor'] = vendors
        
        return unpaid_df

    def add_paid_line(self, history_data: dict, summary_data: dict):

        if 'datepaid' in list(summary_data.keys()):
            pay_date = summary_data['datepaid'][0]
            paid_line_data = [pay_date, 'Invoice paid', 0.00]
        else:
            return history_data
        
        insert_index = 0
        for i in range(len(history_data['date'])):
            curr_val = history_data['date'][i]
            range_max = len(history_data['date']) - 1
            if i < range_max:
                if pay_date >= curr_val:
                    continue
                else:
                    insert_index = i
            else:
                insert_index = -1
                

        if insert_index > -1:
            for i in range(len(paid_line_data)):
                history_data[list(history_data.keys())[i]].insert(insert_index, paid_line_data[i])
        else:
            for i in range(len(paid_line_data)):
                history_data[list(history_data.keys())[i]].append(paid_line_data[i])

        return history_data
        