import curses
from vendor_interface import run

def test(stdscr: curses.window):
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    for i in range(10):
        stdscr.addstr(str(i))
        stdscr.addstr("\n")
    
    while True:
        key = stdscr.getkey()
        if key == "Q":
            break
        else:
            stdscr.addstr(key)
    
    curses.echo()
    curses.nocbreak()
    stdscr.keypad(False)
    curses.endwin()
    
curses.wrapper(run())