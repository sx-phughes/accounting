import pandas as pd
from datetime import datetime
import os

from wires.WirePayment import company_ids, company_names, WirePayment, Vendor
from wires.WireFile import WireFile


def write_files_to_disk(
    wire_files: list[WireFile], path: str = None, value_date: str = None
) -> None:
    """Given a list of wire files, one for each company, write the files to
    disk at the given path. Default write location is downloads."""

    dest = "/".join([os.environ["HOMEPATH"], "Downloads"])
    if path:
        dest = path
    vd = datetime.now().strftime("%Y-%m-%d")
    if value_date:
        vd = value_date
    for file in wire_files:
        f_name = f"{file.company} Wires {vd}"
        file.write_file(dest, f_name)


def create_wire_files(wires: dict[str, list[WirePayment]]) -> list[WireFile]:
    """Given a dictionary of wire payments keyed to their respective companies,
    create wire file objects for each company and write to disk.
    """

    wire_files = []
    for co in wires.keys():
        if len(wires[co]) > 0:
            file = WireFile(wires[co], co)
            wire_files.append(file)
        else:
            continue
    return wire_files


def process_payables_df_to_wires(
    wire_invoices: pd.DataFrame,
    value_date: datetime,
) -> dict[str, WirePayment]:
    """Creates a dict of WirePayment objects keyed to each company for each
    invoice to be paid via wire.
    """

    global wire_value_date
    wire_value_date = value_date
    co_wires_dict = {company: [] for company in company_names.keys()}

    companies = wire_invoices["company"].unique()
    # print("Companies: ", companies)
    for company in companies:
        company_wires = wire_invoices.loc[
            wire_invoices["company"] == company
        ].copy()

        create_payment_objects(company_wires, co_wires_dict[company])
        # print("Num ", company, " wires: ", len(co_wires_dict[company]))

    return co_wires_dict


def create_payment_objects(
    invoices: pd.DataFrame, co_list: list
) -> list[WirePayment]:
    """Creates a list of payment objects from a data frame of invoices. All
    invoices in the dataframe must be invoices intended to be paid via wire,
    and one company."""

    company = invoices["company"].values[0]
    global wire_value_date

    for i, row in invoices.iterrows():
        payment = WirePayment(
            orig_bank_id="071000013",
            orig_account=company_ids[company],
            amount=row["amount"],
            value_date=wire_value_date,
            vendor=row["vendor"],
            template_name=row["template"],
            details=row["inv_num"],
            template=True,
        )
        co_list.append(payment)


def os_interface_wire_wrapper(
    payables: pd.DataFrame, valuedate: datetime
) -> None:
    """Wrapper for creating wire payments from inside of the AP module."""

    wire_payment_dict = process_payables_df_to_wires(
        wire_invoices=payables, value_date=valuedate
    )
    wire_files = create_wire_files(wires=wire_payment_dict)
    write_files_to_disk(wire_files=wire_files)
