import pandas as pd


class JournalLine(object):
    def __init__(self, gl_account, pos_is_dc, amount, memo):
        self.gl_account = gl_account
        self.pos_is_dc = pos_is_dc
        self.amount = amount
        self.memo = memo

class JournalEntry(object):
    def __init__(self, date, entry_name):
        self.date = date
        self.num_lines = 0
        self.lines = {}
        self.descr = entry_name
    
    def add_line(self, gl_account, pos_is_dc, amount, memo, journal_line=''):
        if journal_line:
            self.lines.update({self.num_lines: journal_line})
        else:
            self.lines.update({self.num_lines: JournalLine(gl_account, pos_is_dc, amount, memo)})
        self.num_lines += 0
        
    def rem_line(self, line_num):
        self.lines.pop(line_num)
        for i in range(len(self.lines.keys)):
            if i == list(self.lines.keys)[i]:
                continue
            elif i != list(self.lines.keys)[i]:
                old_key = self.lines.keys[i]
                val = self.lines[old_key]
                self.lines.pop(old_key)
                self.lines[i] = val
    
    def update_line(self, line_num, new_line):
        self.lines[line_num] = new_line
    
    def totals(self, dc):
        pass
    
    def print_entry(self, path):
        data = {'gl_account': [],
                'debit': [],
                'credit': [],
                'memo': []}
        
        for i, j in self.lines.items():
            data['gl_account'].append(j.gl_account)
            
            if j.pos_is_dc == 'd':
                if j.amount >= 0:
                    data['debit'].append(round(abs(j.amount),2))
                    data['credit'].append(0)
                else:
                    data['credit'].append(round(abs(j.amount),2))
                    data['debit'].append(0)
            else:
                if j.amount >= 0:
                    data['debit'].append(0)
                    data['credit'].append(round(abs(j.amount),2))
                else:
                    data['debit'].append(round(abs(j.amount),2))
                    data['credit'].append(0)
                
            data['memo'].append(j.memo)
        
        df = pd.DataFrame(data)
        
        with pd.ExcelWriter(path) as writer:
            df.to_excel(writer, self.descr, index=False)