import os
from pynput.keyboard import Key, Listener
import sys
import time

def cursor_up():
    sys.stdout.write('\033[A')
    sys.stdout.flush()

def cursor_down():
    sys.stdout.write('\033[B')
    sys.stdout.flush()


def show_rewrite():
    print('Line 1!!')
    print('Line 2!!')
    print('Line 3!!')    

    cursor_up()
    cursor_up()

    time.sleep(5)

    text = input('Line 2!! :')

    time.sleep(5)

    cursor_down()

    print('Back to bottom!')

def on_press(key):
    if key == Key.up:
        cursor_up()
    elif key == Key.down:
        cursor_down()
    else:
        pass

def on_release(key):
    if key == Key.esc:
        return False

def test_menu():
    line1 = 'This Is the Menu Title!'
    line2 = ''
    line3 = 'this is a subtitle!'
    line4 = '\tinput1!'
    line5 = '\tinput2!'
    line6 = ''
    line7 = 'Submit!!'

    lines = [
            line1,
            line2,
            line3,
            line4,
            line5,
            line6,
            line7
            ]
    for i in lines:
        print(i)

        
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

test_menu()
