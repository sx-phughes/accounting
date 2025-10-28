from functions import *
from CursorFunc import *
import os

os.system("cls")

fields = ["Vendor", "Invoice Number", "Amount" "Credit Card", "CC User"]

input_length = 25

unformatted_lines = []
for field in fields:
    line = field + "\t" + (" " * input_length)
    unformatted_lines.append(line)

ascii_lines = get_ascii_table_lines(*unformatted_lines, total_line=False)
start_col = ascii_lines[0].find("|", 2) + 2
start_line = 1

print(*ascii_lines, sep="\n")
move_cursor(row=start_line, col=start_col)

input()
