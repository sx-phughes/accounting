import pandas as pd
import AbnCash
from MonthEnd.Abn import Base, FileGrabber
import Debug

def get_data() -> None:
    Debug.dprint(f"Pulling ABN Cash for {Base.year}-{Base.month}")
    misc_data = AbnCash.get_eqt_cash_data(Base.year, Base.month)
    filtered = misc_data.loc[misc_data['LedgerNumber'] == 8200].copy()
    Debug.dprint(f"misc breakdown table len = {str(len(filtered.index))}")
    return filtered
