import pandas as pd
import math

def find_col_name_row(df: pd.DataFrame):
    cols = list(df.columns.values)
    
    for i, row in df.iterrows():
        vals = []
        for col in cols:
            vals.append(row[col])
            
        # Debug
        print(vals)
        
        row_is_cols_header = False
        
        for j in range(len(vals)):
            # Debug
            print(f'Testing value: {vals[j]}')
            
            if type(vals[j]) == str:
                # Debug
                print('Type is string, continuing')
                
                if j == len(vals) - 1:
                    row_is_cols_header = True
                    break
                
                continue
            else:
                # Debug
                print('Type is not string, breaking')
                break
            
        if row_is_cols_header:
            col_names_index = i
            # Debug
            print(f'col names index = {col_names_index}')
            print(df.iloc[col_names_index])
            break
    
    return col_names_index