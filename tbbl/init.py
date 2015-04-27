########################################
# init.py
#
# Author: zrong
# Creation: 2015-04-17
########################################

import os
import shutil
from tbbl import config
from zrong.base import slog
from zrong import git

class InitBase(object):

    def __init__(self, gconf, gargs, parser=None):
        self.conf = gconf
        self.args = gargs
        self.parser = parser

    def callUpdate(self, updateArgv):
        pass

    def cloneAGit(self, gitConf, includeUpdate=True):
        exists = os.path.exists(gitConf.path)
        if self.args.force and exists:
            slog.info('Removing git repostory "%s"'%gitConf.path)
            shutil.rmtree(gitConf.path)
            exists = False

        if exists:
            if includeUpdate:
                updateArgv = ['update', '--'+gitConf.name]
                if args.force:
                    updateArgv.append('-f')
                updateArgs, parser = config.checkArgs(conf, updateArgv)
                update.build(conf, updateArgs, parser)
        else:
            git.clone(gitConf.git, gitConf.path)

    def all(self):
        for gitConf in self.conf.git_conf.values():
            self.cloneAGit(gitConf, False)

    def build(self):
        if self.args.all:
            self.all()
            self.callUpdate(['update', '-a'])
            return False

        noAnyArgs = True
        argsDict = vars(self.args)
        for git in self.conf.git_conf.keys():
            if argsDict[git]:
                self.cloneAGit(conf.git_conf[git])
                noAnyArgs = False

        return noAnyArgs

