from bofadata import BOFAData
from journalentry import *

class BOFAEntries(object):
    def __init__(self, bofa_data:BOFAData):
        self.data = bofa_data
        self.date = bofa_data.end
        self.bs_entry = JournalEntry(self.date, 'BOFA BS Entry')
        self.equities_mm_entry = JournalEntry(self.date, 'Equities MM Entry')
        self.equities_prop_entry = JournalEntry(self.date, 'Equities Prop Entry')
        
    def balance_sheet_entry(self):
        je = {'Line Item': [],
              'COMB Account': [],
              'GL Account': [],
              'Amount': []}
        
        self.bs_entry.add_line(12503, 'd', self.data.comb_data[self.data.comb_data['Account'] == '644', 'Long Stock MV'].sum().value, 'Long Stock')
        self.bs_entry.add_line(12502, 'd', self.data.comb_data[self.data.comb_data['Account'] == '644', 'Long Option MV'].sum().value, 'Long Option')
        self.bs_entry.add_line(20503, 'd', self.data.comb_data[self.data.comb_data['Account'] == '644', 'Short Stock MV'].sum().value, 'Short Stock')
        self.bs_entry.add_line(20502, 'd', self.data.comb_data[self.data.comb_data['Account'] == '644', 'Short Option MV'].sum().value, 'Short Option')
        self.bs_entry.add_line(20506, 'd', self.data.comb_data[self.data.comb_data['Account'] == '644', 'Short Bond MV'].sum().value, 'Short Debt')
        
        # this subtracts out the pending dividend credit that BAML doesn't remove -- we count it elsewhere so we have to remove it
        self.bs_entry.add_line(40503, 'c', self.data.comb_data[self.data.comb_data['Account'] == '64440', 'Pend Div Debit'].sum().value + self.data.comb_data[self.data.comb_data['Account'] == '64440', 'Pend Div Credit'].sum().value, 'Stock PnL')
        self.bs_entry.add_line(40502, 'c', self.data.comb_data[self.data.comb_data['Account'] == '64498', 'Pend Div Debit'].sum().value + self.data.comb_data[self.data.comb_data['Account'] == '64498', 'Pend Div Credit'].sum().value, 'Stock PnL')
        
        cash = ['', '', 12501, -1 * (long_stock[3] + long_option[3] + short_stock[3] + short_option[3] + short_debt[3] + stock_pnl_1[3] + stock_pnl_2[3])]
        
        # Accrued Interest Items
        #   Short Stock Interest Lines
        ss_accts = [[64498, 50502], [64440, 50503], [64413, 50501], [64441, 50503]]
        ss_lines = []
        for i in ss_accts:
            line_data = ['Short Stock Interest', i[0], i[1], self.data.comb_data[self.data.comb_data['Account'] == str(i[0]), 'MTD SSR Total'].sum().value]
            ss_lines.append(line_data)
            
        #   Assessed Bal Interest Lines
        ab_accts = [[64499, 50504], [64498, 50500], [64440, 50501], [64413, 50501], [64441, 50501]]
        ab_lines = []
        for i in ab_accts:
            line_data = ['Assessed Balance Interest', i[0], i[1], self.data.comb_data[self.data.comb_data['Account'] == str(i[0]), 'MTD Interest'].sum().value]
            
        # Pending Div Credit/Debit Allocation to Payable/Receivable
        div_receivable = ['Dividend Receivable', 644, 12504, -1 * self.data.comb_data[self.data.comb_data['Account'] == 644, 'Pend Div Debit'].sum().value]
        div_payable = ['Dividend Payable', 644, 20504, -1 * self.data.comb_data[self.data.comb_data['Account'] == 644, 'Pend Div Credit'].sum().value]
        
        # Pending Div Credit/Debit Removal from Div Accts
        comb_accts = [64440, 64498]
        gl_accts = [[41500, 51500], [41501, 51501]]
        line_items = ['Dividend Income', 'Dividend Expense']
        col_names = ['Pend Div Credit', 'Pend Div Debit']
        for i in range(len(comb_accts)):
            for j in range(len(col_names)):
                line_data = [line_items[j], comb_accts[i], gl_accts[i][j], self.data.comb_data.loc[self.data.comb_data['Account'] == comb_accts[i], col_names[j]]]
        
        
    def equity_mm_entry(self):
        pass
    
    def equity_prop_entry(self):
        pass