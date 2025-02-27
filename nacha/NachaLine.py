
class NachaLine():
    def __init__(self, **fields: list):
        # field_dict formatted as follows: {field_name: [field_len, field_value]}
        self.fields = fields
        self.line_string = ''
        
        for i in fields.keys():
            self.line_string += self.construct_field(fields[i][0], fields[i][1])
            
        self.line_string = self.validate_line(self.line_string)
            
    def __str__(self):
        return self.line_string
    
    def construct_field(self, field_len:int, field_value):
        if field_len > len(str(field_value)):
            field_string = str(field_value)
            filler = ' ' * (field_len - len(field_string))
            field_string += filler
        elif field_len == len(str(field_value)):
            field_string = str(field_value)
        elif field_len < len(str(field_value)):
            field_string = str(field_value)[0:field_len]
            
        # print(f'field string {field_string}, spec len {field_len}, actual len {len(field_string)}')
        
        return field_string
    
    def validate_input(self, value, val_type):
        return type(value) == val_type
    
    def validate_all_inputs(self, fields: dict):
        for i in fields.keys():
            if self.validate_input(fields[i][1], str):
                continue
            else:
                for i in fields.keys():
                    print(f'{i} : {type(fields[i])}, {str(fields[i][1])}')
                
                raise TypeError(fields[i][1])
    
    def validate_line(self, line):
        # print(line)
        # print(len(line))
        if len(line) == 94:
            return line
        else:
            raise TypeError('Field values are not of proper length')
        
class FileHeaderLine(NachaLine):
    def __init__(self, bank_aba, company_id, file_creation_date, file_id_modifier, orig_bank_name, company_name):
        super().__init__(record_type_code = [1, '1'],
                         priority_code = [2,'01'],
                         company_id = [10, company_id],
                         bank_aba = [10, ' '+ str(bank_aba)],
                         file_creation_date = [10, file_creation_date],
                         file_id_modifier = [1, file_id_modifier],
                         record_size = [3, '094'],
                         blocking_factor = [2, '10'],
                         format_code = [1,'1'],
                         immediate_destination_name = [23, orig_bank_name],
                         immedaite_origin_name = [23, company_name],
                         reference_code = [8, ' ' * 8]
                         )
        
class FileFooterLine(NachaLine):
    def __init__(self, batch_count, block_count, entry_addenda_count, entry_hash, total_debits, total_credits):
        super().__init__(record_type_code = [1, '9'],
                         batch_count = [6, batch_count],
                         block_count = [6, block_count],
                         entry_addenda_count = [8, entry_addenda_count],
                         entry_hash = [10, entry_hash],
                         debits = [12, total_debits],
                         credits = [12, total_credits],
                         reserved = [39, ' ' * 39]
                         )
        
class BatchHeaderLine(NachaLine):
    def __init__(self, service_class_code, company_name, company_id, std_entry_class, company_entry_description, effective_date, orig_dfi_id, batch_number):
        super().__init__(record_type_code = [1, '5'],
                         service_class_code = [3, service_class_code],
                         company_name = [16, company_name],
                         company_discretionary_data = [20, ' ' * 20],
                         company_id = [10, company_id],
                         std_entry_class = [3, std_entry_class],
                         co_entry_descr = [10, company_entry_description],
                         co_descr_date = [6, ' ' * 6],
                         eff_entry_date = [6, effective_date],
                         reserved = [3, ' ' * 3],
                         orig_status_code = [1, '1'],
                         orig_dfi_id = [8, orig_dfi_id],
                         batch_number = [7, batch_number]
                         )
        
class BatchFooterLine(NachaLine):
    # svc_class_code, entry_addenda_count, entry_hash, total_debits, total_credits, co_id, orig_dfi_id, batch_number
    def __init__(self, **fields):
        super().__init__(record_type_code = [1, '8'],
                         service_class_code = [3, fields['svc_class_code']],
                         entry_addenda_count = [6, fields['entry_addenda_count']],
                         entry_has = [10, fields['entry_hash']],
                         debits = [12, fields['total_debits']],
                         credits = [12, fields['total_credits']],
                         co_id = [10, fields['co_id']],
                         msg_auth_code = [19, ' ' * 19],
                         reserved = [6, ' ' * 6],
                         orig_dfi_id = [8, fields['orig_dfi_id']],
                         batch_number = [7, fields['batch_number']]
                         )
        
class TransactionLine(NachaLine):
    def __init__(self, **fields):
        # trx_code, rec_aba, dfi_acct, amount, rec_co_name, addenda_indicator, entry_seq_no
        # self.validate_all_inputs(fields)
        super().__init__(record_type_code = [1, '6'],
                         trx_code = [2, fields['trx_code']],
                         rec_dfi = [8, fields['rec_aba'][0:8]],
                         rec_check_num = [1, fields['rec_aba'][8:9]],
                         dfi_acct = [17, fields['dfi_acct']],
                         amount = [10, fields['amount']],
                         id_no = [15, fields['dfi_acct']],
                         rec_co_name = [22, fields['rec_co_name']],
                         discretionary_data = [2, ' ' * 2],
                         addenda_indicator = [1, fields['addenda_indicator']],
                         trace_no = [15, str(fields['rec_aba'])[0:8] + fields['entry_seq_no']]
                         )
        
class AddendaLine(NachaLine):
    def __init__(self, payment_info, entry_seq_no, vendor):
        super().__init__(record_type_code = [1, '7'],
                         addenda_type = [2, '05'],
                         payment_info = [80, self.check_company(vendor, payment_info)],
                         addenda_seq_no = [4, '0001'],
                         entry_detail_seq_no = [7, entry_seq_no])
        
    def check_company(self, vendor, payment_info):
        if vendor == 'Citigroup Global Mkts.':
            payment_info = 'billing id: SPLX -- invoice id: ' + payment_info
            return payment_info
        else:
            return payment_info