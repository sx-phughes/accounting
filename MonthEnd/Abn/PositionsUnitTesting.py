import pandas as pd
import numpy as np
import sys, os

sys.path.append("/".join([os.environ["HOMEPATH"], "accounting"]))
from MonthEnd.Abn import (
    Positions,
    MonthEndData,
    MiscBreakdown,
    Base,
    FileGrabber,
    InterestData,
)

from Positions import (
    process_positions_data,
    pivot_positions,
    summarize_by_category,
)

path = "C:/gdrive/Shared drives/accounting/Simplex Trading/2025/ABN/202508/20250829-2518-C2518-POSITION.csv"
test_data = pd.read_csv(filepath_or_buffer=path, low_memory=False).fillna(0)
mtm = "Mark To Market Value"
processed_positions = process_positions_data(test_data)
pivoted = pivot_positions(processed_positions)
final = summarize_by_category(pivoted)


##############
# Unit Tests #
##############
def test_raw_data() -> None:
    assert len(test_data.index) == 200890
    assert round(test_data[mtm].sum(), 2) == 407102794.61
    assert round(test_data["OTE"].sum(), 2) == 46451768.75


def test_data_processing() -> None:
    assert len(processed_positions.index) == 200890
    assert round(processed_positions[mtm].sum(), 2) == 407102794.61
    assert round(processed_positions["OTE"].sum(), 2) == 46451768.75


def test_positions_pivot() -> None:
    assert len(pivoted.index) == 177919
    assert round(pivoted[mtm].sum(), 2) == 407102794.61
    assert round(pivoted["OTE"].sum(), 2) == 46451768.75
    assert round(pivoted["Total Value"].sum(), 2) == 453554563.36
    assert pivoted.iloc[0][0] == "1OMER3.520251121Put"


def test_final_summary() -> None:
    assert len(final.index) == 7

    def cat_mask(cat: str) -> pd.Series:
        return final["Category"] == cat

    assert (
        round(
            final.loc[cat_mask("Long Futures Option"), "Total Value"].values[
                0
            ],
            2,
        )
        == 995334931.00
    )
    assert (
        round(final.loc[cat_mask("OTE"), "Total Value"].values[0], 2)
        == 46451768.75
    )
