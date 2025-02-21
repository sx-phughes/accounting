from NachaLine import *
import math

class TransactionEntry():
    def __init__(self, vendor, amount, invoice_number, vendor_aba, vendor_account, sequence_no):
        self.no_decimal_amount = self.no_decimal(amount)
        self.transaction_line = TransactionLine(
            trx_code = 22,
            rec_aba = vendor_aba,
            dfi_acct = vendor_account,
            amount = self.no_decimal_amount,
            rec_co_name = vendor,
            addenda_indicator = '1',
            entry_seq_no = sequence_no
        )
        self.addenda_line = AddendaLine(
            payment_info=invoice_number,
            entry_seq_no=sequence_no,
            vendor = vendor
        )
        
    def __str__(self):
        return self.transaction_line.__str__() + '\n' + self.addenda_line.__str__()
    
    def no_decimal(self, amount):
        amount = float(amount)
        amount = str(amount)
        whole, decimal = amount.split('.')
        while len(decimal) < 2:
            decimal += '0'
            
        no_dot_amount = int(whole + decimal)
        
        return no_dot_amount

class Batch():
    def __init__(self, company_name, company_id, co_entry_descr, effective_date, orig_dfi_id, batch_number, trx_entries: list[TransactionEntry]):
        self.trx_entries = trx_entries
        
        self.header_line = BatchHeaderLine(
            service_class_code='220',
            company_name=company_name,
            company_id=company_id,
            std_entry_class='CCD',
            company_entry_description=co_entry_descr,
            effective_date=effective_date,
            orig_dfi_id=orig_dfi_id,
            batch_number=batch_number
        )
        
        self.num_lines = 2 * len(trx_entries)
        
        self.footer_line = BatchFooterLine(
            svc_class_code='220',
            entry_addenda_count = self.num_lines,
            entry_hash=self.hash(),
            total_credits=0,
            total_debits=self.sum_debits(),
            co_id=company_id,
            orig_dfi_id=orig_dfi_id,
            batch_number=batch_number
        )
    def __str__(self):
        str_list = [self.header_line.__str__()] + [i.__str__() for i in self.trx_entries] + [self.footer_line.__str__()]
        batch_str = '\n'.join(str_list)
        return batch_str
        
    def hash(self):
        hash_sum = 0
        
        for i in self.trx_entries:
            hash_sum += int(i.transaction_line.fields['rec_dfi'][1])
        
        hash_sum = str(hash_sum)
        
        if len(hash_sum) > 10:
            hash_sum = hash_sum[-10:]
        
        return hash_sum
    
    def sum_debits(self):
        sum = 0
        
        for i in self.trx_entries:
            sum += i.no_decimal_amount
            
        return sum
    
class NachaFile():
    def __init__(self, bank_aba, company_id, file_creation_date, file_id_modifier, orig_bank_name, co_name, batches: list[Batch]):
        self.file_header = FileHeaderLine(
            bank_aba=bank_aba,
            company_id=company_id,
            file_creation_date=file_creation_date,
            file_id_modifier=file_id_modifier,
            orig_bank_name=orig_bank_name,
            company_name=co_name
        )
        
        self.batches = batches
        self.entry_addenda_lines = 0
        self.total_hash = 0
        self.total_debits = 0
        for i in batches:
            self.entry_addenda_lines += i.num_lines
            self.total_hash += int(i.hash())
            self.total_debits += i.sum_debits()
        self.total_hash = str(self.total_hash)[-10:]  
        
        self.file_footer = FileFooterLine(
            batch_count=len(self.batches),
            block_count=math.ceil(self.line_count()/10),
            entry_addenda_count=self.entry_addenda_lines,
            entry_hash=self.total_hash,
            total_debits=self.total_debits,
            total_credits=0
        )
        
    def __str__(self):
        str_list = [self.file_header.__str__()] + [i.__str__() for i in self.batches] + [self.file_footer.__str__()]
        text = '\n'.join(str_list)
        if self.line_count() % 10 != 0:
            pad = '\n' + ('9' * 94)
            rem = self.line_count() % 10
            pad_str = pad * rem
            text += pad_str
        
        return text
        
    def line_count(self):
        file_info = 2
        batch_info = 2
        trx_lines = 0
        
        for i in self.batches:
            trx_lines += i.num_lines
        
        return file_info + batch_info + trx_lines