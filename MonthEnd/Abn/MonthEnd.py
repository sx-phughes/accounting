# Package Imports
from MonthEnd.Abn import Base, FileGrabber, InterestData 
from MonthEnd.Abn import Positions, MonthEndData, MiscBreakdown
import Debug

table_names = [
    'interest_data.csv',
    'positions_data.csv',
    'positions_by_pivot.csv',
    'positions_by_category.csv',
    'data_table.csv',
    'misc_breakdown.csv'
]

def run_month_end_files(year: int, month: int, debug=False) -> None:
    if debug:
        Debug.switch_state()
    
    Debug.dprint("setting globals for Base and FileGrabber")
    Base.set_globals(year, month, "C:/gdrive")
    FileGrabber.get_global_files()

    fn = [
        InterestData.get_data,
        Positions.get_positions_data,
        Positions.get_positions_pivot,
        Positions.get_category_summary,
        MonthEndData.get_data,
        MiscBreakdown.get_data
    ]

    tables = []
    for func in fn:
        Debug.dprint(f"running function {func}")
        table = func()
        tables.append(table)
    
    paired_data_and_names = zip(tables, table_names)

    for table, name in paired_data_and_names:
        save_path = '/'.join([Base.get_trading_path(), name])
        if not table.empty:
            table.to_csv(save_path, index=False)

        
