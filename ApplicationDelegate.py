import objc
objc.setVerbose(1)

from AppKit import NSEvent
from PyObjCTools import AppHelper
from Cocoa import NSObject, NSLog, NSUserNotificationCenter, \
    NSUserNotification, NSWorkspaceApplicationKey
from Cocoa import NSFunctionKeyMask, NSAlternateKeyMask, \
    NSControlKeyMask, NSCommandKeyMask
from Cocoa import NSWorkspace
from LauncherController import LauncherController
import chili

import sys
import traceback

import Quartz


class EventTapRunner(NSObject):
    """ a simple object that lets us use
    performSelectorOnMainThread_withObject_waitUntilDone_
    """
    def call_(self, args):
        callback = args[0]
        event = args[1]
        callback(event)


class EventTap(object):
    """ wraps a Quartz keyboard event tap """

    def __init__(self, cb, block_cb):
        self.runner = EventTapRunner.alloc().init()

        self.setup_event_tap(cb, block_cb)

    def setup_event_tap(self, callback, should_block):

        def keyboardTapCallback(proxy, type_, event, refcon):
            if type_ == Quartz.kCGEventTapDisabledByTimeout & 0xffffffff:
                # event tap timed out, re-enable.
                Quartz.CGEventTapEnable(self.tap, True)
                NSLog('event tap timed out, re-enabling')
                return None

            # Convert the Quartz CGEvent into something more useful
            keyEvent = NSEvent.eventWithCGEvent_(event)
            try:
                selector = objc.selector(self.runner.call_, signature='v@:@')
                self.runner.performSelectorOnMainThread_withObject_waitUntilDone_(
                    selector, (callback, keyEvent), False)

                if should_block(keyEvent):
                    return None
            except Exception, e:
                tb = sys.exc_info()
                print ''.join(traceback.format_exception(*tb))
                print 'Exception: ' + e.message

            return event

        self.tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown),
            keyboardTapCallback,
            None
        )

        runLoopSource = Quartz.CFMachPortCreateRunLoopSource(None, self.tap, 0)
        Quartz.CFRunLoopAddSource(
            Quartz.CFRunLoopGetCurrent(),
            runLoopSource,
            Quartz.kCFRunLoopDefaultMode
        )
        # Enable the tap
        Quartz.CGEventTapEnable(self.tap, True)

        Quartz.CFRunLoopRun()


class ApplicationDelegate(NSObject):

    def init(self):
        self = super(ApplicationDelegate, self).init()
        self.hotkeys = dict()
        self.key_hooks = list()
        self.register_hotkey('ctrl-alt- ', self.show_launcher)
        self.register_hotkey('fn-alt-q', self.quit)

        return self

    def applicationDidFinishLaunching_(self, _):
        NSLog("applicationDidFinishLaunching_")

        try:
            chili.load_user_settings()
        except Exception, e:
            self.alert_exception(e)

        # launcher window view controller
        self.ctrl = LauncherController.alloc().init()
        self.tap = EventTap(self.global_event, self.should_block_event)

        # regsiter for notifications on deactivated apps
        # this is useful for determining the app that was used
        # before the launcher window was popped up
        delegate = lambda notification: self.notification(notification)
        NSWorkspace.sharedWorkspace().notificationCenter() \
            .addObserverForName_object_queue_usingBlock_(
                'NSWorkspaceDidDeactivateApplicationNotification',
                None, None, delegate)

        chili.set_launcher(self.ctrl)

        n = NSUserNotification.alloc().init()
        n.setTitle_('Chili')
        n.setInformativeText_('Ready')
        NSUserNotificationCenter.defaultUserNotificationCenter() \
            .deliverNotification_(n)

    def notification(self, notification):
        app = notification.userInfo()[NSWorkspaceApplicationKey]
        self.ctrl.app_deactivated(app)

    def applicationWillTerminate_(self, sender):
        pass

    def register_hotkey(self, hotkey, callback):
        """ registers a callback function for given hotkey """
        split = hotkey.split('-')
        if len(split) < 2:
            return

        char = split[-1]
        mask = 0
        for modifier in split[:-1]:
            if modifier == 'alt':
                mask |= NSAlternateKeyMask
            elif modifier == 'ctrl':
                mask |= NSControlKeyMask
            elif modifier == 'cmd':
                mask |= NSCommandKeyMask
            elif modifier == 'fn':
                mask |= NSFunctionKeyMask

        self.hotkeys[(char, mask)] = callback

    def register_key_hook(self, callback):
        """ registers a global hook for key presses """
        self.key_hooks.append(callback)

    def should_block_event(self, event):
        """ tells the event tap wether to pass or block a keyboard event
        regardless of actual callback """
        char = event.charactersIgnoringModifiers()
        mask = event.modifierFlags() & (NSControlKeyMask |
            NSCommandKeyMask | NSAlternateKeyMask | NSFunctionKeyMask)

        return (char, mask) in self.hotkeys
        ctrl = event.modifierFlags() & NSControlKeyMask
        alt = event.modifierFlags() & NSAlternateKeyMask
        fn = event.modifierFlags() & NSFunctionKeyMask

        if ctrl and alt and char == ' ':
            return True

        if ctrl and fn and char == 'q':
            return True

    def global_event(self, event):
        """ process incoming keybaoard event """
        char = event.charactersIgnoringModifiers()
        mask = event.modifierFlags() & (NSControlKeyMask |
            NSCommandKeyMask | NSAlternateKeyMask | NSFunctionKeyMask)

        if (char, mask) in self.hotkeys:
            self.hotkeys[(char, mask)]()
            return True

        for hook in self.key_hooks:
            hook(char, mask)

        return False

    def show_launcher(self):
        """ toggle launcher window """
        self.ctrl.toggle()

    def quit(self):
        AppHelper.stopEventLoop()

    def alert_exception(self, exception):
        """ display an exception on notification center """
        n = NSUserNotification.alloc().init()
        n.setTitle_('Chili')
        n.setInformativeText_(str(exception))
        NSUserNotificationCenter.defaultUserNotificationCenter() \
            .deliverNotification_(n)

        tb = sys.exc_info()
        print ''.join(traceback.format_exception(*tb))
