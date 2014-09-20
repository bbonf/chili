from ApplicationDelegate import ApplicationDelegate
from LauncherWindow import LauncherWindow
# asserts for ignoring unused imports
assert ApplicationDelegate
assert LauncherWindow

if __name__ == '__main__':
    from PyObjCTools import AppHelper
    AppHelper.runEventLoop()
