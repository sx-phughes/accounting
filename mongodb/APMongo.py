import asyncio
import pandas as pd
import numpy as np
from pymongo import AsyncMongoClient
import json
import copy

vendor_field_renamer = {
    "Vendor": "name",
    "Company": "company",
    "Expense Category": "expense_cat",
    "Approver": "approver",
    "Payment Type": "pmt_type",
    "QB Mapping": "qb_name",
    "Account Mapping": "qb_acct",
    "ACH ABA": "ach_aba",
    "ACH Account Number": "ach_acct",
    "ACH Vendor Name": "ach_name",
    "IDB Broker": "idb",
    "Contact": "contact_name",
    "Email": "email",
    "Phone": "phone",
    "Wire Template": "template",
    "Beneficiary ID": "ben_id",
    "Beneficiary ID Type": "ben_id_type",
    "Beneficiary Country": "ben_country",
    "Beneficiary Bank ID Type": "ben_bank_id_type",
    "Beneficiary Bank ID": "ben_bank_id",
    "Beneficiary Bank Name": "ben_bank",
    "Beneficiary Bank Address Line 1": "ben_bank_addr_1",
    "Beneficiary Bank Address Line 2": "ben_bank_addr_2",
    "Beneficiary Bank City, State/Province, Zip/Postal Code": "ben_bank_city_st_zip",
    "Beneficiary Bank Country": "ben_bank_country",
    "Intermediary Bank ID Type": "int_bank_id_type",
    "Intermediary Bank ID": "int_bank_id",
    "Intermediary Bank Name": "int_bank",
    "Intermediary Bank Address Line 1": "int_bank_addr_1",
    "Intermediary Bank Address Line 2": "int_bank_addr_2",
    "Intermediary Bank City, State/Province, Zip/Postal Code": "int_bank_city_st_zip",
    "Intermediary Bank Country": "int_bank_country",
}

new_cols = []
for old_col in vendor_field_renamer.keys():
    new_cols.append(vendor_field_renamer[old_col])

vendor_doc_template = {
    "name": "",
    "company": "",
    "expense_cat": "",
    "approver": "",
    "pmt_type": "",
    "idb": False,
    "qb": {
        "qb_name": "",
        "qb_acct": 0,
    },
    "contact": {
        "contact_name": "",
        "email": "",
        "phone": "",
    },
    "ach": {
        "ach_name": "",
        "ach_acct": "",
        "ach_aba": "",
    },
    "wire": {
        "template": "",
        "ben_id": "",
        "ben_id_type": "",
        "ben_country": "",
        "ben_bank_id_type": "",
        "ben_bank_id": "",
        "ben_bank": "",
        "ben_bank_addr_1": "",
        "ben_bank_addr_2": "",
        "ben_bank_city_st_zip": "",
        "ben_bank_country": "",
        "int_bank_id_type": "",
        "int_bank_id": "",
        "int_bank": "",
        "int_bank_addr_1": "",
        "int_bank_addr_2": "",
        "int_bank_city_st_zip": "",
        "int_bank_country": "",
    },
}

vendor_field_sub_obj_mapping = {
    "name": "",
    "company": "",
    "expense_cat": "",
    "approver": "",
    "pmt_type": "",
    "idb": "",
    "qb_name": "qb",
    "qb_acct": "qb",
    "contact_name": "contact",
    "email": "contact",
    "phone": "contact",
    "ach_name": "ach",
    "ach_acct": "ach",
    "ach_aba": "ach",
    "template": "wire",
    "ben_id": "wire",
    "ben_id_type": "wire",
    "ben_country": "wire",
    "ben_bank_id_type": "wire",
    "ben_bank_id": "wire",
    "ben_bank": "wire",
    "ben_bank_addr_1": "wire",
    "ben_bank_addr_2": "wire",
    "ben_bank_city_st_zip": "wire",
    "ben_bank_country": "wire",
    "int_bank_id_type": "wire",
    "int_bank_id": "wire",
    "int_bank": "wire",
    "int_bank_addr_1": "wire",
    "int_bank_addr_2": "wire",
    "int_bank_city_st_zip": "wire",
    "int_bank_country": "wire",
}


async def connect_to_ap() -> AsyncMongoClient:
    """Connect to accounts payable mongo cluster"""

    cxn = "mongodb+srv://phughes_db_user:{db_password}@apcluster.kdvs70f.mongodb.net/?retryWrites=true&w=majority&appName=apCluster"
    pw = input("DB password:")
    client = AsyncMongoClient(cxn.format(db_password=pw))
    return client


async def main() -> None:
    try:
        client = await connect_to_ap()

        database = client["accountspayable"]
        vendors = database["vendors"]

        objs = get_vendors_as_dicts()

        vendors.insert_one(objs[0])
        query = {"name": "3MD Relocation Services"}

        await client.close()
    except Exception as e:
        raise Exception(
            "Unable to find the document due to the following error: ", e
        )


def get_vendors_data() -> pd.DataFrame:
    """Retrieve vendors data from excel file"""

    path = (
        "C:/gdrive/Shared drives/accounting/patrick_data_files/ap/Vendors.xlsx"
    )
    sheet = "Vendors"

    df = pd.read_excel(io=path, sheet_name=sheet, dtype=str)
    renamed = df.rename(columns=vendor_field_renamer)
    renamed["qb_acct"] = renamed["qb_acct"].fillna(0).astype(np.int32)
    print(*renamed.columns, sep="\n")
    return renamed


def convert_row_to_dict(row: pd.Series) -> dict:
    """Converts vendor row into the structured dict"""

    new_dict = copy.deepcopy(vendor_doc_template)
    for col in new_cols:
        sub = vendor_field_sub_obj_mapping[col]
        if sub:
            try:
                if np.isnan(row[col]):
                    continue
                else:
                    new_dict[sub][col] = row[col]
            except:
                new_dict[sub][col] = row[col]
        elif col == "idb":
            try:
                if np.isnan(row[col]):
                    new_dict[col] = False
            except:
                new_dict[col] = True
        else:
            try:
                if np.isnan(row[col]):
                    continue
                else:
                    new_dict[col] = row[col]
            except:
                new_dict[col] = row[col]
    return new_dict


def read_vendors_json() -> list[str]:
    text = ""
    with open("./vendors.json", "r") as f:
        text = f.read()
    json_list = text.split("\n\n\n")
    return json_list


def get_vendors_as_dicts() -> None:
    list_vendors_json = read_vendors_json()
    vendors_as_dicts = []
    for obj_str in list_vendors_json:
        new_dict = json.loads(obj_str)

        vendors_as_dicts.append(new_dict)
    return vendors_as_dicts


def print_dict(obj: dict) -> None:
    keys = list(obj.keys())
    print("{")
    for key in keys:
        if isinstance(obj[key], str) or isinstance(obj[key], bool):
            print(f"\t'{key}': '{obj[key]}'")
        elif isinstance(obj[key], dict):
            sub_dict = obj[key]
            print(f"\t'{key}':", "{", sep=" ")
            sub_dict_keys = list(sub_dict.keys())
            for sub_dict_key in sub_dict_keys:
                print(f"\t\t'{sub_dict_key}': '{sub_dict[sub_dict_key]}'")
            print("\t}")
    print("}")


async def upload_vendors_to_db() -> None:
    vendors = get_vendors_data()
    vendor_docs = []
    count = 0
    # lim = 3
    for i, row in vendors.iterrows():
        doc = convert_row_to_dict(row)
        vendor_docs.append(doc)
        count += 1
        # if count >= lim:
        #     break

    # for i in range(lim):
    # print_dict(vendor_docs[i])

    client = await connect_to_ap()
    db = client["accountspayable"]
    vendors_cluster = db["vendors"]
    object_ids = await vendors_cluster.insert_many(vendor_docs)
    print(object_ids)


if __name__ == "__main__":
    pass
