########################################
# update.py
#
# Author: zrong
# Creation: 2015-04-17
########################################

import os
import shutil
import subprocess
import tempfile
from zrong import (slog, git, ftp)
from tbbl.base import print_sep

class UpdateBase(object):

    def __init__(self, gconf, gargs, parser=None):
        self.conf = gconf
        self.args = gargs
        self.parser = parser

    def _downloadAndUnzip(self, fname, removedDirs, unzipDir):
        f = tempfile.NamedTemporaryFile(mode='wb', delete=False).name
        ftp_conf = self.conf.getFtpConf()
        ftp_conf['start_path'] = ftp_conf['lib_dir']
        ftp.download_file(fname, f, ftp_conf)

        for path in removedDirs:
            if os.path.exists(path):
                slog.info('Remove directory [%s]...'%path)
                shutil.rmtree(path)

        slog.info('Extract [%s] to [%s]'%(f, unzipDir))
        shutil.unpack_archive(f, unzipDir, 'zip')
        os.remove(f)
        slog.info('Remove tempfile [%s].'%f)

    def lua(self):
        print_sep('\nStart to update the lua framworks.', True, 40)
        src = self.conf.getClientPath('src')
        cocos = os.path.join(src, 'cocos')
        quick = os.path.join(src, 'quick')
        zrong = os.path.join(src, 'zrong')

        if os.path.islink(cocos) or \
            os.path.islink(quick) or \
            os.path.islink(zrong):
            slog.info('%s OR %s OR %s is a link. Remove a link is forbidden.'%(
                cocos, quick, zrong))
            return

        self._downloadAndUnzip(self.conf.lib_conf.lua, [cocos, quick, zrong], src)
        print_sep('Update lua framworks has done.', False, 40)

    def cpp(self):
        print_sep('\nStart to update the runtime-src directory.', True, 40)
        gitdir = self.conf.getDistPath('.git')
        if os.path.isdir(gitdir):
            slog.info('%s is a git repostory. Do nothing.'%gitdir)
            return
        runtimeDir = self.conf.getDistPath('runtime-src')
        self._downloadAndUnzip(self.conf.lib_conf.cpp, 
                [runtimeDir], 
                self.conf.getDistPath())
        print_sep('\nUpdate the runtime-src directory has done.', False, 40)

    def cocos(self):
        print_sep('\nStart to update the cocos2d-x framewroks.', True, 40)
        cocos2dx = self.conf.getDistPath('cocos2d-x')

        if os.path.islink(cocos2dx):
            slog.info('%s is a link. Do nothing.'%cocos2dx)
            return None
        if os.path.isdir(os.path.join(cocos2dx, '.git')):
            slog.info('%s is a git repostory. Do nothing.'%cocos2dx)
            return

        self._downloadAndUnzip(self.conf.lib_conf.cocos, 
                [cocos2dx], 
                self.conf.getDistPath())
        print_sep('Update the cocos2d-x frameworks has done.', False, 40)

    def _processAGit(self, gitConf):
        print_sep('\nStart to update the git repository [%s].'%gitConf.path, True, 40)
        exists = os.path.exists(gitConf.path)
        if exists:
            if self.args.force:
                gitArgs = git.get_args(gitConf.path, 'reset', '--hard')
                slog.info(' '.join(gitArgs))
                subprocess.call(gitArgs)
            gitArgs = git.get_args(gitConf.path, 'pull', 'origin', 'master')
            slog.info(' '.join(gitArgs))
            subprocess.call(gitArgs)
            print_sep('Update the git repository [%s] has done.'%gitConf.path, False, 40)
        else:
            slog.warning('%s is not exists!'%gitConf.path)

    def all(self):
        self.lua()
        self.cpp()
        self.cocos()
        for gitConf in self.conf.git_conf.values():
            self._processAGit(gitConf)

    def build(self):
        if self.args.all:
            self.all()
            return False

        noAnyArgs = True
        if self.args.cocos:
            self.cocos()
            noAnyArgs = False
        if self.args.lua:
            self.lua()
            noAnyArgs = False
        if self.args.cpp:
            self.cpp()
            noAnyArgs = False

        argsDict = vars(self.args)
        for git in self.conf.git_conf.keys():
            if argsDict[git]:
                self.processAGit(self.conf.git_conf[git])
                noAnyArgs = False
        return noAnyArgs

