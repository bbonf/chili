from Cocoa import *
import objc

class ChiliAlert(NSObject):
    def initWithAlert_(self, alert):
        self = super(ChiliAlert, self).init()
        if self is None:
            return None

        self.alert = alert
        return self

    @staticmethod
    def make(title, default, alt, other, text):
        args = [title, default, alt, other, text]

        alert = NSAlert.alertWithMessageText_defaultButton_alternateButton_otherButton_informativeTextWithFormat_(*args)
        return ChiliAlert.alloc().initWithAlert_(alert)

    def runModal(self):
        ret = self.alert.runModal()
        self.performSelectorInBackground_withObject_('handleResponse',ret)

    def show(self, default_cb=None, alt_cb=None, other_cb=None):
        self.performSelectorOnMainThread_withObject_waitUntilDone_('runModal',None,False)
        self.cbs = dict(default=default_cb, alt=alt_cb, other=other_cb)

    def handleResponse(self, retcode):
        if retcode == NSAlertDefaultReturn:
            if self.cbs['default']:
                self.cbs['default']()

        elif retcode == NSAlertOtherReturn:
            if self.cbs['other']:
                self.cbs['other']()

        elif retcode == NSAlertAlternateReturn:
            if self.cbs['alt']:
                self.cbs['alt']()

def prompt(text, **kwargs):
    ChiliAlert.make(kwargs.get('title','Chili'), kwargs.get('default'),
        kwargs.get('alt'), kwargs.get('other'), text).show(kwargs.get('default_cb'),
        kwargs.get('alt_cb'), kwargs.get('other_cb'))


class ChiliStatusItem(object):
    def __init__(self, text):
        status_bar = NSStatusBar.systemStatusBar()
        self.status_item = status_bar.statusItemWithLength_(NSVariableStatusItemLength)
        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self.img = NSImage.alloc().initWithSize_(NSSize(50,22))
        self.img.lockFocus()
        s = NSString.stringWithString_(text)
        s.drawInRect_withAttributes_(NSRect(NSPoint(0,10),NSSize(50,12)), None)
        self.img.unlockFocus()

        self.status_item.setImage_(self.img)

def status_item_make(text):
    return ChiliStatusItem(text)
