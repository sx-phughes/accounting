import numpy as np
import pandas as pd

from payables.Interface.payables_wb import PayablesWorkbook, get_col_index


def process_inputs(invoice_inputs: list[str]) -> list[str | bool | np.float64]:
    convert_cc_to_bool(invoice_inputs)


def get_vendors() -> pd.DataFrame:
    vendors = pd.read_excel(
        "C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx",
        "Vendors",
    )


def convert_cc_to_bool(invoice_inputs: list[str]) -> list[str | bool]:
    i = get_col_index("CC")
    response = False
    if invoice_inputs[i] == "y":
        response = True
    invoice_inputs[i] = response
