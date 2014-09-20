import ctypes
from Cocoa import NSAccessibilityPositionAttribute, NSAccessibilityFocusedWindowAttribute
from Cocoa import NSAccessibilitySizeAttribute
from Cocoa import NSScreen

cf = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
ax = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/HIServices.framework/HIServices')

cf.CFStringCreateWithCString.restype = ctypes.c_void_p

ax.AXUIElementCopyAttributeValue.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
ax.AXUIElementCreateSystemWide.restype = ctypes.c_void_p
ax.AXUIElementSetAttributeValue.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
ax.AXValueCreate.restype = ctypes.c_void_p

kAXValueCGPointType = 1
kAXValueCGSizeType = 2

AXFullScreen = 'AXFullScreen'

def CFSTR(s):
    global cf, ctypes
    return cf.CFStringCreateWithCString(None, ctypes.c_char_p(s), 0x8000100)

class MyNSPoint(ctypes.Structure):
    _fields_ = [('x', ctypes.c_double), ('y', ctypes.c_double)]

class MyNSSize(ctypes.Structure):
    _fields_ = [('w', ctypes.c_double), ('h', ctypes.c_double)]

def get_focused_window():
    e = ctypes.c_void_p(ax.AXUIElementCreateSystemWide())

    focused_app = ctypes.c_void_p()
    ax.AXUIElementCopyAttributeValue(e, CFSTR('AXFocusedApplication'), ctypes.byref(focused_app))
    focused_win = ctypes.c_void_p()
    ax.AXUIElementCopyAttributeValue(focused_app, CFSTR(NSAccessibilityFocusedWindowAttribute), ctypes.byref(focused_win))

    return focused_win


def get_window_pos(window):
    point = MyNSPoint(0, 0)
    _point = ctypes.c_void_p()
    ax.AXUIElementCopyAttributeValue(window, CFSTR(NSAccessibilityPositionAttribute), ctypes.byref(_point))
    ax.AXValueGetValue(_point, kAXValueCGPointType, ctypes.byref(point))

    return point


def set_window_pos(window, x, y):
    point = MyNSPoint(x, y)
    _point = ctypes.c_void_p(ax.AXValueCreate(kAXValueCGPointType, ctypes.byref(point)))
    ax.AXUIElementSetAttributeValue(window, CFSTR(NSAccessibilityPositionAttribute), _point)


def get_window_size(window):
    size = MyNSSize(0, 0)
    _size = ctypes.c_void_p()
    ax.AXUIElementCopyAttributeValue(window, CFSTR(NSAccessibilitySizeAttribute), ctypes.byref(_size))
    ax.AXValueGetValue(_size, kAXValueCGSizeType, ctypes.byref(size))

    return size


def set_window_size(window, w, h):
    size = MyNSSize(w, h)
    _size = ctypes.c_void_p(ax.AXValueCreate(kAXValueCGSizeType, ctypes.byref(size)))
    ax.AXUIElementSetAttributeValue(window, CFSTR(NSAccessibilitySizeAttribute), _size)

def set_window_fullscreen(window):
    ax.AXUIElementSetAttributeValue(window, CFSTR(AXFullScreen), cf.kCFBooleanTrue)

def get_window_screen(window):
    pos = get_window_pos(window)
    screens = NSScreen.screens()

    for screen in screens:
        frame = screen.frame()
        if pos.x >= frame.origin.x and \
            pos.y >= frame.origin.y and \
            pos.x <= frame.origin.x + frame.size.width and \
            pos.y <= frame.origin.y + frame.size.height:

            return screen

    # screen not found
    return NSScreen.mainScreen()
