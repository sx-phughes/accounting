import copy
import asyncio
from pymongo import AsyncMongoClient

from APMongo import connect_to_ap, print_dict

company_doc_template = {
    "company": "",
    "aba": "",
    "nacha_name": "",
    "nacha_id": "",
    "wire_name": "",
    "wire_id": "",
}

nacha_ids = {
    "Holdco": "9542988001",
    "Investments": "9684771001",
    "Technologies": "9711101001",
    "Trading": "9007310001",
}
nacha_names = {
    "Holdco": "SIMPLEX HOLDCO",
    "Investments": "SIMPLEX INVESTMENTS LLC",
    "Technologies": "SIMPLEX TECHNOLOGIES",
    "Trading": "SIMPLEX TRADING, LLC",
}

wire_ids = {
    "Holdco": "000000424542988",
    "Investments": "000000644684771",
    "Technologies": "000000559711101",
    "Trading": "000000885007310",
}
wire_names = {
    "Holdco": "SIMPLEX HOLDCO, LLC",
    "Investments": "SIMPLEX INVESTMENTS LLC",
    "Technologies": "SIMPLEX TECHNOLOGIES",
    "Trading": "SIMPLEX TRADING, LLC",
}


def create_company_docs() -> list[dict]:
    """Creates a document for each of the opcos."""

    companies = [
        "Holdco",
        "Technologies",
        "Trading",
        "Investments",
    ]
    co_docs = []
    for co in companies:
        new_doc = map_company_to_doc(co)
        co_docs.append(new_doc)
    return co_docs


def map_company_to_doc(company: str) -> dict:
    """Maps company info to document structure."""

    new = copy.deepcopy(company_doc_template)

    new["company"] = company
    new["aba"] = "071000013"
    new["nacha_name"] = nacha_names[company]
    new["nacha_id"] = nacha_ids[company]
    new["wire_name"] = wire_names[company]
    new["wire_id"] = wire_ids[company]

    return new


async def upload_company_docs() -> None:
    """Creates a new collection for the company info documents and uploads the
    company data."""

    client = await connect_to_ap()
    db = client["accountspayable"]
    await db.create_collection("payments")
    pmt_cluster = db["payments"]

    docs = create_company_docs()
    for i in docs:
        print_dict(i)

    result = await pmt_cluster.insert_many(docs)
    print(result)


if __name__ == "__main__":
    asyncio.run(upload_company_docs())
