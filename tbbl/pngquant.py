########################################
# pngquant.py
# call pngquant to compress PNG image
#
# Author zrong(zengrong.net)
# Creation 2015-04-29
########################################

import os
import subprocess
from zrong import (slog)
from zrong.base import get_files
from tbbl.base import (print_sep)

class PngquantBase(object):

    def __init__(self, gconf, gargs, parser=None):
        self.conf = gconf
        self.args = gargs
        self.parser = parser
        pqpath = None
        if self.conf.is_windows:
            pqpath = 'pngquant/win32/pngquant.exe'
        else:
            pqpath = 'pngquant/mac/pngquant'
        self.pq = self.conf.getBin(pqpath)
        self.file_size = self.args.size*1024

    def _get_param(self, inputfile, outputfile):
        quality = "%s-%s"%(self.args.min, self.args.max)
        speed = str(self.args.speed)
        return [self.pq, '--skip-if-larger', '--verbose', '--force',
                '--quality', quality,
                '--speed', speed,
                '--output', outputfile,
                inputfile]

    def _run_dir(self, dirname):
        dirpath = self.conf.getClientPath('res', dirname)
        files = get_files(dirpath, ['png'])
        filterfiles = []
        for f in files:
            if os.path.getsize(f) > self.file_size:
                filterfiles.append(f)
        for f in filterfiles:
            xargs = self._get_param(f, f)
            #slog.info(xargs)
            subprocess.call(xargs)

    def run(self):
        if self.args.dir == "*":
            for dirname in ('pdir', 'plst', 'ani', 'arm'):
                self._run_dir(dirname)
        else:
            self._run_dir(self.args.dir)

    def build(self):
        self.run()
        return False
