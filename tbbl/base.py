import os
import platform
import shutil
import tempfile
from pkg_resources import (resource_filename, resource_string)
from jinja2 import Template
from zrong import slog
from zrong.base import (DictBase,write_by_templ,read_file,write_file)

class ConfBase(DictBase):

    def init(self, workDir, confFile):
        subdict = self.getOriginal(workDir, confFile)
        write_by_templ(self.getTplFile(), confFile, subdict)
        self.read_from_file(confFile)

    # tplFile is a config file template.
    def getTplFile(self):
        return None

    # Must override the method and return a dict with config data.
    def getOriginal(self, workDir, confFile):
        return {}

    def updateConf(self, aconf):
        # Save a temp conf file, read its conf_version, compare them.
        subdict = self.getOriginal(aconf.getPath('work'), aconf.conf_file)
        tmpfile = tempfile.NamedTemporaryFile(mode='wb', delete=False)
        write_by_templ(self.getTplFile(), tmpfile.name, subdict)
        tmpconf = self.getTmpConf()
        tmpconf.read_from_file(tmpfile.name)
        slog.info('The config version: (OLD=%d, NEW=%d)', 
                aconf.conf_ver if aconf.conf_ver else -1, 
                tmpconf.conf_ver)
        if aconf.conf_ver and aconf.conf_ver >= tmpconf.conf_ver:
            tmpfile.close()
            os.remove(tmpfile.name)
            self.copy_from_dict(aconf)
            return
        # Update python2 and tp's path
        tmpconf.exe_conf.python2 = aconf.exe_conf.python2
        tmpconf.exe_conf.tp = aconf.exe_conf.tp
        tmpconf.user_conf.name = aconf.user_conf.name
        self.copy_from_dict(tmpconf)
        tmpfile.close()
        os.remove(tmpfile.name)
        self.save_to_file()
        slog.info('Update conffile done.')
        
    def save_to_file(self):
        super(ConfBase, self).save_to_file(self.conf_file)

    def getPath(self, name, *path):
        adir = self.dir_conf[name] if name in self.dir_conf else name
        if path:
            return absPath(adir, *path)
        return adir

    def getClientPath(self, *path):
        clientDir = self.getGit('client', 'path')
        if path:
            return self.getPath(clientDir, *path)
        return clientDir

    def getDistPath(self, *path):
        return self.getPath('distribution', *path)

    def getExe(self, name, checkExistence=False):
        exe = self.exe_conf[name]
        if checkExistence and exe:
            # Gettext is special.
            if name == 'gettext':
                if self.is_windows:
                    return os.path.isdir(exe)
                return 'gettext'
            else:
                if not shutil.which(exe, mode=os.X_OK|os.F_OK):
                    return None
        return exe

    def getGit(self, name, key=None):
        git = self.git_conf.get(name)
        if git and key:
            return git.get(key)
        return git

    def getPHP(self):
        return self.getBin('quick/win32/php.exe') if self.is_windows else 'php'

    def getBin(self, path):
        return resource_filename('tbbl', 'bin/'+path)

    def getJinjaTempl(self, name):
        return self.getTemplFile(name, 'templ.jinja.%s')

    def getStringTempl(self, name):
        return self.getTemplFile(name, 'templ.string.%s')

    def getTemplFile(self, name, pattern='templ.%s'):
        if pattern:
            name = pattern%name
        templ = self.getPath('templ', name)
        if not os.path.exists(templ):
            raise TEAM1201Error('Cannnot find the template file "%s"'%templ)
        return templ

    def getTemplSub(self, subName, keyName):
        name = 'templ.sub.%s.py'%str(subName)
        subFile = os.path.join(self.getPath('templ'), name)
        if not os.path.exists(subFile):
            raise TEAM1201Error('Cannnot find the template sub-file "%s"'%subFile)
        subStr = read_file(subFile)
        return eval(subStr)[keyName]

def absPath(*path):
    return os.path.abspath(os.path.join(*path))

def write_by_jinja(templ, target, content):
    templ_txt = read_file(templ)
    templ = Template(templ_txt)
    write_file(target, templ.render(content))

def print_sep(info, on_start=True, num=20):
    if on_start:
        fmt = '{0}\n{1}'
    else:
        fmt = '{1}\n{0}\n'
    slog.info(fmt.format(info,'='*num))

def print_info(start, end, num=20):
    def B():
        print_sep(start, True, num)
        print_sep(start, False, num)
    return B
