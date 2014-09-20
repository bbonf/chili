from Quartz import *
from keycode import keyCodeForChar
from Cocoa import NSApplication

# limited support for simulating key strokes using code from https://github.com/abarnert/pykeycode
def type_string(string):
    codes = map(keyCodeForChar, string)
    send_keys(codes)

def send_keys(keys):
    events = []
    source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
    for key, shift in keys:
        event = CGEventCreateKeyboardEvent(source, key, True)
        if shift:
            CGEventSetFlags(event, kCGEventFlagMaskShift | CGEventGetFlags(event))
        events.append(event)

        event = CGEventCreateKeyboardEvent(source, key, False)
        if shift:
            CGEventSetFlags(event, kCGEventFlagMaskShift | CGEventGetFlags(event))
        events.append(event)

    map(lambda e: CGEventPost(kCGAnnotatedSessionEventTap, e), events)

def hotkey(key):
    """ hotkey decorator, currently supports only printable keys and modifiers defined
    as 'modifier-key' e.g. 'ctrl-cmd-k' or 'fn-w'.
    callback function takes no arguments """
    def decorator(func):
        NSApplication.sharedApplication().delegate().register_hotkey(key, func)
        return func

    return decorator
