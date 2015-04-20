########################################
# templ.py
# Convert template files with templ.sub.[name].py
#
# Author zrong(zengrong.net)
# Creation 2015-04-20
########################################

import os
from zrong import slog, git
from tbbl.base import (write_by_jinja, print_sep)

class TemplBase(object):

    def __init__(self, gconf, gargs, parser=None):
        self.conf = gconf
        self.args = gargs
        self.parser = parser

    def _initTempls(self):
        if hasattr(self, "subs") and hasattr(self, "templs"):
            return
        files = os.listdir(self.conf.getPath('templ'))
        self.subs = []
        self.templs = []
        for afile in files:
            if afile.startswith('templ.sub.'):
                self.subs.append(afile)
            else:
                self.templs.append(afile)

    def runapp(self):
        print_sep('\nStart to generate runapp.', True, 40)
        if conf.is_windows:
            templ = 'runapp.bat'
        else:
            templ = 'runapp.sh'
        confpath = conf.getClientPath(templ)
        write_by_templ(conf.getStringTempl(templ),
                confpath,
                {'CLIENT_PATH':conf.getClientPath()},
                safe=True)
        print_sep('[%s] has generated.'%confpath, False, 40)

    def build(self):
        noAnyArgs = True
        if self.args.runapp:
            self.runapp()
            noAnyArgs = False

        return noAnyArgs
