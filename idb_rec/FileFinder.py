import os, re
from datetime import datetime

class FileFinder:
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.yrmo = datetime(year, month, 1).strftime('%Y%m')
        self.search_dir = 'C:/gdrive/Shared drives/accounting/payables'