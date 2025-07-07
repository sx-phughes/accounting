# Standard Imports
import pandas as pd

# Package Imports
from MonthEnd.Abn import Base
import AbnCash
import Debug


def get_data() -> None|pd.DataFrame:
    t_plus_eqt = AbnCash.get_eqt_cash_data(Base.t_plus.year, Base.t_plus.month)
    Debug.dprint(t_plus_eqt.columns)
    t_plus_mics = AbnCash.get_mics_cash_data(
        Base.t_plus.year,
        Base.t_plus.month
    )
    
    if not t_plus_eqt.empty:
        eqt_interest = filter_for_interest(t_plus_eqt)
        mics_interest = filter_for_interest(t_plus_mics)
        all_interest = pd.concat([eqt_interest, mics_interest])
    
        interest_w_strat = merge_account_mapping(all_interest)

        return interest_w_strat

def filter_for_interest(cash_data: pd.DataFrame) -> pd.DataFrame:
    phrases = ['AB INT', 'SHORT STOCK', 'HAIRCUT', 'FUT CAP INT']
    mask = '|'.join(phrases)
    
    interest_data = cash_data[cash_data['Description'].str.contains(mask)]
    
    cols = ['DateEntered', 'Account', 'Amount', 'Description']
    interest_data = interest_data[cols]
    
    return interest_data

def merge_account_mapping(interest_data: pd.DataFrame) -> pd.DataFrame:
    return pd.merge(
        interest_data,
        Base.account_mapping[['ACCOUNT', 'Strategy']],
        'left',
        left_on='Account',
        right_on='ACCOUNT'
    )