from WirePayment import WirePayment
from datetime import datetime
import csv


class WireFile:
    """An object for holding information to be used in construction of a wire payment file to be written to disk."""

    def __init__(
        self, transactions: list[WirePayment] | WirePayment, company: str
    ):
        """Object initialized from either single or multiple WirePayment objects."""
        self.transactions = transactions
        self.header = ["HEADER", datetime.now().strftime("%Y%m%d%H%M%S"), 1]
        self.company = company
        self.hash_sum = 0
        if len(transactions) > 1:
            for i in transactions:
                self.hash_sum += i.amount
        else:
            self.hash_sum = transactions.amount
        self.trailer = ["TRAILER", len(transactions), self.hash_sum]

    def write_file(self, path: str, file_name: str):
        """Writes file to disk."""

        with open(path + "/" + file_name + ".csv", "x") as f:
            writer = csv.writer(f)
            writer.writerow(self.header)

            if len(self.transactions) > 1:
                for i in self.transactions:
                    writer.writerow(i.create_payment())
            else:
                writer.writerow(self.transactions.create_payment())

            writer.writerow(self.trailer)
