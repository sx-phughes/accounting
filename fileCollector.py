import shutil
import os
import re

src1 = "C:/gdrive/Shared drives/Clearing Archive/ABN_Archive"
# src2 = "2025"
# src3 = "ABN"
# src = "/".join([src1, src2, src3])
src = src1

file_pattern = "-2518-C2518-CSVCASH_AC.csv.zip"

dest1 = "C:/gdrive/Shared drives/accounting/Tax/2025/Mixed Straddle 2025"
dest2 = "ABN Files"
dest = "/".join([dest1, dest2])

folders = os.listdir(src)
filtered_folders = list(filter(lambda x: re.match(r"2025\d{4}", x), folders))

for folder in filtered_folders:
    file = "".join([folder, file_pattern])
    try:
        from_path = "/".join([src, folder, file])
        to_path = "/".join([dest, file])
        # print(from_path, to_path)
        shutil.copy(src=from_path, dst=to_path)
    except FileNotFoundError:
        print(f"file {file} not found")
        continue

    # month_folder = "/".join([src, folder])
    # files = os.listdir(month_folder)
    # for file in files:
    #     ext = file.split(".")[-1]
    #     new_fname = file + "_" + folder + "." + ext
    #     if re.match(file_pattern, file):
    #         shutil.copy(
    #             src="/".join([month_folder, file]),
    #             dst="/".join([dest, new_fname]),
    #         )
