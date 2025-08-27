# Standard imports
import numpy as np
import re
import sys
import os
from typing import Any

def cursor_up():
    sys.stdout.flush()
    # undo \n from entering input
    print("\033[A", end='', flush=True)
    # move up a line and to beginning
    print("\033[1F", end='', flush=True)
    # clear line
    # print("\033[2K", end='', flush=True)

def cursor_down():
    sys.stdout.flush()
    sys.stdout.flush()


def cls():
    os.system("cls")

def check_date(date: str):
    """Check that date matches YYYY-MM-DD format"""
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})', date)
    
    if match:
        if int(match.group(1)) in range(2020, 2040) and \
            int(match.group(2)) in range(1,13) and \
            int(match.group(3)) in range(1, 32):
            return True
    return False

def set_type(obj: Any, dest_type: str) -> Any:
    if dest_type == "str":
        return str(obj)
    elif dest_type == "int":
        return int(obj)
    elif dest_type == "float":
        return float(obj)
    elif dest_type == "float64":
        return np.float64(obj)
    elif dest_type == "bool":
        return bool(obj)
    else:
        raise TypeError(f"Unprogrammed type: {dest_type}")

def debug(text: str) -> None:
    with open("debug.log", "+a") as file:
        file.write(text)