import os
import pandas as pd
import xlsxwriter
import numpy as np
from datetime import datetime

from Interface.payables_wb import PayablesWorkbook


def create_summary_path(date: datetime) -> str:
    """Returns the save path for the payables summary book."""

    pieces = [
        "C:/gdrive/Shared drives/accounting/Payables",
        str(date.year),
        date.strftime("%Y%m"),
        date.strftime("%Y-%m-%d"),
        f"{date.strftime("%Y-%m-%d")} Payables Summary.xlsx",
    ]

    return "/".join(pieces)


def make_summary_workbook(
    payables: PayablesWorkbook, path: str = None
) -> None:
    """Write invoice summary workbook to disk"""

    write_to = os.environ["HOMEPATH"] + "/Downloads/payables_summary.xlsx"
    if path:
        write_to = path

    with pd.ExcelWriter(
        write_to,
        "xlsxwriter",
        date_format="%Y-%m-%d",
    ) as writer:
        workbook: xlsxwriter.workbook.Workbook = writer.book

        # Cell formats
        global money, comma, bold_with_border, decimal, normal
        money = workbook.add_format({"num_format": "$#,##0.00"})
        comma = workbook.add_format({"num_format": "#,##0.00"})
        bold_with_border = workbook.add_format({"bold": True})
        bold_with_border.set_border(1)
        decimal = workbook.add_format({"num_format": "#,##0.00"})
        normal = workbook.add_format({"bold": False})

        write_summary_sheet(
            payables=payables, writer=writer, workbook=workbook
        )
        # write_wire_setup_sheet(
        #     payables=payables, writer=writer, workbook=workbook
        # )
        write_invoice_sheet(
            payables=payables, writer=writer, workbook=workbook
        )


def write_summary_sheet(
    payables: PayablesWorkbook,
    writer: pd.ExcelWriter,
    workbook: xlsxwriter.Workbook,
) -> None:
    """Write the summary sheet to file."""

    summary_tables = get_summary_tables(payables=payables)
    summary_sheet = create_summarypage(workbook, payables.payables_date)
    write_col = 0
    for table in summary_tables:
        table.to_excel(
            excel_writer=writer,
            sheet_name="Main Summary",
            startcol=write_col,
            startrow=2,
        )
        # Set table first column width to 30
        summary_sheet.set_column(
            first_col=write_col, last_col=write_col, width=30
        )
        # Set table second col width 20, num format with $
        summary_sheet.set_column(
            first_col=write_col + 1,
            last_col=write_col + len(table.columns),
            width=20,
            cell_format=comma,
        )

        write_col += 3


def format_table(
    table: pd.DataFrame,
    writer: pd.ExcelWriter,
    sheet: xlsxwriter.workbook.Worksheet,
) -> None:
    """Formats a table for the summary sheet."""

    pass


def write_invoice_sheet(
    payables: PayablesWorkbook,
    writer: pd.ExcelWriter,
    workbook: xlsxwriter.Workbook,
) -> None:
    """Writes invoice detail sheet with invoice-level information for review.

    Args:
        payables (PayablesWorkbook): PayablesWorkbook object containing
        payables information
        writer (pd.ExcelWriter): pandas ExcelWriter object
        workbook (xlsxwriter.Workbook): Workbook object being written to
    """
    invoice_sheet = workbook.add_worksheet(name="Invoices")
    invoices = get_invoice_table(payables=payables)
    invoices.to_excel(excel_writer=writer, sheet_name="Invoices", index=False)
    invoice_sheet.autofit()

    invoice_sheet.set_row(row=0, cell_format=bold_with_border)
    num_cols = len(invoices.columns)
    invoice_sheet.set_column(
        first_col=num_cols, last_col=num_cols, cell_format=comma
    )


def write_wire_setup_sheet(
    payables: PayablesWorkbook,
    writer: pd.ExcelWriter,
    workbook: xlsxwriter.Workbook,
) -> None:
    """Writes sheet with information displayed to facilitate wire entry in
    JPM"""

    wire_sheet = workbook.add_worksheet("Wire Setup")
    wires = get_wire_table(payables=payables)
    wires.to_excel(excel_writer=writer, sheet_name="Wire Setup")
    wire_sheet.set_column(first_col=0, last_col=0, width=30)
    wire_sheet.set_column(
        first_col=1, last_col=1, width=20, cell_format=decimal
    )


def get_invoice_table(payables: PayablesWorkbook) -> pd.DataFrame:
    data = payables.merge_vendors()
    cols = [
        "Vendor",
        "Invoice #",
        "Company",
        "Expense Category",
        "Approver",
        "Payment Type",
        "Amount",
    ]
    selected_cols = data[cols].copy(deep=True)
    return selected_cols


def create_summarypage(
    workbook: xlsxwriter.workbook.Workbook, date: str
) -> xlsxwriter.workbook.Worksheet:
    summary_sheet = workbook.add_worksheet("Main Summary")
    summary_sheet.write(0, 0, f"Payables Summary: {date}")
    return summary_sheet


def get_summary_tables(payables: PayablesWorkbook) -> tuple[pd.DataFrame]:
    """Get summary tables for the main summary page of the workbook."""

    merged_vendors = payables.merge_vendors()
    by_vendor = merged_vendors.pivot_table(
        values="Amount",
        index="QB Mapping",
        aggfunc="sum",
    ).sort_values("Amount", ascending=False)
    by_approver = merged_vendors.pivot_table(
        values="Amount", index="Approver", aggfunc="sum"
    )
    by_expense_cat = merged_vendors.pivot_table(
        values="Amount", index="Expense Category", aggfunc="sum"
    )
    by_company = merged_vendors.pivot_table(
        values="Amount", index="Company", columns="Payment Type", aggfunc="sum"
    )
    by_company["Total"] = by_company[by_company.columns].sum(axis=1)
    summary_tables = (by_vendor, by_approver, by_expense_cat, by_company)

    for table in summary_tables:
        try:
            table.loc["Total", "Amount"] = table["Amount"].sum()
        except KeyError:
            continue

    return summary_tables


def get_wire_table(payables: PayablesWorkbook) -> pd.DataFrame:
    with_deets = payables.merge_vendors()
    wire_mask = with_deets["Payment Type"] == "Wire"
    wires = with_deets.loc[wire_mask].copy(deep=True)
    by_vendor_wires = wires.pivot_table(
        values="Amount", index="Vendor", aggfunc="sum"
    )

    invoices_by_vendor_wires = get_wire_invoices_by_vendor(wires)
    by_vendor_wires_merged = by_vendor_wires.merge(
        right=invoices_by_vendor_wires, how="left", on="Vendor"
    )
    return by_vendor_wires_merged


def get_wire_invoices_by_vendor(wires: pd.DataFrame) -> pd.DataFrame:
    unique_vendors = wires["Vendor"].unique()
    unique_vendors.sort()
    wire_invoices_by_vendor = pd.DataFrame(
        index=unique_vendors, columns=["Invoices"]
    )
    wire_invoices_by_vendor = wire_invoices_by_vendor.rename_axis("Vendor")
    # print(wire_invoices_by_vendor)
    for vendor in unique_vendors:
        vendor_invoices = wires.loc[wires.index == vendor, "Invoice #"]
        str_vendor_invoices = ", ".join(vendor_invoices)
        mask = wire_invoices_by_vendor.index == vendor
        wire_invoices_by_vendor.loc[mask, "Invoices"] = str_vendor_invoices
    return wire_invoices_by_vendor


if __name__ == "__main__":
    ap = PayablesWorkbook("2025-09-30")
    make_summary_workbook(payables=ap)
