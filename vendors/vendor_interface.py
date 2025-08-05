import pandas as pd
import re
import sys
import curses

# import vendors.vendors_fns
options = ["View vendor table", "Search for vendor"]
pd.set_option("display.max_rows", None)

def init_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    return stdscr


def close_curses(stdscr: curses.window):
    curses.echo()
    curses.nocbreak()
    stdscr.keypad(False)
    curses.endwin()


def get_option_selection(stdscr: curses.window) -> int:
    selection = None
    while not selection:
        stdscr.addstr("\nInput number of option:")

        try:
            selection = input(">\t")
            selection = validate_input(selection)
            break
        except TypeError as e:
            stdscr.addstr(e)
            stdscr.addstr("Input must be a number of above option")
            input()
            print_escape_code("\x1b[1A\x1b[2K" * 4)
            selection = None

    return selection


def print_escape_code(*code: str) -> None:
    print(*code, sep="", end="", flush=True)


def validate_input(input: str) -> int:
    if re.match(r"\d", input):
        return int(input)
    else:
        raise TypeError


def view_vendor_table(t: pd.DataFrame) -> None:
    pass


def search_for_vendor():
    pass

functions = [view_vendor_table, search_for_vendor]

def main_menu(stdscr: curses.window) -> None:
    stdscr.addstr("entering main loop\n")
    while True:
        for i in range(len(options)):
            num = i + 1
            formatted = "%d. %s" % (num, options[i])
            stdscr.addstr(formatted)

        selection = get_option_selection(stdscr)
        selection -= 1
        if selection == len(options):
            break
        else:
            functions[selection]()

def run():
    stdscr = init_curses()
    main_menu(stdscr)
    close_curses(stdscr)