import pandas as pd

path = "C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx"
sheet = "Vendors"

df = pd.read_excel(io=path, sheet_name=sheet)

df.to_json(
    path_or_buf="./vendors.json", orient="records", index=False, lines=True
)
