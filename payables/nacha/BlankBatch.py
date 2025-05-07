from Payables.nacha.NachaConstructor import *
from Payables.nacha.NachaFile import *
from datetime import datetime

relevant_cols = ('name on account', 'beneficiary bank', 'aba', 'account number', 'amount')

def make_trx(account_name, amount, note, aba, account_no, seq_no):
    trx = TransactionEntry(
        vendor=account_name,
        amount=amount,
        invoice_number=note,
        vendor_aba=aba,
        vendor_account=account_no,
        sequence_no='0' * (7 - len(str(seq_no))) + str(seq_no),
        debug=False
    )
    
    return trx

def make_batch(transactions: list[TransactionEntry], company_name, batch_no, value_date, entry_descr=''):
    batch = Batch(
        company_name=NachaConstructor.company_names[company_name],
        company_id=NachaConstructor.company_ids[company_name],
        co_entry_descr=entry_descr,
        effective_date=value_date,
        orig_dfi_id=NachaConstructor.company_abas[company_name],
        batch_number=batch_no,
        trx_entries=transactions
    )
    
    return [batch]

def make_file(batches: list[Batch], company_name, file_id_modifier):
    file = NachaFile(
        bank_aba=NachaConstructor.company_abas[company_name],
        company_id=NachaConstructor.company_ids[company_name],
        file_creation_date=datetime.now().strftime('%y%m%d%H%M'),
        file_id_modifier=file_id_modifier,
        orig_bank_name='JPMORGAN CHASE BANK, N.A.',
        co_name=NachaConstructor.company_names[company_name],
        batches=batches
    )

    return file

def id_cols(old_cols: list[str]) -> dict:
    print('Please identify key column names in table:\n')
    for col_name in old_cols:
        print(f'\t{col_name}')
    
    print('\n')
    
    column_mapping = {}
    
    for new_col in relevant_cols:
        print(f'Enter name of column containing data for: {new_col}')
        old_col_name = input('\t>')
        column_mapping.update({old_col_name: new_col})
    
    return column_mapping

def read_table(path: str):
    pmt_info = pd.read_csv(path, dtype=str)
    
    renamer = id_cols(pmt_info.columns.to_list())
    
    named_pmt_info = pmt_info.rename(columns=renamer)
    
    return named_pmt_info
    
    
def process_transactions(df: pd.DataFrame, note: str) -> NachaFile:
    transactions = []
    for i, row in df.iterrows():
        transactions.append(
            make_trx(
                account_name=row['name on account'],
                amount=row['amount'],
                note=note,
                aba=row['aba'],
                account_no=row['account number'],
                seq_no=(101 + i)
            )
        )
    
    return transactions

def process_file(src_path: str, save_path: str, company_name: str, value_date_y2m2d2: str, trx_note: str='', batch_descr: str=''):
    pmt_info = read_table(src_path)
    
    transactions = process_transactions(pmt_info, trx_note)
    batches = make_batch(transactions, company_name, '0000001', value_date=value_date_y2m2d2, entry_descr=batch_descr)
    file_obj = make_file(batches, company_name, 'A')
    
    with open(file=save_path, mode='w') as nacha_file:
        nacha_file.write(str(file_obj))
        
def nacha_company_selector() -> str:
    print('Select Company to Issue ACHs from:')
    company_names = list(NachaConstructor.company_names.keys())
    for i in range(len(company_names)):
        print(f'{str(i)}:\t{company_names[i]}')
    print('\n')
    
    selected = int(input('>\t'))
    
    return company_names[selected]