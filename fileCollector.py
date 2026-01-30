import shutil
import os
import re

src1 = "C:/gdrive/Shared drives/accounting/Simplex Trading/"
src2 = "2025"
src3 = "BOFA"
src = "/".join([src1, src2, src3])

file_pattern = "GL_Detail_Table.csv"

dest1 = "C:/gdrive/Shared drives/accounting/Simplex Trading/Audit/2025"
dest2 = "Dividends and Interest"
dest = "/".join([dest1, dest2])

for folder in os.listdir(src):
    month_folder = "/".join([src, folder])
    files = os.listdir(month_folder)
    for file in files:
        ext = file.split(".")[-1]
        new_fname = file + "_" + folder + "." + ext
        if re.match(file_pattern, file):
            shutil.copy(
                src="/".join([month_folder, file]),
                dst="/".join([dest, new_fname]),
            )
