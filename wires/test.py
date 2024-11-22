from WirePayment import WirePayment, Vendor
from WireFile import WireFile
from datetime import datetime
import os

if os.path.exists('C:/Users/phughes_simplextradi/Downloads/Test File.csv'):
    os.remove('C:/Users/phughes_simpletradi/Downloads/Test File.csv')

anova = Vendor('Anova')

pmt = WirePayment('021000021', '000000559711101', 500.00, datetime(2024,11,16), anova, 'Test Payment')

file = WireFile(pmt)

file.write_file('C:/Users/phughes_simplextradi/Downloads', 'Test File')