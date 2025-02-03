from flask import Flask, render_template, request, redirect, url_for
from PayablesStructure import PayablesTable, Invoice, Amendment
import pandas as pd

payables = PayablesTable()

vendors_path = 'C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx'
vendors = pd.read_excel(vendors_path,'Vendors')

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def home():
    curr_month = '202411'
    unique_months = []
    for i in list(payables.payables_table['invoicemonth'].values):
        if i not in unique_months:
            unique_months.append(i)

    if request.method == 'POST':
        summary_opt = request.form['month']
        return redirect(url_for('month_summary', monthyear=summary_opt))
    else:
        return render_template(
            'index.html',
            monthyear=curr_month,
            months=unique_months
            )

@app.route('/summary<monthyear>')
def month_summary(monthyear):
    month_table = payables.payables_table.loc[payables.payables_table['invoicemonth'] == int(monthyear)].copy()
    month_sum = month_table['amount'].sum()
    month_count = len(month_table)

    html_table = month_table[['vendor', 'invoiceno', 'amount', 'is_paid']].rename(
        columns={
            'vendor': 'Vendor',
            'invoiceno': 'Invoice Number',
            'amount': 'Amount',
            'is_paid': 'Is Paid?'
        }
        ).to_html(index=False)
    
    return render_template(
        'monthsummary.html',
        monthyear=monthyear,
        month_sum=month_sum,
        month_count=month_count,
        payables=html_table
        )

@app.route('/invoice<uniqueid>')
def invoice_summary(uniqueid):
    pass

@app.route('/add_invoice', methods=['GET', 'POST'])
def add_invoice():
    if request.method == ['POST']:
        new_invoice = Invoice(
            invoiceno=request.form['invoice-no'],
            vendor=request.form['vendor'],
            invoicemonth=request.form['invoice-month'],
            amount=request.form['amount']
            )
        payables.add_invoice(new_invoice)
    else:
        return render_template(
            'add_invoice.html',
            vendors=vendors['Vendor'].values
            )

@app.route('/add_amendment', methods=['GET', 'POST'])
def add_amendment():
    if request.method == ['POST']:
        amending_invoice_unique_id = request.form['vendor'] + request.form['invoice_no']
        invoice_line = payables.loc[payables['uniqueid'] == amending_invoice_unique_id]
        amending_invoice = Invoice(
            invoiceno=invoice_line['invoiceno'],
            vendor=invoice_line['vendor'],
            invoicemonth=invoice_line['invoicemonth'],
            amount=invoice_line['amount'],
        )
        new_amendment = Amendment(
            amending_invoice=amending_invoice,
            invoiceno=request.form['invoice-no'],
            new_amount=request.form['new-amount']
        )

        payables.add_invoice(new_amendment)
    else:
        return render_template(
            'add_amendment.html',
            vendors=vendors['Vendor'].values
        )

if __name__ == '__main__':
    app.run()