import pandas as pd
import numpy as np
from DupePayments import payables_root, get_n_months_payble_paths

def get_data_about_unique_vendors(
    cols: list[str], months: int, end_of_month: str):
    data = get_vendors_from_n_months(months, end_of_month)
    extracted_cols_data = data[cols]
    return extracted_cols_data

def get_vendors_from_n_months(months: int, end_of_month: str):
    path_stems = get_n_months_payble_paths(end_of_month, months)
    unique_vendors = get_vendor_data(path_stems)
    unique_dataframe = make_list_a_dataframe(unique_vendors, "Unique")

    vendor_table = get_vendors_database()

    merged = unique_dataframe.merge(
        right=vendor_table,
        left_on="Unique",
        right_on="Vendor",
        how="left"
    )

    return merged

def make_list_a_dataframe(vals: list, col_name: str) -> pd.DataFrame:
    dict_of_vals = {col_name: vals}
    df_of_vals = pd.DataFrame(dict_of_vals)
    return df_of_vals


def get_vendor_data(stems: list[str]):
    vendors = []
    for stem in stems:
        data = pd_excel_handler('/'.join([payables_root, stem]), "Invoices")
        if data is None:
            continue
        vendors += data['Vendor'].unique().tolist()
    unique_vendors = get_list_unique_vals(vendors)

    return unique_vendors
    
def pd_excel_handler(path: str, sheet_name: str) -> pd.DataFrame:
    try:
        data = pd.read_excel(io=path, sheet_name=sheet_name)
    except FileNotFoundError:
        try:
            xlsx_path = path.replace('xlsm', 'xlsx')
            data = pd.read_excel(io=xlsx_path, sheet_name=sheet_name)
        except FileNotFoundError:
            return None

    return data

def get_list_unique_vals(vendors: list[str]):
    unique_vals = []
    for vendor in vendors:
        if vendor in unique_vals or vendor == "" or vendor is None:
            continue
        unique_vals.append(vendor)
    return unique_vals

def get_vendors_database() -> pd.DataFrame:
    vendors_path = \
        'C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx'
    return pd.read_excel(io=vendors_path, sheet_name='Vendors')

def save_df_to_path(data: pd.DataFrame, path: str) -> None:
    data.to_excel(excel_writer=path, sheet_name="Unique Vendors")


if __name__ == "__main__":
    requested = get_data_about_unique_vendors(
        ["Vendor", "Approver"], 
        12, 
        "2025-08-31"
    )
    save_path = "C:/Users/Patrick/Downloads/Unique_vendors.xlsx"
    save_df_to_path(requested, save_path)


