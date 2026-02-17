from datetime import datetime, timedelta
import pandas as pd
from patrick_functions.DateFunctions import last_biz_day
from zipfile import ZipFile
import pandas as pd
import re, pypdf, os
from EoyExtractPageText import *


class AbnBase:
    def __init__(self, close_year, close_month, google_drive_root="C:/gdrive"):
        self.year = close_year
        self.month = close_month
        self.gdrive_root = google_drive_root

        self.t_minus_year, self.t_minus_month = (
            self.t_minus.year,
            self.t_minus.month,
        )
        self.t_plus_year, self.t_plus_month = (
            self.t_plus.year,
            self.t_plus.month,
        )

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year: int):
        self._year = year

    @property
    def month(self):
        return self._month

    @month.setter
    def month(self, month: int):
        self._month = month

    @property
    def eom(self):
        return last_biz_day(self.year, self.month)

    @property
    def moyr(self):
        return datetime(self.year, self.month, 1).strftime("%Y%m")

    @property
    def trading_path(self):
        return (
            self.gdrive_root
            + f"/Shared drives/accounting/Simplex Trading/{self.year}/ABN"
        )

    @property
    def archive_path(self):
        return self.gdrive_root + "/Shared drives/Clearing Archive/ABN_Archive"

    @property
    def t_minus(self):
        t0 = datetime(self.year, self.month, 1)
        td = timedelta(days=20)
        t_minus = t0 - td
        t_minus_eom = t_minus + timedelta(
            days=(last_biz_day(t_minus.year, t_minus.month).day - t_minus.day)
        )

        return t_minus_eom

    @property
    def t_plus(self):
        t0 = datetime(self.year, self.month, 28)
        td = timedelta(days=20)
        t_plus = t0 + td
        t_plus_eom = t_plus + timedelta(
            days=(last_biz_day(t_plus.year, t_plus.month).day - t_plus.day)
        )

        return t_plus_eom


## Files Needed ##
#   1. yyyymmdd-2518-C2518-CSVCASH_AC.csv.zip
#   2. yyyymmdd-2518-C2518-POSITION.csv.zip


class MonthlyStatement:
    index = {}

    def __init__(self, path, file_name):
        self.path = path
        self.fname = file_name

    def __str__(self):
        return self.fname

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, account):
        MonthlyStatement.index.update({account: self})
        self._account = account

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        self._date = datetime.strptime(date, "%Y%m%d")

    @property
    def margin(self):
        return self._margin

    @margin.setter
    def margin(self, margin):
        self._margin = margin

    @property
    def abn_num(self):
        return self._abn_num

    @abn_num.setter
    def abn_num(self, num):
        self._abn_num = num


class AbnFileGrabber(AbnBase):
    def __init__(self, year, month):
        super().__init__(year, month)

        self.last_biz_day = last_biz_day(year, month)
        # self.moyr = self.last_biz_day.strftime('%Y%m')
        self.date_str = self.last_biz_day.strftime("%Y%m%d")

    def main(self):
        self.get_file_dirs()
        self.unzip()

        return (
            pd.read_csv(self.csvcash, low_memory=False),
            pd.read_csv(self.position, low_memory=False),
        )

    def get_file_dirs(self):
        self.csvcash_name = f"{self.date_str}-2518-C2518-CSVCASH_AC.csv.zip"
        self.position_name = f"{self.date_str}-2518-C2518-POSITION.csv.zip"

        self.csvcash_zip = (
            self.archive_path + f"/{self.date_str}/{self.csvcash_name}"
        )
        self.position_zip = (
            self.archive_path + f"/{self.date_str}/{self.position_name}"
        )

    def unzip(self):
        paths_list = [
            [
                self.csvcash_zip,
                self.csvcash_zip.split("/")[-1].replace(".zip", ""),
                self.trading_path + "/" + self.moyr,
            ],
            [
                self.position_zip,
                self.position_zip.split("/")[-1].replace(".zip", ""),
                self.trading_path + "/" + self.moyr,
            ],
        ]

        for i in paths_list:
            with ZipFile(i[0], "r") as zip:
                zip.extract(i[1], i[2])

        self.csvcash = paths_list[0][2] + "/" + paths_list[0][1]
        self.position = paths_list[1][2] + "/" + paths_list[1][1]

    def archive_date_path(self, day=0):
        if day == 0:
            date_str = last_biz_day(self.year, self.month).strftime("%Y%m%d")
        else:
            date_str = datetime(self.year, self.month, day).strftime("%Y%m%d")

        dir_path = self.archive_path + "/" + date_str

        return dir_path

    def get_ABN_pdfs(self, f_pattern):
        dir_path = self.archive_date_path()

        files = os.listdir(dir_path)

        proper_files = list(filter(lambda x: re.search(f_pattern, x), files))

        return proper_files

    def get_account_file_mapping(self):

        dir_path = self.archive_date_path()

        f_pattern = r"[\w_\d]*([A-Z]{4})\_(\d{10})_DPR_SU.pdf"

        proper_files = self.get_ABN_pdfs(f_pattern)

        os.chdir(dir_path)

        account_file_mapping = {}

        count = 0

        for f in proper_files:
            count += 1
            pdf = pypdf.PdfReader(f)
            first_page = pdf.pages[0]

            account_name = get_account_name(first_page)

            search = re.search(f_pattern, f)
            account_type = search.group(1)
            file_map_i = re.search(f_pattern, f).group(2)

            print(
                f"{count}: {account_type} account {account_name} has file index {file_map_i}"
            )

            account_file_mapping.update(
                {account_name: [account_type, file_map_i]}
            )

        return account_file_mapping

    def get_abn_pdf_monthly_statement(
        self, account, account_file_mapping, day=None
    ):
        if day is None:
            dir_path = self.archive_date_path()
        else:
            dir_path = self.archive_date_path(day=day)

        f_pattern = rf"[\w_\d]*{account_file_mapping[account][0]}\_{account_file_mapping[account][1]}_DPR_SU.pdf"

        try:
            f_name = list(
                filter(
                    lambda f_name: re.search(f_pattern, f_name),
                    os.listdir(dir_path),
                )
            )[0]
        except:
            f_name = ""

        return (dir_path, f_name)
