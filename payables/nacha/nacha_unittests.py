import pandas as pd

from NachaConstructor import NachaConstructor

def get_test_data() -> pd.DataFrame:
    path = '/'.join([
        'C:/gdrive/Shared drives/accounting/Payables',
        '2025/202508/2025-08-31/2025-08-31 Payables.xlsm'
    ])
    invoices = pd.read_excel(io=path, sheet_name="Invoices")
    return invoices

global data, constructor
data = get_test_data()
constructor = NachaConstructor(
    trx_table=data,
    value_date="20250930",
    debug=False
)

def get_short_string() -> str:
    bgc = data.loc[data["Vendor"] == "BGC"].copy(deep=True)
    bgc_invoices = bgc["Invoice #"]
    inv_str = constructor.get_invoice_str(bgc_invoices)
    return inv_str
    
def test_short_string() -> None:
    assert get_short_string() == "BGC-Jul-2025-00001697 BGC-Jul-2025-00001818"