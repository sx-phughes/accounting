import pandas as pd

path = "C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx"
sheet = "Vendors"

df = pd.read_excel(io=path, sheet_name=sheet)

df.to_json(
    path_or_buf="./vendors.json", orient="records", index=False, lines=True
)

vendors_txt = ""

with open("./vendors.json", "r") as file:
    vendors_txt = file.read()


split = vendors_txt.split("}")
joined = "},".join(split)

final = "{" + joined + "}"

with open("./formatted_vendors.json", "w") as f:
    f.write(final)
