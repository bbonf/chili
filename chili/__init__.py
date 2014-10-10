import os
import glob

import chili.ui
from Cocoa import NSWorkspace, NSURL

# this shouldn't be module-level
CHILI_CMDS = dict()
CHILI_LAUNCHER = None


def register_command(cmd, func):
    global CHILI_CMDS
    CHILI_CMDS[cmd] = func


def find_loose(haystack, needle):
    """ an attempt at fuzzy lookup. should be rewritten """
    position = 0
    distance = 0
    for char in needle:
        next_position = haystack.find(char, position)
        if next_position < 0:
            return False

        distance += next_position - position
        position = next_position

    return distance


def get_commands(prefix=''):
    """ command lookup. should be rewritten """
    loose = [cmd for cmd in CHILI_CMDS.iteritems() if find_loose(cmd[0].lower(),prefix.lower())]
    return sorted(loose, key=lambda cmd: find_loose(cmd[0].lower(),prefix.lower()))

    """ earlier version:
    ends = [cmd for cmd in CHILI_CMDS.iteritems() if cmd[0].lower().endswith(prefix.lower())]
    starts = [cmd for cmd in CHILI_CMDS.iteritems() if cmd[0].lower().startswith(prefix.lower())]
    contains = [cmd for cmd in CHILI_CMDS.iteritems() if prefix.lower() in cmd[0].lower()]

    result = sorted(ends, key=lambda x:x[0].lower())
    result += [cmd for cmd in starts if cmd not in sorted(result, key=lambda x:x[0].lower())]
    result += [cmd for cmd in contains if cmd not in sorted(result, key=lambda x:x[0].lower())]

    return result
    """


def get_command(cmd):
    """ get specific command or find best match """
    if cmd in CHILI_CMDS:
        return CHILI_CMDS[cmd]

    cmds = get_commands(prefix=cmd)
    if len(cmds) > 0:
        return cmds[0][1]

    return None


def command(cmd):
    """ command decorator. function takes a single argument that is given on the command text box """
    def decorator(func):
        def delegate(arg=None):
            func(arg)

        register_command(cmd, func)
        return delegate
    return decorator


def set_launcher(launcher):
    global CHILI_LAUNCHER
    CHILI_LAUNCHER = launcher


def close(reactivate=True):
    if reactivate:
        CHILI_LAUNCHER.unpop()
    else:
        CHILI_LAUNCHER.close()


def input(text):
    CHILI_LAUNCHER.set_input(text)


def launch(app):
    workspace = NSWorkspace.sharedWorkspace()
    workspace.launchApplication_(app)


def open(file):
    workspace = NSWorkspace.sharedWorkspace()
    workspace.openFile_(file)


def open_with(file, app):
    workspace = NSWorkspace.sharedWorkspace()
    workspace.openFile_withApplication_(file, app)


def open_url(url):
    workspace = NSWorkspace.sharedWorkspace()
    workspace.openURL_(NSURL.URLWithString_(url))


@command('reload')
def load_user_settings(_=None):
    glbls = dict(command=command)

    configs = glob.glob(os.path.expanduser('~/.chili/*.py'))
    if len(configs) < 1:
        chili.ui.prompt("Couldn't find any config files in: %s" % os.path.expanduser('~/.chili/'))

    for f in configs:
        execfile(f, glbls)


@command('quit')
def quit(_=None):
    from PyObjCTools import AppHelper
    AppHelper.stopEventLoop()


def add_launchers(pattern):
    for app in glob.glob(pattern):
        def launch(arg):
            def delegate(_):
                open(arg)
                close(reactivate=False)

            return delegate

        name = os.path.basename(app).split('.')[0]
        register_command(name, launch(app))

add_launchers('/Applications/*.app')
add_launchers('/Applications/Utilities/*.app')
add_launchers('/System/Library/PreferencePanes/*.prefPane')
