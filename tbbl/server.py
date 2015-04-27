########################################
# server.py
#
# Author zrong(zengrong.net)
# Creation 2015-04-20
########################################

import os
from zrong import git, slog
from tbbl.base import print_sep

class ServerBase(object):

    def __init__(self, gconf, gargs, parser=None):
        self.conf = gconf
        self.args = gargs
        self.parser = parser
        self.servers = ['redis', 'gate', 'game', 'fight']

    def _check_servername(self, typ):
        for sname in typ:
            if sname not in self.servers:
                slog.error('不支持的服务器类型： %s'%sname)
                return None
            if sname == 'redis':
                return ['redis']
        return typ

    def _check_branch(self, reponame):
        repopath = self.conf.getGit(reponame, 'path')
        if not os.path.exists(repopath):
            slog.error('Please initialize "{0}" repostory first! '
                    'You can type "hhlb init --{0}" to do it.'.format(reponame))
            return None, None
        if not git.isclean(repopath):
            slog.error('Your git repostory [%s] is not clean! '
                    'Please commit it first.'%repopath)
            return None, None
        branches = git.get_branches(repopath)
        curbr = branches[0]
        if not curbr:
            slog.error('Get branches error!')
            return None, None
        if curbr != self.conf.user_conf.name:
            slog.error('Your git branch is [%s], but your name is [%s], '
                    'Please correct it.'%(curbr, self.conf.user_conf.name))
            return None, None
        return repopath, curbr

    def _commit_empty(self, reponame, msg):
        repopath, curbr = self._check_branch(reponame)
        if not repopath or not curbr:
            return False
        code, output = git.call(repopath, 'commit', '--allow-empty', '-m', msg)
        if code > 0:
            slog.error(output)
            return
        code, output = git.call(repopath, 'push', 'origin', curbr)
        if code > 0:
            slog.error(output)
            return False
        slog.info(output)
        return True

    def _merge(self, reponame):
        repopath, curbr = self._check_branch(reponame)
        if not repopath or not curbr:
            return
        code, output = git.call(repopath, 'fetch')
        if code > 0:
            slog.error(output)
            return
        code, output = git.call(repopath, 'merge', 'master')
        if code > 0:
            slog.error(output)
            return
        slog.info(output)

    def _send_signal(self, signal, typ, repo):
        print_sep('\nSend signal [%s] to server [%s].'%(signal, ' '.join(typ)), True, 40)
        reponame = 'serverctrl'
        if self.args.merge_master:
            self._merge(reponame)
        typ = self._check_servername(typ)
        if not typ:
            return
        if 'redis' in typ:
            msg = 'REDIS '+signal
        else:
            msg = 'SERVER %s,%s'%(repo, ' '.join(typ))
        if self._commit_empty(reponame, msg):
            print_sep('Send signal is successful.', False, 40)

    def _update_server(self, update):
        reponame = self.args.type+'server'
        if self.args.merge_master:
            self._merge(reponame)
        msg = 'UP'
        if len(update) > 0:
            msg = '%s %s'%(msg, update[0])
        self._commit_empty(reponame, msg)

    def build(self):
        noAnyArgs = True

        if args.update != None and self.args.type != 'redis':
            self._update_server(self.args.update)
            noAnyArgs = False
        if args.signal:
            self._send_signal(self.args.signal)
            noAnyArgs = False

        return noAnyArgs

