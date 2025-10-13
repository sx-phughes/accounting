from WirePayment import WirePayment, Vendor
from WireFile import WireFile
from datetime import datetime
import os

if os.path.exists('C:/Users/phughes_simplextradi/Downloads/Test File.csv'):
    os.remove('C:/Users/phughes_simplextradi/Downloads/Test File.csv')

anova = Vendor('Anova')

pmt = WirePayment(
    orig_bank_id='071000013',
    orig_account='000000559711101',
    amount=500.00, 
    value_date=datetime(2025,9,16), 
    vendor=anova, 
    details='Test Payment', 
    template=True
)

file = WireFile(pmt)

file.write_file('C:/Users/phughes_simplextradi/Downloads', 'Test File')