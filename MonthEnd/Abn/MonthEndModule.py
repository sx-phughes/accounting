# Package Imports
import sys, os

sys.path.append("\\".join([os.environ["HOMEPATH"], "accounting"]))
from MonthEnd.Abn import (
    Base,
    FileGrabber,
    InterestData,
    Positions,
    MonthEndData,
    MiscBreakdown,
)
import Debug

table_names = [
    "interest_data.csv",
    "positions_data.csv",
    "positions_by_pivot.csv",
    "positions_by_category.csv",
    "data_table.csv",
    "misc_breakdown.csv",
]


def run_month_end_files(year: int, month: int, debug=False) -> None:
    if debug:
        Debug.switch_state()

    Debug.dprint("setting globals for Base and FileGrabber")
    Base.set_globals(year, month, "C:/gdrive")
    FileGrabber.get_global_files()

    fn = [
        [InterestData.get_data, "Getting interest data"],
        [Positions.me_get_positions_data, "Getting positions data"],
        [Positions.me_get_positions_pivot, "Pivoting positions data"],
        [Positions.me_get_category_summary, "Summarizing positions data"],
        [MonthEndData.get_data, "Collecting month-end line item data"],
        [MiscBreakdown.get_data, "Creating misc breakdown table"],
    ]

    tables = []
    for func, debugText in fn:
        Debug.dprint(f"{debugText}")
        table = func()
        tables.append(table)

    paired_data_and_names = zip(tables, table_names)

    for table, name in paired_data_and_names:
        save_path = "/".join([Base.get_trading_path(), Base.cm_moyr, name])
        if not table is None:
            table.to_csv(save_path, index=False)
