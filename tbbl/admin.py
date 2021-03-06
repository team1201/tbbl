########################################
# admin.py
#
# Author: zrong
# Creation: 2015-04-17
########################################

import os
import subprocess
from zrong import (slog)
from zrong.base import (list_dir, create_zip, DictBase)
from zrong.ftp import ( upload_file, upload_dir)

class AdminBase(object):

    def __init__(self, gconf, gargs, parser=None):
        self.conf = gconf
        self.args = gargs
        self.parser = parser

    def isAdmin():
        return False

    # Child Class must implement it.
    def newConf():
        return None

    def upload218Tool(self, filePath, remotePath, removeFile):
        ftpConf = self.conf.getFtpConf(self.args.ftp)
        ftpConf.start_path = ftpConf.tool_dir
        return upload_file(filePath, remotePath, ftpConf, removeFile)

    def upload218Doc(self, dirName, uploadDir):
        ftpConf = self.conf.getFtpConf(self.args.ftp)
        ftpConf.start_path = ftpConf.doc_dir
        upload_dir(dirName, uploadDir, ftpConf)

    def upload218Lib(self, filePath, remotePath):
        ftpConf = self.conf.getFtpConf(self.args.ftp)
        ftpConf.start_path = ftpConf.lib_dir
        return upload_file(filePath, remotePath, ftpConf, True)

    def upload218Sim(self, filePath, remotePath, delFile=True):
        ftpConf = self.conf.getFtpConf(self.args.ftp)
        ftpConf.start_path = ftpConf.sim_dir
        return upload_file(filePath, remotePath, ftpConf, delFile)

    def rebuildConf(self):
        if os.path.exists(self.conf.conf_file):
            os.remove(self.conf.conf_file)
        workDir = self.conf.getPath('work')
        confFile = self.conf.conf_file
        self.conf = self.newConf()
        self.conf.init(workDir, confFile)
        slog.info('Regenerate "%s" done.'%confFile)

    def src(self):
        srcDIR = self.conf.getClientPath('src')

        slog.info('Packaging lua framework to a tempfile')
        files = []
        for p, d, fs in os.walk(srcDIR, followlinks=True):
            for f in fs:
                path = os.path.join(p,f)
                if '.DS_Store' in path:
                    continue
                files.append(path)
        pre = len(srcDIR)-3
        self.upload218Sim(create_zip(files, pre), self.conf.lib_conf.src)

    def res(self):
        resDir = self.conf.getClientPath('res')
        slog.info('Packaging resources to a tempfile')
        files = []
        for p, d, fs in os.walk(resDir):
            for f in fs:
                path = os.path.join(p, f)
                if '.DS_Store' in path:
                    continue
                files.append(path)

        # len('res') == 3, it will includ 'res' prefix in zip file
        pre = len(resDir)-3
        self.upload218Sim(create_zip(files, pre), self.conf.lib_conf.res)

    def cocos(self):
        if not self.isAdmin():
            return

        cocosdir = os.getenv("COCOS_DIR")
        cocos2dx = os.path.abspath(os.path.join(cocosdir, 'cocos2d-x'))
        if not os.path.exists(cocos2dx):
            raise TEAM1201Error('Cannot find cocos2d-x!')

        slog.info('Packaging cocos2d-x library "%s" to a tempfile.'%cocos2dx)
        files = []
        for p, d, fs in os.walk(cocos2dx, followlinks=True):
            ignore = False
            for ignoreFile in ('.git', 'docs', 'tests', 'licenses'):
                if os.path.join(cocos2dx, ignoreFile) in p:
                    ignore = True
                    break
            if ignore:
                continue
            for f in fs:
                path = os.path.join(p,f)
                ignore = False
                for part in ('.git', '.DS_Store'):
                    if part in path:
                        ignore = True
                        break
                if ignore:
                    continue
                if os.path.islink(path):
                    continue
                files.append(path)

        pre = len(cocosdir)+1
        self.upload218Lib(create_zip(files, pre), self.conf.lib_conf.cocos)

    def cpp(self):
        if not self.isAdmin():
            return

        dirname = 'runtime-src'
        runtimeDir = self.conf.getDistPath(dirname)

        slog.info('Packaging C++ project files to a tempfile.')
        files = []
        for p, d, fs in os.walk(runtimeDir, followlinks=True):
            for f in fs:
                path = os.path.join(p,f)
                if '.DS_Store' in path:
                    continue
                files.append(path)
    
        slog.info('runtimeDir:%s', runtimeDir)
        # Save dirname in zip.
        pre = len(runtimeDir)-len(dirname)
        self.upload218Lib(create_zip(files, pre), self.conf.lib_conf.cpp)

    def lua(self):
        if not self.isAdmin():
            return

        srcDIR = self.conf.getClientPath('src')

        slog.info('Packaging lua framework to a tempfile')
        files = []
        for aDIR in (
                os.path.join(srcDIR, 'zrong'), 
                os.path.join(srcDIR, 'quick'), 
                os.path.join(srcDIR, 'cocos'),
                ):
            for p, d, fs in os.walk(aDIR, followlinks=True):
                for f in fs:
                    path = os.path.join(p,f)
                    if '.DS_Store' in path:
                        continue
                    files.append(path)
        
        pre = len(srcDIR)+1
        self.upload218Lib(create_zip(files, pre), self.conf.lib_conf.lua)

    def toluaauto(self, bindType):
        if not self.isAdmin():
            return
        inifile = None
        cwd = self.conf.getDistPath('tolua', 'auto')
        for f in list_dir(cwd):
            if f.endswith('.ini') \
            and f.startswith('cocos2dx_') \
            and bindType in f.lower():
                inifile = f
        if inifile:
            xarg = [self.conf.getExe('python2'), 'genbindings.py', inifile]
            slog.warning('toluaauto args: %s', xarg)
            slog.warning('toluaauto target path: %s', cwd)
            py = subprocess.Popen(xarg, cwd=cwd)
            py.wait()
        else:
            slog.error('Cannot find a file named %s!'%bindType)

    def toluamanual(self, bindType):
        if not self.isAdmin():
            return
        toluafile = None
        cwd = self.conf.getDistPath('tolua', 'manual')
        for f in list_dir(cwd):
            if f.endswith('.tolua') \
            and bindType in f.lower():
                toluafile = f
        if toluafile:
            bindName = os.path.join(self.conf.getDistPath('tolua', 'manual'), toluafile)
            php = self.conf.getBin('quick/lib/compile_luabinding.php')
            xarg = [self.conf.getPHP(), php, '-pfx', 'cc', '-d', 
                    self.conf.getDistPath('runtime-src', 'Classes',
                        'lua-bindings', 'manual'), bindName]
            subprocess.call(xarg)
        else:
            slog.error('Cannot find a file named %s!'%bindType)

    def build(self):
        # After update self or rebuild conf, dismiss all others action.
        if self.args.reconf:
            self.rebuildConf()
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
        if self.args.res:
            self.res()
            noAnyArgs = False
        if self.args.src:
            self.src()
            noAnyArgs = False
        if self.args.toluamanual:
            self.toluamanual(self.args.toluamanual)
            noAnyArgs = False
        if self.args.toluaauto:
            self.toluaauto(self.args.toluaauto)
            noAnyArgs = False

        return noAnyArgs

