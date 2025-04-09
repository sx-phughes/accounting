# import os
# from pynput.keyboard import Key, Listener
import sys
# import time

def cursor_up():
    sys.stdout.flush()
    sys.stdout.write('\033[A')
    sys.stdout.write('\033[A')
    sys.stdout.flush()

def cursor_down():
    sys.stdout.flush()
    # sys.stdout.write('\033[B')
    sys.stdout.flush()


# def show_rewrite():
#     print('Line 1!!')
#     print('Line 2!!')
#     print('Line 3!!')    
# 
#     cursor_up()
#     cursor_up()
# 
#     time.sleep(5)
# 
#     text = input('Line 2!! :')
# 
#     time.sleep(5)
# 
#     cursor_down()
# 
#     print('Back to bottom!')
# 
# class GuiMenu:
#     def __init__(self, menu_name: str, lines: list[str], bool_vals:
#                  list[bool]):
# 
#     def on_press(key):
#         if key == Key.up:
#             if curr_line > 0:
#                 cursor_up()
#                 curr_line -= 1
#             else:
#                 pass
#         elif key == Key.down:
#             if curr_line < max_line:
#                 cursor_down()
#                 curr_line += 1
#             else:
#                 pass 
#         else:
#             pass
#     def on_release(key):
#         if feed[curr_line][1]:
#             input_dict[feed[curr_line][0]] = input(f'\r{feed[curr_line][0]')
#         if key == Key.esc:
#             return False
# 
#     def test_menu():
#         line1 = 'Enter Invoice'
#         line2 = ''
#         line3 = 'Vendor: ' 
#         line4 = 'Invoice Number: ' 
#         line5 = 'Amount: ' 
#         line6 = ''
#         line7 = 'Enter Invoice' 
# 
#         lines = [
# 
# def on_press(key):
#     if key == Key.up:
#         cursor_up()
#     elif key == Key.down:
#         cursor_down()
#     else:
#         pass
# 
# def on_release(key):
#     if key == Key.esc:
#         return False
# 
# def test_menu():
#     line1 = 'This Is the Menu Title!'
#     line2 = ''
#     line3 = 'this is a subtitle!'
#     line4 = '\tinput1!'
#     line5 = '\tinput2!'
#     line6 = ''
#     line7 = 'Submit!!'
# 
#     lines = [
#             line1,
#             line2,
#             line3,
#             line4,
#             line5,
#             line6,
#             line7
#         ]
# 
#         inputs = [
#             False,
#             False,
#             True,
#             True,
#             True,
#             False,
#             True
#         ]
# 
#         feed = [[line, input_bool] for line, input_bool in zip(lines, inputs)]
# 
#         global curr_line = len(feed) - 1
#         global max_line = len(feed) - 1
# 
#         with Listener(on_press=on_press, on_release=on_release) as listener:
#             listener.join()
#             ]
#     for i in lines:
#         print(i)
# 
#         
#     with Listener(on_press=on_press, on_release=on_release) as listener:
#         listener.join()
