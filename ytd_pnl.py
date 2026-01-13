from MonthEnd.Transfers.DataGathering import AbnMonthEndStatements
import pandas as pd
from datetime import datetime, timedelta
from calendar import monthrange
import os


def monthend_date(year: int, month: int) -> datetime:
    last_day = monthrange(year, month)[1]
    eom_date = datetime(year, month, last_day)
    if eom_date.weekday() >= 5:
        adjustment = timedelta(4 - eom_date.weekday())
        eom_date = eom_date + adjustment

    return eom_date


def get_account_bal(account: str, year: int, month: int) -> float:
    eom_date = monthend_date(year, month)
    date_str = eom_date.strftime("%Y%m%d")
    me_statements = AbnMonthEndStatements(date_str)
    eqt_bal = me_statements[0]
    mics_bal = me_statements[1]

    eqt_filtered = eqt_bal.loc[eqt_bal["ACCOUNT"] == account]
    mics_filtered = mics_bal.loc[mics_bal["Account"] == account]

    try:
        if eqt_filtered.empty:
            bal = mics_filtered["NetLiq"].values[0]
        elif mics_filtered.empty:
            bal = eqt_filtered["EQUITY"].values[0]
    except IndexError:
        bal = 0

    # print(year, month, bal)

    return bal


def get_multiple_period_balances(
    start_date: tuple[int], end_date: tuple[int], account: str
) -> pd.DataFrame:
    """Returns a dataframe of month-end balances within a given period

    Args:
        start_date (tuple[year, month]): start of date range (inclusive)
        end_date (tuple[year, month]): end of date range (inclusive)
        account (str): account number

    Returns:
        pd.DataFrame: table of month-end equity/net liq values for the account
    """
    dt_start = monthend_date(start_date[0], start_date[1])
    dt_end = monthend_date(end_date[0], end_date[1])
    current = dt_start
    data = {"year": [], "month": [], "account": [], "value": []}
    while current.year <= dt_end.year and current.month <= dt_end.month:
        bal = get_account_bal(account, current.year, current.month)
        data["year"].append(current.year)
        data["month"].append(current.month)
        data["account"].append(account)
        data["value"].append(bal)

        next = current + timedelta(days=15)
        current = monthend_date(next.year, next.month)

    table = pd.DataFrame(data=data)
    return table


def ytd_pnl_gui() -> None:
    os.system("cls")
    title = "# Account PnL #"
    print("#" * len(title))
    print(title)
    print("#" * len(title))

    prompts = (
        "Input start year (yyyy):",
        "Input start month (mm):",
        "Input end year (yyyy):",
        "Input end month (mm):",
        "Input account number:",
    )

    big_len = max([len(x) for x in prompts]) + 1
    responses = []
    for i in range(len(prompts)):
        prompt = prompts[i]
        if len(prompt) == big_len:
            user_input = input(prompt + " ")
        else:
            pad_len = big_len - len(prompt)
            padded = "".join([prompt, " " * pad_len])
            user_input = input(padded)
        if i <= 3:
            responses.append(int(user_input))
        else:
            responses.append(user_input)

    start_date = (responses[0], responses[1])
    end_date = (responses[2], responses[3])
    data = get_multiple_period_balances(
        start_date,
        end_date,
        responses[4],
    )

    pd.set_option("display.max_rows", None)
    print("\n\n", data, "\n\n")

    save_data = input("Save data to disk?")
    if save_data in ("y", "yes", "Y", "Yes"):
        str_start = str(start_date[0]) + str(start_date[1])
        str_end = str(end_date[0]) + str(end_date[1])
        f_name = f"{str_start}_{str_end}_{responses[4]}_pnl.csv"
        path = os.environ["HOMEPATH"]
        data.to_csv("/".join([path, "Downloads", f_name]))


if __name__ == "__main__":
    ytd_pnl_gui()
