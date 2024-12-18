from flask import Flask, render_template, request, redirect, url_for
from PayablesStructure import PayablesTable
import pandas as pd

payables = pd.read_csv('C:/gdrive/My Drive/code_projects/payables2/payables.csv')

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def home():
    curr_month = '202411'
    unique_months = []
    for i in list(payables['invoicemonth'].values):
        if i not in unique_months:
            unique_months.append(i)

    if request.method == 'POST':
        summary_opt = request.form['month']
        return redirect(url_for('month_summary', monthyear=summary_opt))
    else:
        return render_template('index.html', monthyear=curr_month, months=unique_months)

@app.route('/summary<monthyear>')
def month_summary(monthyear):
    month_table = payables.loc[payables['invoicemonth']==int(monthyear)].copy()
    month_sum = month_table['amount'].sum()
    month_count = len(month_table)

    html_table = month_table[['vendor', 'invoiceno', 'amount', 'is_paid']].rename(columns={'vendor': 'Vendor', 'invoiceno': 'Invoice Number', 'amount': 'Amount', 'is_paid': 'Is Paid?'}).to_html(index=False)
    
    return render_template('monthsummary.html', monthyear=monthyear, month_sum=month_sum, month_count=month_count, payables=html_table)

@app.route('/invoice<uniqueid>')
def invoice_summary(uniqueid):
    pass

if __name__ == '__main__':
    app.run()