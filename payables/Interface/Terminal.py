import ctypes
from ctypes import wintypes
from typing import Any
import os

from CursorFunc import *

class PyTerminal:
    def __init__(self):
        os.system("cls")
        self.curs_x = 0
        self.curs_y = 0
        self._get_window_size()
    
    def _get_window_size(self):
        print("\x1b[999;999H", end='', flush=True)
        self._max_x, self._max_y = get_cursor_pos()
        print("\x1b[0;0H", end='', flush=True)
        
    @property
    def curs_x(self):
        return self._curs_x
    
    @curs_x.setter
    def curs_x(self, x_val: int):
        if isinstance(x_val, int):
            self._curs_x = x_val
        else:
            raise TypeError
    
    @property
    def curs_y(self):
        return self._curs_y
    
    @curs_y.setter
    def curs_y(self, y_val: int):
        if isinstance(y_val, int):
            self._curs_y = y_val
        else:
            raise TypeError
    
    def print(self, printable: Any) -> None:
        self.curs_x += len(printable)
        if self.curs_x > self._max_x:
            self.curs_x -= self._max_x
            self.curs_y += 1

        if "\n" in printable:
            self.curs_x = 0
            self.curs_y += 1
        
        if self.curs_y > self._max_y:
            self.curs_y = self._max_y

        print(printable, end='')

if __name__ == "__main__":
    term = PyTerminal()
    term.print("Hello world!\n")
    term.print(f"max_x: {term._max_x}\n")
    term.print(f"max_y: {term._max_y}")
