import ctypes

from Cocoa import NSEvent, NSKeyDownMask, NSLog

ax = ctypes.cdll.LoadLibrary('/System/Library/Frameworks/ApplicationServices.framework/Versions/A/Frameworks/HIServices.framework/HIServices')

def ax_enabled():
    return ax.AXIsProcessTrusted()
