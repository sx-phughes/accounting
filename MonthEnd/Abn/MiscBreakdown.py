import pandas as pd
import AbnCash
from MonthEnd.Abn import Base, FileGrabber
import Debug

def get_data() -> None:
    misc_data = AbnCash.get_eqt_cash_data(Base.year, Base.month)
    return misc_data.loc[misc_data['LedgerNumber'] == 8200]