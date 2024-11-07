import pandas as pd
import math

def drop_bottom_rows(df: pd.DataFrame):
    cols = list(df.columns.values)
    
    first_col_vals = df[cols[0]].values
    
    for i in range(len(first_col_vals)):
        if type(first_col_vals[i]) == str:
            continue
        elif math.isnan(first_col_vals[i]):
            junk_rows_start = i
            break
        
    return junk_rows_start