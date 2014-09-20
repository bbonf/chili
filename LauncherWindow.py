from Cocoa import NSWindow
from objc import IBOutlet, IBAction
from Foundation import NSLog

import chili
import objc
import re


class LauncherWindow(NSWindow):
    # command list, currently implemented as a simple multilned label
    label = IBOutlet()

    # command text field
    textField = IBOutlet()

    # regex for arithmetic expressions
    calc_re = re.compile(r'[\d\(\)\.\+\-\*/\s]{2}[\d\(\)\.\+\-\*/\s]')

    def awakeFromNib(self):
        NSLog('awakeFromNib')
        self.selected_cmd = None

    def controlTextDidChange_(self, notification):
        text = self.textField.stringValue()

        # try to eval arithmetic expressions or lookup commands otherwise
        if self.calc_re.match(text):
            try:
                self.label.setStringValue_(eval(text))
            except:
                pass

        else:
            self.update_commands_list(prefix=text.split(' ')[0])

    @IBAction
    def onEnter_(self, sender):
        # command was selected from the commands list
        if self.selected_cmd:
            cmd = self.selected_cmd[1]
            arg = self.textField.stringValue()[len(self.selected_cmd[0]):]

            self.selected_cmd = None

        # command is selected from text field
        else:
            if not self.textField.stringValue():
                return

            split = self.textField.stringValue().split(' ', 1)

            cmd = chili.get_command(split[0])
            arg = split[1] if len(split) > 1 else None

        if cmd:
            # run command
            self.performSelectorInBackground_withObject_(
                objc.selector(self.runCmd_, signature='v@:@'), (cmd, arg))

    def runCmd_(self, cmdArg):
        try:
            # call command function
            cmdArg[0](cmdArg[1])
        except Exception, e:
            self.windowController().report_exception(e)

    def cancel_(self, sender):
        self.windowController().unpop()

    def update_commands_list(self, prefix=''):
        """ fill commands list with commands that match prefix.
        Prefix is not really used to lookup prefixes, and the whole lookup
        algorithm should be reworked """
        self.cmds = chili.get_commands(prefix=prefix)
        self.cmd_idx = -1

        self.label.setStringValue_('\n'.join(map(lambda x: x[0], self.cmds)))

    def control_textView_doCommandBySelector_(self, ctrl, _, selector):
        """ handle up/down key events for selecting commands """
        if selector == 'moveUp:':
            if self.cmd_idx > 0:
                self.cmd_idx -= 1
                self.selected_cmd = self.cmds[self.cmd_idx]
                self.textField.setStringValue_(self.cmds[self.cmd_idx][0])

            return True

        elif selector == 'moveDown:':
            if self.cmd_idx < len(self.cmds) - 1:
                self.cmd_idx += 1
                self.selected_cmd = self.cmds[self.cmd_idx]
                self.textField.setStringValue_(self.cmds[self.cmd_idx][0])
            return True

        return False
