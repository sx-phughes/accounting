import os
import sys
import pandas as pd
import re
import pypdf

try:
    from MonthEnd.Abn.Base import get_archive_date_path, get_t_minus
    from MonthEnd.Abn.EoyExtractPageText import *
    from MonthEnd.Abn import FileGrabber
except ModuleNotFoundError:
    from Base import get_archive_date_path
    from EoyExtractPageText import *
    import FileGrabber


def convert_to_eoy_cash(year: int) -> pd.DataFrame:
    """Converts the last CSV Cash File of the year to a usable format for the
    new year.

    PROCESS NOTES
    MARK TO MARKET OPTIONS LONG/SHORT ARE NETTED TO MARK TO MARKET OPTIONS

    MARK TO MARKET UNSETTLED LONG/SHORT STOCK ARE NETTED TO MARK TO MARKET
    UNSETTLED STOCK

    MARK TO MARKET UNSETTLED LONG/SHORT PREFSTOCK ARE NETTED TO MARK TO
    MARKET UNSETTLED PREFSTOCK
      ADD PRIOR VALUES FOR THESE TO THE RESULTING FILE AND ZERO OUT THE
      NETTED CATEGORIES

    GROSS PROFIT OR LOSS IS A FUTURES ONLY CATEGORY AND IS NETTED INTO BALANCE PREVIOUS YEAR
      THIS CAN STAY UNTOUCHED

    OPEN TRADE EQUITY IS LISTED AS OPEN TRADE EQUITY FUTURES BUT STAYS THE
    SAME
      THIS NEEDS TO BE RENAMED FOR VALUES TO COME THROUGH
    """
    t_minus = get_t_minus()
    dir = get_archive_date_path(year, 12, day=t_minus.day)
    downloads = os.getenv("HOMEPATH") + "/Downloads"

    f_pattern = r"[\w_\d]*DPR_SU_EOY.pdf"

    proper_files = get_ABN_pdfs(f_pattern, year, 12, t_minus.day)

    os.chdir(dir)

    master = pd.DataFrame()
    count = 0

    for f in proper_files:
        count += 1
        pdf = pypdf.PdfReader(f)
        pages = pdf.pages
        page_nums = get_page_nos(pages)

        for num in page_nums:
            page_obj = pages[num]
            df = get_data_table(f, page_obj)
            if count == 1:
                master = df.copy(deep=True)
            else:
                master = pd.concat([master, df])

    master.reset_index(drop=True, inplace=True)

    initial_line_drops = [
        "CASH POSITION",
        "NET LIQUIDATION",
        "NET PROFIT & LOSS",
    ]

    drop_index = master.loc[
        master["Cash Title"].isin(initial_line_drops)
    ].index
    no_bad_lines = master.drop(index=drop_index).reset_index(drop=True)
    no_bad_lines.loc[
        no_bad_lines["Cash Title"].str.contains("MARGIN"), "New"
    ] = 0
    total_sum = no_bad_lines["New"].sum()

    no_bad_lines.to_csv(downloads + "/summary_df.csv")

    ## + Formatting rules to make = to normal cash file ##
    csv_cash = FileGrabber.get_cash_file(year, 12)
    csv_cash.loc[
        csv_cash["Cash Title"].str.contains("MARGIN"), "Opening Balance"
    ] = 0
    csv_cash_total = csv_cash["Opening Balance"].sum()

    ## Check 1 ##
    if round(total_sum, 0) != round(csv_cash_total, 0):
        raise ValueError(
            "Total Sum and CSVCASH Sum are not equal",
            f"Total Sum: {total_sum:,.2f}",
            f"CSVCASH Sum: {csv_cash_total:,.2f}",
        )
    else:
        print(
            "Check 1 passed\n",
            f"Total Sum: {total_sum:,.2f}",
            f"CSVCASH Sum: {csv_cash_total:,.2f}",
        )

    line_items_to_keep = [
        "MARK TO MARKET OPTIONS LONG",
        "MARK TO MARKET OPTIONS SHORT",
        "MARK TO MARKET UNSETTLED LONG STOCK",
        "MARK TO MARKET UNSETTLED SHORT STOCK",
        "MARK TO MARKET UNSETTLED LONG PREFSTOCK",
        "MARK TO MARKET UNSETTLED SHORT PREFSTOCK",
        "MARK TO MARKET UNSETTLED LONG WARRANT",
        "MARK TO MARKET UNSETTLED SHORT WARRANT",
    ]

    orig_mark_to_market = csv_cash.loc[
        csv_cash["Cash Title"].isin(line_items_to_keep)
    ].copy()
    basic_mark_to_market = orig_mark_to_market[
        ["Account Name", "Cash Title", "Opening Balance"]
    ].copy(deep=True)
    mark_to_market = basic_mark_to_market.rename(
        columns={"Opening Balance": "New"}
    ).copy(deep=True)
    mark_to_market["Change"] = 0
    mark_to_market["Old"] = mark_to_market["New"]
    mark_to_market["Month to Date"] = 0
    mark_to_market["f_name"] = "CSVCASH"

    line_items_to_drop = [
        "MARK TO MARKET OPTIONS",
        "MARK TO MARKET UNSETTLED STOCK",
        "MARK TO MARKET UNSETTLED PREFSTOCK",
        "MARK TO MARKET UNSETTLED WARRANT",
    ]

    rows_to_drop = no_bad_lines.loc[
        no_bad_lines["Cash Title"].isin(line_items_to_drop)
    ].index
    summary_without_net_mtm = no_bad_lines.drop(index=rows_to_drop).copy()
    summary_with_split_mtm = pd.concat(
        [summary_without_net_mtm, mark_to_market]
    )

    new_summary = summary_with_split_mtm.copy()
    new_summary["Cash Title"] = summary_with_split_mtm["Cash Title"].mask(
        summary_with_split_mtm["Cash Title"] == "OPEN TRADE EQUITY FUTURE",
        "OPEN TRADE EQUITY",
    )

    summary_renamed = new_summary.rename(
        columns={"New": "Opening Balance", "Account": "Account Name"}
    )
    new_summary_final = summary_renamed.drop(columns="f_name")
    new_summary_final.to_csv(downloads + "/final_df.csv")
    final_checksum = new_summary_final["Opening Balance"].sum()

    ## Check 2 ##
    if round(csv_cash_total, 0) != round(final_checksum, 0):
        raise ValueError(
            "Final Check Sum and CSVCASH Sum are not equal",
            f"Final Check Sum: {final_checksum:,.2f}",
            f"CSVCASH Sum: {csv_cash_total:,.2f}",
        )
    else:
        print(
            "Check 2 passed\n",
            f"Final Checksum: {final_checksum:,.2f}",
            f"CSVCASH Sum: {csv_cash_total:,.2f}",
        )

    return new_summary_final


def get_ABN_pdfs(f_pattern: str, year: int, month: int, day: int):
    dir_path = get_archive_date_path(year, month, day)

    files = os.listdir(dir_path)

    proper_files = list(filter(lambda x: re.search(f_pattern, x), files))

    return proper_files


if __name__ == "__main__":
    year = int(sys.argv[1])
    eoy_cash = convert_to_eoy_cash(year)
    eoy_cash.to_csv(
        os.getenv("HOMEPATH") + "/Downloads/eoy_cash_final.csv", index=False
    )
