from abc import ABC
from payables.vars import *

class Invoice(ABC):
    def __init__(self, name, PayableSession):
        self._session = PayableSession
        self.f_name = name
        self.files = []
        self._filenum = 1
    
    def data_entry(self):
        print('Please input invoice information below: ')
        vendor = input('Vendor: ')
        inv_num = input('Invoice Number: ')
        inv_date = input('Invoice Date (yyyy-mm-dd): ')
        inv_amt = input('Invoice Amount: ')
        inv_type = input('Input invoice type (invoice, broker, or cc): ')

        self.input_data(vendor=vendor, invoice_number=inv_num, invoice_date=inv_date, amount=inv_amt, inv_type=inv_type)
    
    def input_data(self, vendor, invoice_number, invoice_date, amount, inv_type):
        self.vendor = vendor
        self.inv_num = invoice_number
        self.inv_date = invoice_date
        self.amount = amount
        self.type = inv_type
        self.new_file_pattern = f'{self.vendor} - {self.inv_num}'
    
        self.save_path = self._session.folder_paths[inv_type]
        self.new_full_path = self.save_path + '/' + self.new_file_pattern
        
    def df_format(self):
        file_path_list = [f['path'] for f in self.files]
        if len(file_path_list) > 1:
            file_paths = ','.join(file_path_list)
        else:
            file_paths = file_path_list[0]

        needed_data = [self.vendor, self.inv_num, self.inv_date, self.amount, file_paths]
        return needed_data
    
    def add_file(self, file_path:str):
        ext = file_path.split('.')[-1]
        num = self._filenum
        
        file_dict = {
            'path': file_path,
            'ext': ext,
            'new_name': self.new_file_pattern + f'_{str(num)}'
        }
        self.files.append(file_dict)
        
        self._filenum += 1
    
    def __repr__(self):
        if self.vendor:
            return f'{self.Vendor} - {self.inv_num} - ${self.amount}'
        else:
            return f'Unnamed invoice {self.f_name}'

                    
def invoice_constructor(invoice_obj: Invoice):
    print('Please input invoice information below: ')
    vendor = input('Vendor: ')
    inv_num = input('Invoice Number: ')
    inv_date = input('Invoice Date (yyyy-mm-dd): ')
    inv_amt = input('Invoice Amount: ')
    inv_type = input('Input invoice type (invoice, broker, or cc): ')
    
    invoice_obj.input_data(vendor=vendor, invoice_number=inv_num, invoice_date=inv_date, amount=inv_amt, inv_type=inv_type)
    
    return invoice_obj

    
# class NormalInvoice(Invoice):
#     def __init__(self, name, full_path, PayableSession):
#         super().__init__(name, full_path, PayableSession)
#         self.save_path = self._session.folder_paths['invoice']

# class BrokerInvoice(Invoice):
#     def __init__(self, vendor, invoice_number, invoice_date, amount, path):
#         pass        
        