import pandas as pd
import math, re
from datetime import datetime
import BrokerFile

def check_date_col(vals):
    for i in range(len(vals)):

            # debug
            # print(first_col_vals[i])

            if type(vals[i]) == datetime or re.search(BrokerFile.BrokerFile.col_patterns['date'], str(vals[i])):
                
                # debug
                # print('Type is datetime')

                if i < len(vals) - 1:
                    continue
                else:

                    # debug
                    # print('no junk rows found')

                    junk_rows_start = math.inf
                    break
            else:
                # debug
                # print('value is not datetime')

                junk_rows_start = i
                break
        
    return junk_rows_start

def check_other_col(vals, col_name=''):
    for i in range(len(vals)):
        try:            
            if math.isnan(vals[i]) == True:
                junk_rows_start = i
                return junk_rows_start
            else:
                continue
        except:
            continue
    
    return 0
        
    
def drop_bottom_rows(df: pd.DataFrame, date_col: str, underlying_col: str, comms_col: str):

    # Dict for rows in which data stops
    stop_rows = {
        date_col: 0,
        underlying_col: 0,
        comms_col: 0
    }
    
    # Iterate through each of the columns
    for col_name in [date_col, underlying_col, comms_col]:

        # Get the column values
        first_col_vals = df[col_name].values.tolist()
        
        # If date column is up, use date col check fn; else, use other col check fn
        # Set stop row value to the found stop row
        if col_name == date_col:
            stop_rows[col_name] = check_date_col(first_col_vals)
        else:
            stop_rows[col_name] = check_other_col(first_col_vals, col_name)
            
    
    final_junk_row_index = min(stop_rows[date_col], stop_rows[underlying_col], stop_rows[comms_col])
        

    
    return final_junk_row_index


def validate_row(row, names_patterns_dict):
    test_results = []
    for i in names_patterns_dict.keys():
        test_results.append(bool(re.search(names_patterns_dict[i], row[i])))
    
    multiply = 1
    for i in test_results:
        multiply = multiply * i
    
    return bool(multiply)