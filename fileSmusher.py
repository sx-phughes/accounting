import os
import pandas as pd

dir = "C:/gdrive/Shared drives/accounting/Simplex Trading/2025/BOFA/202501/DivFiles"

headers = [
    "Record ID",
    "Record#",
    "Business Date",
    "Reference #",
    "Account #",
    "Security Type",
    "CUSIP #",
    "ISIN #",
    "SEDOL #",
    "SYMBOL",
    "Security Description",
    "B/S",
    "QTY",
    "Debt Credit Code",
    "Amount",
    "Type of Entry",
    "Origin Code",
    "Memo code",
    "Symbol 21",
]

df = pd.DataFrame(columns=headers)
os.chdir(dir)

for file in os.listdir():
    file_data = pd.read_csv(
        filepath_or_buffer=file, names=headers, low_memory=False
    )
    div_df = file_data[
        (file_data["Origin Code"] != "DIVP")
        & (file_data["Origin Code"] == "DV")
    ].copy()
    if df.empty and not div_df.empty:
        df = div_df
    elif not div_df.empty and not df.empty:
        df = pd.concat([df, div_df])

df.to_csv("dividend recon sheet.csv")
