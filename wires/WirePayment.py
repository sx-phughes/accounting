import re, math
from datetime import datetime
import pandas as pd
from Fields import fields
from TemplateFields import template_fields

company_ids = {
    "Holdings": "000000424542988",
    "Investments": "000000644684771",
    "Technologies": "000000559711101",
    "Trading": "000000885007310",
}
company_names = {
    "Holdings": "SIMPLEX HOLDCO, LLC",
    "Investments": "SIMPLEX INVESTMENTS LLC",
    "Technologies": "SIMPLEX TECHNOLOGIES",
    "Trading": "SIMPLEX TRADING, LLC",
}

company_abas = {
    "Holdings": "071000013",
    "Investments": "071000013",
    "Technologies": "071000013",
    "Trading": "071000013",
}


class WireField:
    """Object containing information related to a single field in a wire
    payment line."""

    def __init__(self, field_name, field_len: int, field_value):
        self.name = field_name
        self.len = field_len
        self.val = field_value

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, field_value):
        if self.len == 0:
            field_value = ""
        elif len(field_value) > self.len:
            field_value = field_value[0 : self.len]
        else:
            field_value = field_value

        self._val = field_value


class Vendor:
    """Object for containing information about a specific vendor."""

    vendor_info = pd.read_excel(
        "C:/gdrive/Shared Drives/accounting/patrick_data_files/ap/Vendors.xlsx",
        "Vendors",
    ).fillna("")

    def __init__(self, vendor: str):
        self.vendor = vendor
        self.get_vendor_info(vendor)

    def __repr__(self):
        return f"Vendor object for '{self.vendor}'"

    def get_vendor_info(self, vendor):
        """Pulls vendor information about the passed parameter (vendor) and
        stores it in object attributes."""

        vendor_row = Vendor.vendor_info.loc[
            Vendor.vendor_info["Vendor"] == vendor
        ]
        self.template = vendor_row["Wire Template"].values[0]
        self.id = vendor_row["Beneficiary ID"].values[0]
        self.id_type = vendor_row["Beneficiary ID Type"].values[0]
        self.beneficiary_country = vendor_row["Beneficiary Country"].values[0]
        self.bank_id_type = vendor_row["Beneficiary Bank ID Type"].values[0]
        self.bank_id = vendor_row["Beneficiary Bank ID"].values[0]
        self.bank_name = vendor_row["Beneficiary Bank Name"].values[0]
        self.bank_address1 = vendor_row[
            "Beneficiary Bank Address Line 1"
        ].values[0]
        self.bank_address2 = vendor_row[
            "Beneficiary Bank Address Line 2"
        ].values[0]
        self.bank_address3 = vendor_row[
            "Beneficiary Bank City, State/Province, Zip/Postal Code"
        ].values[0]
        self.bank_country = vendor_row["Beneficiary Bank Country"].values[0]
        self.intermediary_id_type = vendor_row[
            "Intermediary Bank ID Type"
        ].values[0]
        self.intermediary_id_value = vendor_row["Intermediary Bank ID"].values[
            0
        ]
        self.intermediary_name = vendor_row["Intermediary Bank Name"].values[0]
        self.intermediary_address1 = vendor_row[
            "Intermediary Bank Address Line 1"
        ].values[0]
        self.intermediary_address2 = vendor_row[
            "Intermediary Bank Address Line 2"
        ].values[0]
        self.intermediary_address3 = vendor_row[
            "Intermediary Bank City, State/Province, Zip/Postal Code"
        ].values[0]
        self.intermediary_country = vendor_row[
            "Intermediary Bank Country"
        ].values[0]


class Field:
    def __init__(self, field_info: list, value=None):
        self.f_name = field_info[0]
        self.f_length = field_info[1]
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        str_val = str(value)

        if self.f_length == 0 or value is None:
            str_val = ""
        elif len(str_val) > self.f_length:
            str_val = str_val[0 : self.f_length]
        else:
            str_val = str_val

        self._value = str_val


field_objs = []

for i in fields:
    section = [Field(j) for j in i]

    field_objs.append(section)

template_field_objs = []

for i in template_fields:
    section = [Field(j) for j in i]

    template_field_objs.append(section)


class WirePayment:
    """Object for constructing a single wire payment from passed information."""

    fields = field_objs
    template_fields = template_field_objs

    def __init__(
        self,
        orig_bank_id,
        orig_account,
        amount,
        value_date: datetime,
        vendor: Vendor,
        details: str,
        template: bool = False,
    ):
        self.orig_bank_id = orig_bank_id
        self.orig_account = orig_account
        self.amount = amount
        self.value_date = value_date
        self.vendor = vendor
        self.details = details
        self.template = template

        if template:
            self.record_fields = WirePayment.template_fields[0]
            self.trx_fields = WirePayment.template_fields[1]
            self.vd_fields = WirePayment.template_fields[2]
            self.trx_det_fields = WirePayment.template_fields[3]
            self.reg_fields = WirePayment.template_fields[4]
            self.b2b_fields = WirePayment.template_fields[5]
            self.note_fields = WirePayment.template_fields[6]
            self.email_fields = WirePayment.template_fields[7]
        else:
            self.record_fields = WirePayment.fields[0]
            self.trx_fields = WirePayment.fields[1]
            self.vd_fields = WirePayment.fields[2]
            self.beneficiary_fields = WirePayment.fields[3]
            self.ben_bank_fields = WirePayment.fields[4]
            self.unused_1 = WirePayment.fields[5]
            self.int_bank_fields = WirePayment.fields[6]
            self.obo_fields = WirePayment.fields[7]
            self.unused_2 = WirePayment.fields[8]
            self.trx_det_fields = WirePayment.fields[9]
            self.unused_3 = WirePayment.fields[10]
            self.reg_fields = WirePayment.fields[11]
            self.b2b_fields = WirePayment.fields[12]
            self.other_fields = WirePayment.fields[13]

    def __len__(self):
        return 1

    def create_payment(self):
        template_func_list = [
            self.set_record,
            self.set_trx,
            self.set_vd,
            self.set_details,
            self.set_reg,
            self.set_b2b_dets,
            self.set_note,
            self.set_email,
        ]

        func_list = [
            self.set_record,
            self.set_trx,
            self.set_vd,
            self.set_ben,
            self.set_ben_bank,
            self.set_int_bank,
            self.set_details,
            self.set_b2b_dets,
            self.set_other,
        ]

        fields = []

        if self.template:
            for i in range(len(template_func_list)):
                fields += [j.value for j in template_func_list[i]()]
        else:
            for i in range(len(func_list)):

                fields += [j.value for j in func_list[i]()]

                if i == 4:
                    fields += [j.value for j in self.unused_1]
                elif i == 5:
                    fields += [j.value for j in self.obo_fields]
                    fields += [j.value for j in self.unused_2]
                elif i == 6:
                    fields += [j.value for j in self.unused_3]
                    fields += [j.value for j in self.reg_fields]

        return fields

    def set_record(self):
        if self.template:
            self.record_fields[0].value = "PT"
        else:
            self.record_fields[0].value = "P"

        return self.record_fields

    def set_trx(self):
        if self.template:
            values = [
                self.orig_bank_id,
                self.orig_account,
                self.vendor.template,
                "",
                self.amount,
                "",
                "",
            ]
        else:
            values = [
                "WIRES",
                self.orig_bank_id,
                self.orig_account,
                "N",
                "USD",
                self.amount,
                "",
                "",
                "",
                "",
                "",
            ]

        for i in range(len(self.trx_fields)):
            self.trx_fields[i].value = values[i]

        return self.trx_fields

    def set_vd(self):
        self.vd_fields[0].value = self.value_date

        return self.vd_fields

    def set_ben(self):
        values = [
            self.vendor.id_type,
            self.vendor.id,
            self.vendor.vendor,
            "",
            "",
            "",
            "",
            self.vendor.beneficiary_country,
            "",
        ]

        for i in range(len(self.beneficiary_fields)):
            self.beneficiary_fields[i].value = values[i]

        return self.beneficiary_fields

    def set_ben_bank(self):
        values = [
            "",
            self.vendor.bank_id_type,
            self.vendor.bank_id,
            self.vendor.bank_name,
            self.vendor.bank_address1,
            self.vendor.bank_address2,
            self.vendor.bank_address3,
            self.vendor.bank_country,
            "",
            "",
        ]

        for i in range(len(self.ben_bank_fields)):
            self.ben_bank_fields[i].value = values[i]

        return self.ben_bank_fields

    def set_int_bank(self):
        values = [
            self.vendor.intermediary_id_type,
            self.vendor.intermediary_id_value,
            self.vendor.intermediary_name,
            self.vendor.intermediary_address1,
            self.vendor.intermediary_address2,
            self.vendor.intermediary_address3,
            self.vendor.intermediary_country,
            "",
            "",
        ]

        for i in range(len(self.int_bank_fields)):
            self.int_bank_fields[i].value = values[i]

        return self.int_bank_fields

    def set_details(self):
        if self.template:
            values = (
                [
                    "",
                    "",
                    "",
                ]
                + self.details
                + [""] * 8
            )
        else:
            values = [
                "",
                "",
                "",
            ] + self.details

        for i in range(len(self.trx_det_fields)):
            self.trx_det_fields[i].value = values[i]

        return self.trx_det_fields

    def set_b2b_dets(self):
        if self.template:
            for i in range(len(self.b2b_fields)):
                self.b2b_fields[i].value = ""
        else:
            self.b2b_fields[18].value = "N"
            self.b2b_fields[20].value = "OUR"

        return self.b2b_fields

    def set_other(self):
        self.other_fields[2].value = "N"

        return self.other_fields

    def set_reg(self):
        for i in range(len(self.reg_fields)):
            self.reg_fields[i].value = ""

        return self.reg_fields

    def set_note(self):
        self.note_fields[0].value = ""

        return self.note_fields

    def set_email(self):
        for i in range(len(self.email_fields)):
            self.email_fields[i].value = ""

        return self.email_fields

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, details: str):
        detail_list = [[], [], [], []]

        num_lines = min(math.ceil(len(details) / 35), 4)
        for i in range(num_lines):
            detail_list[i] = details[i * 35 : (i + 1) * 35]

        for i in range(len(detail_list)):
            if len(detail_list[i]) == 0:
                detail_list[i] = ""

        self._details = detail_list

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount: float):
        if re.match(r"\d+.\d{1,2}", str(amount)):
            self._amount = amount
        elif re.match(r"\d+.\d{3,}", str(amount)):
            self._amount = round(amount, 2)
        else:
            raise TypeError

    @property
    def value_date(self):
        return self._value_date

    @value_date.setter
    def value_date(self, value_date: datetime):
        self._value_date = value_date.strftime("%Y%m%d")
