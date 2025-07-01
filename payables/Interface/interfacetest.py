import sys
from os import SEEK_SET

def parse_cursor_position(report: str) -> tuple[int, int]:
    print(report)
    row_col = [-1, -1]
    num = ''
    for i in report:
        print(i)
        if i >= '0' and i <= '9':
            ''.join([num, i])
        elif i == ';':
            row_col.append(int(num))
            num = ''
    
    return (row_col[0], row_col[1])
            

def main():
    while True:
        sys.stdout.write("\033[6n")
        sys.stdout.flush()
        sys.stdin.flush()
        sys.stdin.readline(10)
        # print(f"row {str(parsed[0])}; col {str(parsed[1])}")

main()