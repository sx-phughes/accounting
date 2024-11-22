from WirePayment import WirePayment
from datetime import datetime
import csv

class WireFile:
    def __init__(self, transactions: list[WirePayment]|WirePayment):
        self.transactions = transactions
        self.header = ['HEADER', datetime.now().strftime('%Y%m%d%H%M%S'), 1]
        self.hash_sum = 0
        if len(transactions) > 1:
            for i in transactions:
                self.hash_sum += i.amount
        else:
            self.hash_sum = transactions.amount
        self.trailer = ['TRAILER', len(transactions), self.hash_sum]
        
    def write_file(self, path:str, file_name: str):
        with open(path + '/' + file_name + '.csv', 'x') as f:
            writer = csv.writer(f)
            writer.writerow(self.header)
            
            if len(self.transactions) > 1:
                for i in self.transactions:
                    writer.writerow(i.create_payment())
            else:
                writer.writerow(self.transactions.create_payment())
                
            writer.writerow(self.trailer)