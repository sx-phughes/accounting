from datetime import datetime
import pandas as pd


comb_headers = [
    "Record Type",
    "Account",
    "Symbol",
    "Daily Interest by Symbol",
    "PL Change",
    "GL Change",
    "Todays Equity",
    "TD Balance",
    "Long Stock MV",
    "Short Stock MV",
    "Long Option MV",
    "Short Option MV",
    "Long Bond MV",
    "Short Bond MV",
    "Pend Div Debit",
    "Pend Div Credit",
    "Pend Div Debit Ex-Date",
    "Pend Div Credit Ex-date",
    "Net TF Fees",
    "Net Commission",
    "Daily Interest",
    "MTD Interest",
    "Daily SSR Total",
    "MTD SSR Total",
    "CM Total Equity",
    "CM Commission",
    "CM Clmg & Exch Fees",
    "CM NFA Fee",
    "CM Gross PL",
    "CM Ending Balance",
    "E1Y Commission",
    "E1Y Commissions - Stock",
    "E1Y Commissions - Options",
    "E1Y Commissions - Bonds",
    "E1Y Execution Fees",
    "E1Y Exec. Fees - Stocks",
    "E1Y Exec. Fees - Options",
    "E1Y Exec. Fees - Bonds",
    "E1Y SEC Fees",
    "E1Y SEC Fees Stocks",
    "E1Y SEC Fees Options",
    "E1Y SEC Fees Bonds",
    "E1Y Exch. Fees ",
    "E1Y Exch. Fees Stock",
    "E1Y Exch. Fees Options",
    "E1Y Exch. Fees Bonds",
    "E1YOff Floor Comm.",
    "OCC Fees",
    "Options Daily P&L",
    "Options MTD P&L",
    "Options YTD P&L",
    "Stocks Daily P&L",
    "Stocks MTD P&L",
    "Stocks YTD P&L",
    "Bond Accrued Interest",
    "Business Date",
    "Create Date",
    "Create Time",
]


def BofADailyPnL(date: datetime, acct: int) -> tuple[float, float]:
    ###
    # COMB File
    # Dividends Table
    ###
    year_dir = date.strftime("%Y")
    month_dir = date.strftime("%Y%m")
    path = (
        f"C:/gdrive/Shared drives/accounting/Simplex Trading/{year_dir}"
        + f"/BOFA/{month_dir}"
    )
    date_part = date.strftime("%Y%m%d")

    comb_path = path + f"/Files/WSB806TZ.COMBFI26.CSV.{date_part}.csv"
    divs_path = path + "/Dividends_Table.csv"

    comb_file = pd.read_csv(comb_path, names=comb_headers)
    divs_file = pd.read_csv(divs_path)
    divs_on_date = divs_file.loc[
        divs_file["Date"] == date.strftime("%m/%d/%Y")
    ].copy()
    options_pnl = GetOptionsPnL(comb_file=comb_file, acct=acct)
    stock_pnl = GetStockPnL(comb_file=comb_file, acct=acct, divs=divs_on_date)

    return (options_pnl, stock_pnl)


def GetOptionsPnL(comb_file: pd.DataFrame, acct: int) -> float:
    acct_filter = comb_file.loc[comb_file["Account"] == acct]
    daily_options_pnl = acct_filter["Options Daily P&L"].values[0]
    exec_fees = acct_filter["E1Y Exec. Fees - Options"].values[0]
    sec_fees = acct_filter["E1Y SEC Fees Options"].values[0]
    occ_fees = acct_filter["OCC Fees"].values[0]
    net_options_pnl = daily_options_pnl - exec_fees - sec_fees - occ_fees
    return net_options_pnl


def GetStockPnL(
    comb_file: pd.DataFrame, acct: int, divs: pd.DataFrame
) -> float:
    acct_filter = comb_file.loc[comb_file["Account"] == acct]
    daily_stock_pnl = acct_filter["Stocks Daily P&L"].values[0]
    exec_fees = acct_filter["E1Y Exec. Fees - Stocks"].values[0]
    sec_fees = acct_filter["E1Y SEC Fees Stocks"].values[0]

    if acct in ["64440", "64406", "64413", "64441"]:
        div_suffix = "MM"
    else:
        div_suffix = ""

    divs_paid = divs["Divs Paid" + div_suffix].values[0]
    divs_recd = divs["Divs Received" + div_suffix].values[0]
    net_stock_pnl = (
        daily_stock_pnl - exec_fees - sec_fees - divs_paid - divs_recd
    )
    return net_stock_pnl


if __name__ == "__main__":
    date = datetime(2026, 2, 9)
    opt_pnl, stock_pnl = BofADailyPnL(date, 64440)
    print(f"Option PnL = ${opt_pnl:,.2f}")
    print(f"Stock PnL = ${stock_pnl:,.2f}")
