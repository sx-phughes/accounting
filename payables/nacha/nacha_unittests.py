import pandas as pd
import numpy as np

from NachaConstructor import NachaConstructor

def get_test_data() -> pd.DataFrame:
    path = '/'.join([
        'C:/gdrive/Shared drives/accounting/Payables',
        '2025/202508/2025-08-31/2025-08-31 Payables.xlsm'
    ])
    invoices = pd.read_excel(io=path, sheet_name="Invoices")
    return invoices

global data, achs, constructor, grouped_trx
data = get_test_data()
achs = data.loc[data["Payment Type"] == "ACH"].copy(deep=True)
constructor = NachaConstructor(
    trx_table=achs,
    value_date="20250930",
    debug=False
)
grouped_trx = constructor.group_trx_by_company(achs)

def get_vendor_invoices(vendor: str) -> pd.Series:
    vendor_data = data.loc[data["Vendor Name"] == vendor].copy(deep=True)
    vendor_invs = vendor_data["Invoice #"]
    return vendor_invs

def get_short_string() -> str:
    bgc_invoices = get_vendor_invoices("BGC")
    inv_str = constructor.get_invoice_str(bgc_invoices)
    return inv_str

def get_long_string() -> str:
    icap_invs = get_vendor_invoices("ICAP")
    inv_str = constructor.get_invoice_str(icap_invs)
    return inv_str

def get_company_total(vendor: str) -> float:
    val = grouped_trx.loc[
        grouped_trx["ACH Vendor Name"] == vendor, "Amount"
    ].sum()
    return round(val,2)

##############################
#### Unit Test Functions #####
##############################
def test_short_string() -> None:
    assert get_short_string() == "BGC-Jul-2025-00001697 BGC-Jul-2025-00001818"

def test_long_string() -> None:
    assert get_long_string() == "36293U/CTF/0725 36293U/ESO/0725 46063U/ESO/0725 46063U/CTF/0725 46063U/ESO/0625"

def test_vendor_sums() -> None:
    assert get_company_total("ICAP") == np.float64(37857.15)
    assert get_company_total("CODA Markets, Inc.") == np.float64(1401.16)
    assert get_company_total("Fitness Formula") == np.float64(1624)