# IDB Rec Base

import pandas as pd
import numpy as np
import re, math
from find_col_name_row import find_col_name_row
from drop_bottom_rows import drop_bottom_rows
from datetime import datetime


class BrokerFile(pd.DataFrame):
    var = 2
    col_patterns = {
        "date": r"\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|^\d{6,8}$|^[1-3]?[0-9][-/.][A-Za-z]{3}[-/.]20\d{2}",
        "underlying": r"^[A-Z]{1,4}$|^[A-Z]{1,4}[23]\d{5}[CP]\d{8}$",
        "comms": r"\d{1,5}.?\d{0,2}",
    }

    def __init__(self, path, sheet_name):
        super().__init__(pd.read_excel(path, sheet_name, engine="openpyxl"))
        self.clean_broker_file()

    def clean_broker_file(self):
        # Cut off junk columns on right-hand side
        empty_cols = [col for col in self.columns if self[col].isnull().all()]

        # debug
        # for i in empty_cols:
        #     print(i)

        self.drop(columns=empty_cols, inplace=True)

        if not self.cols_are_good():
            # print('\nCols not good, finding column headers\n')
            # Get row with column names
            cols_index = find_col_name_row(self)

            # Get column names and rename to proper headers
            main_row = list(self.iloc[cols_index])

            # Debug
            # print(main_row)

            # Checking to see if concat top row is needed
            col_counts = [main_row.count(i) for i in main_row]
            if sum(col_counts) > len(col_counts):

                # Debug
                # print('getting supp row')

                supp_row = list(self.iloc[cols_index - 1])
                row = [
                    supp + main if type(supp) == str else main
                    for supp, main in zip(supp_row, main_row)
                ]
            else:
                row = main_row

            renamer = {
                old: new for old, new in zip(list(self.columns.values), row)
            }
            self.rename(columns=renamer, inplace=True)
            self.columns = self.columns.fillna("Unnamed")
            for i in self.columns:
                if "Unnamed" in i:
                    self.drop(columns=["Unnamed"], inplace=True)
                    break
                else:
                    continue

            # Drop top junk rows
            self.drop(index=range(cols_index + 1), inplace=True)
            self.reset_index(drop=True, inplace=True)

        # debug
        # print(broker_file)

        # Fill down blank rows in date column with dates
        date_col = self.find_col(BrokerFile.col_patterns["date"], "date")
        self[date_col] = self.copy_dates(date_col)

        underlying_col = self.find_col(
            BrokerFile.col_patterns["underlying"], "underlying"
        )
        comms_col = self.find_col(BrokerFile.col_patterns["comms"], "comms")

        # Remove other columns
        drop_cols = [
            col
            for col in self.columns.tolist()
            if col not in [date_col, underlying_col, comms_col]
        ]
        self.drop(columns=drop_cols, inplace=True)

        # Drop bottom junk rows
        stop = drop_bottom_rows(self, date_col, underlying_col, comms_col)

        if stop > 0:
            self.drop(index=range(stop, len(self.index)), inplace=True)
            self.reset_index(drop=True, inplace=True)
            return True

    def comp_df(self):
        return self.clean_data(self.broker_file)

    def clean_data(self):
        # Create clean dataframe
        clean_df = pd.DataFrame()

        # Find cols with needed data and add to clean dataframe
        for col_str in BrokerFile.col_patterns.keys():

            # Debug
            # print(f'col_str = {col_str}')
            # print(f'pattern = {BrokerFile.col_patterns[col_str]}')

            match_str = self.find_col(
                self, BrokerFile.col_patterns[col_str], col_str
            )
            if match_str:

                # Debug
                # print(f'found col match for {col_str} in col {match_str}')

                clean_df[col_str] = self[match_str]

        return clean_df

    def find_col(self, pattern: str, col_name: str) -> str:
        """
        Find column in df matching pattern.\n
        Args:\n
        \tbroker_file: pd.DataFrame, df of all data\n
        \tpattern: str, data pattern to search for\n
        \tcol_name: str, new column name to use\n

        Returns: str with df column name that has needed data
        """
        first_row = list(self.iloc[0])
        cols = list(self.columns)

        # Test first value in each column for match result
        for i in range(len(cols)):
            search = re.search(pattern, str(first_row[i]), re.IGNORECASE)

            # debug
            # if col_name == 'comms':
            # print(f'searching for {col_name}, testing value {str(first_row[i])}, match result: {search}')

            if search and search.string != "nan":
                if col_name == "comms":
                    # Additional logic for comms column
                    if not self.comms_is_correct(self[cols[i]]):
                        continue
                    else:
                        return cols[i]
                elif col_name == "underlying":
                    # Additional logic for underlying column ID: can't have these terms as the data point
                    if not self.underlying_is_correct(self[cols[i]]):
                        continue
                    else:
                        return cols[i]
                elif col_name == "date":
                    if not self.date_is_correct(first_row[i]):
                        continue
                    else:
                        return cols[i]
                else:
                    return cols[i]
            else:
                continue

    def copy_dates(self, date_col: str) -> pd.DataFrame:
        """
        Copies down dates in the identified date row if necessary\n
        Args:\n
        \tbroker_file: pd.DataFrame, commissions data\n
        \tdate_col: str, name of date column
        """

        self["is_nan"] = self[date_col].isna()
        new_data = []
        cur_val = 0

        for i, row in self.iterrows():
            if not row["is_nan"]:
                cur_val = row[date_col]
                new_data.append(row[date_col])
            else:
                new_data.append(cur_val)

        self.drop(columns="is_nan", inplace=True)

        self[date_col] = new_data

        return new_data

    def date_is_correct(self, val):
        if re.search(r"\d{6}", str(val)):
            year = int(str(val)[0:4])
            month = int(str(val)[4:6])
            day = int(str(val)[6:])
            if 2024 < year < 2040:
                if 1 <= month <= 12:
                    if 1 <= day <= 31:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return True

    def underlying_is_correct(self, col):
        # Keyword testing
        for k in col.values:
            for j in ["SIMP", "buy", "sell", "put", "call", "Trader Name"]:
                if re.search(j, str(k), re.IGNORECASE):
                    return False
                else:
                    continue

        # Testing for all same values
        unique_values = []
        for k in col.values:
            if k in unique_values:
                continue
            else:
                unique_values.append(k)
        if len(unique_values) == 1:
            return False

        return True

    def comms_is_correct(self, column: pd.Series):
        col_is_good = False
        try:
            column = column.astype(float)
        except:
            # print('return 1')
            return col_is_good

        sum = column.sum()
        if sum < 40:
            # print('return 2')
            return col_is_good
        elif sum > 300000:
            # print('return 3')
            return col_is_good
        elif sum / len(column.index) < 10:
            # print('return 4')
            return col_is_good

        if re.search(
            "price|strike|ref|quantity|qty|occ|buy|sell|contracts",
            column.name,
            re.IGNORECASE,
        ):
            # print('return 5')
            return col_is_good

        # print('column is good')
        col_is_good = True
        return col_is_good

    def cols_are_good(self):
        cols = list(self.columns.values)

        for i in cols:
            if "Unnamed" in i:
                return False
            else:
                continue

        return True
