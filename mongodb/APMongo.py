import asyncio
import pandas as pd
from pymongo import AsyncMongoClient
import json

vendor_field_renamer = {
    "Vendor": "name",
    "Company": "company",
    "Expense Category": "expense_cat",
    "Approver": "approver",
    "Payment Type": "pmt_type",
    "QB Mapping": "qb_name",
    "Account Mapping": "qb_acct",
    "ACH ABA": "ach_aba",
    "ACH Account Number": "ach_account",
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
    "Beneficiary Bank City, State\/Province, Zip\/Postal Code": "ben_bank_city_st_zip",
    "Beneficiary Bank Country": "ben_bank_country",
    "Intermediary Bank ID Type": "int_bank_id_type",
    "Intermediary Bank ID": "int_bank_id",
    "Intermediary Bank Name": "int_bank",
    "Intermediary Bank Address Line 1": "int_bank_addr_1",
    "Intermediary Bank Address Line 2": "int_bank_addr_2",
    "Intermediary Bank City, State\/Province, Zip\/Postal Code": "int_bank_city_st_zip",
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
    "qb_name": "qb",
    "qb_acct": "qb",
    "contact_name": "contact",
    "email": "contact",
    "phone": "contact",
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

    df = pd.read_excel(io=path, sheet_name=sheet)
    renamed = df.rename(columns=vendor_field_renamer)
    return renamed


def convert_row_to_dict(row: pd.Series) -> dict:
    """Converts vendor row into the structured dict"""

    for col in new_cols:
        new_dict = vendor_doc_template.copy()


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


if __name__ == "__main__":
    # convert_vendors_to_dict()
    pass
