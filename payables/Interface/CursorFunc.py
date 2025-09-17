import ctypes
from ctypes import wintypes
import re
import sys

def cursor_up():
    """Moves the cursor up one row after input."""
    sys.stdout.flush()
    # clear line nav'ed from
    clear_end_of_line_after_input("")
    # undo \n from entering input
    print("\033[A", end='', flush=True)
    # move up a line and to beginning
    print("\033[1F", end='', flush=True)

def cursor_down():
    """Moves the cursor down one row after input."""
    clear_end_of_line_after_input()
    return

def print_sugg_value(value: str) -> None:
    """Reprint a string to a line and moves cursor to beginning of string."""

    input_len = len(str(value))
    print(value, end='', flush=True)
    # Erase from cursor to end of line
    print("\033[0K", end='', flush=True)
    # Move cursor to beginning of the response
    print(f"\033[{input_len}D", end='', flush=True)

def clear_end_of_line_after_input(value: str) -> None:
    """After inputting a value, clears line to end of screen. Returns cursor
    to beginning of next line."""

    data_len = len(value)
    print("\033[A", end='', flush=True)
    print(f"\033[{20+data_len}C", end='', flush=True)
    print("\033[0K", end='', flush=True)
    print(f"\033[E", end='', flush=True)

def get_cursor_pos() -> tuple[int, int]:
    """Returns the cursor position in the terminal."""

    old_stdin_mode = wintypes.DWORD()
    old_stdout_mode = wintypes.DWORD()
    kernel32 = ctypes.windll.kernel32
    kernel32.GetConsoleMode(
        kernel32.GetStdHandle(-10), ctypes.byref(old_stdin_mode)
    )
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-10),0)
    kernel32.GetConsoleMode(
        kernel32.GetStdHandle(-11), ctypes.byref(old_stdout_mode)
    )
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    
    try:
        buff = ""
        sys.stdout.write("\x1b[6n")
        sys.stdout.flush()
        while True:
            buff += sys.stdin.read(1)
            if buff[-1] == "R":
                break
    finally:
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), old_stdin_mode)
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), old_stdout_mode)
    
    res = re.match(r"\x1b\[(?P<y>\d*);(?P<x>\d*)R", buff)
    if res:
        y = res.group("y")
        x = res.group("x")
        return (int(x), int(y))

def better_input(prompt: str) -> str:
    """Input that undoes the automatic enter after submitting the value."""

    ret = input(prompt)
    ret_len = len(ret)
    