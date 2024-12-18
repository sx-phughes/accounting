from PayablesStructure import *
from Input import *

table = PayablesTable()

for i in range(3):
    invoice = input_invoice()
    table.add_invoice(invoice)

table.save()