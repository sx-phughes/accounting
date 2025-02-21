from PayablesStructure import *
import os

def input_invoice():
    os.system('cls')
    print('Invoice Input\n')

    fields = {
        'Invoice Number': '',
        'Vendor Name': '',
        'Invoice Month': '',
        'Invoice Amount': '',
        'File Path (comma separated)': ''
    }

    for i in fields.keys():
        print(i)
        val = input('>\t')
        fields[i] = val

    invoice = Invoice(fields['Invoice Number'], fields['Vendor Name'], fields['Invoice Month'], fields['Invoice Amount'], fields['File Path (comma separated)'].split(','))

    return invoice