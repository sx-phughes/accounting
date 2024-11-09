import pandas as pd
import math
from datetime import datetime

def drop_bottom_rows(df: pd.DataFrame):
    cols = list(df.columns.values)
    
    first_col_vals = df[cols[0]].values
    
    for i in range(len(first_col_vals)):
        # debug
        # print(first_col_vals[i])
        if type(first_col_vals[i]) == str or type(first_col_vals[i]) == datetime:
            # # debug
            # print('Type is string or datetime')
            if i < len(first_col_vals) - 1:
                continue
            else:
                # debug
                # print('no junk rows found')
                junk_rows_start = 0
        elif math.isnan(first_col_vals[i]):
            # debug
            # print('value is nan')
            junk_rows_start = i
            break
    
    return junk_rows_start