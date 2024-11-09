import pandas as pd
import math, re

def find_col_name_row(df: pd.DataFrame):
    cols = list(df.columns.values)
    
    for i, row in df.iterrows():
        vals = []
        for col in cols:
            vals.append(row[col])
            
        # Debug
        # print(vals)
        
        row_is_cols_header = False
        str_count = 0
        non_str_count = 0
        
        for j in range(len(vals)):
            # Debug
            # print(f'Testing value: {vals[j]}')
            
            if j < len(vals) - 1:
                if type(vals[j]) == str:
                    # Debug
                    # print('Type is string, continuing')
                    str_count += 1
                else:
                    non_str_count += 1
                    # Debug
                    # print('Type is not string, continuing')
                    continue
            else:
                if str_count > non_str_count:
                    # Debug
                    # print('Row might be headers')
                    row_is_cols_header = True
                    break
                elif str_count < non_str_count:
                    row_is_cols_header = False
                    # Debug
                    # print('Row is not column headers, breaking')
                    break
        
        clean_vals = []
        
        for val in vals:
            if type(val) == float and math.isnan(val):
                continue
            else:
                clean_vals.append(val)
                
        
        # debug
        # print(clean_vals)
        # if vals[1] == 'Master Ref':
        #     input()
            
        if row_is_cols_header:
            # debug
            # print('entering row double check')
            good_row = False
            for j in range(len(clean_vals)):
                match = re.match(r'^([A-Za-z()/]+\s{1,2})*[A-Za-z()/]+$', str(clean_vals[j]))
                # debug
                # print(f'testing val {clean_vals[i]} for match, match result = {match}')
                if match:
                    # debug
                    # print('matched phrase')
                    if j == len(clean_vals) - 1:
                        good_row = True
                        # debug
                        # print('Row is good')
                    else:
                        continue
                else:
                    break
            # debug
            # if vals[1] == 'Master Ref':
            #     input()
            if good_row:   
                col_names_index = i
                # Debug
                # print(f'col names index = {col_names_index}')
                # print(df.iloc[col_names_index])
                break
    
    return col_names_index