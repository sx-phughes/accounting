debug_state = False

def dprint(obj: any) -> None:
    if debug_state:
        print(obj)

def switch_state() -> None:
    global debug_state
    debug_state = not debug_state