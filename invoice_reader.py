import pypdf
import anthropic
import os
import base64

path = "C:/Users/phughes_simplextradi/Downloads/Provantage-Receipt-9928896.pdf"
with open(path, "rb") as pdf:
    pdf_data_prelim = pdf.read()

pdf_data = base64.standard_b64encode(pdf_data_prelim).decode("utf-8")

with open("../anthropic_key.txt") as f:
    key = f.read().replace("\n", "")

client = anthropic.Anthropic(api_key=key)
message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2500,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {
                    "type": "text",
                    "text": "Can you return the vendor and amount of this invoice in the form of a python dictionary with keys 'vendor' and 'amount'?",
                },
            ],
        }
    ],
)

with open("data.py", "w") as f:
    data = message.content[0].text.replace("`", "")
    clean = data.replace("python", "")[1:]
    f.write("invoice_1 = " + clean)

import data

print(data.invoice_1)
