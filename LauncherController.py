from Cocoa import NSApp, NSWindowController, \
    NSApplication, NSApplicationActivateIgnoringOtherApps


class LauncherController(NSWindowController):

    def init(self):
        self = super(LauncherController, self) \
            .initWithWindowNibName_("LauncherWindow")

        self.last_app = None
        return self

    def unpop(self):
        """ hides launcher window and returns to last used app """
        if self.last_app:
            self.last_app.activateWithOptions_(
                NSApplicationActivateIgnoringOtherApps)

        self.close()

    def toggle(self):
        NSApp.activateIgnoringOtherApps_(True)

        window = self.window()
        if window.isMainWindow():
            self.unpop()

        else:
            self.showWindow_(self)
            self.set_input('')

    def app_deactivated(self, app):
        """ remember last used app """
        self.last_app = app

    def set_input(self, text):
        self.window().textField.setStringValue_(text)
        self.window().textField.selectText_(self)
        self.window().textField.currentEditor().moveToBeginningOfLine_(self)

    def report_exception(self, e):
        NSApplication.sharedApplication().delegate().alert_exception(e)
