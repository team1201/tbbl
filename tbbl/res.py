########################################
# res.py
# Convert resource files to client/res
#
# Author zrong(zengrong.net)
# Creation 2015-04-20
########################################

import os
import subprocess
import shutil
from zrong import (slog, ZrongError)
from zrong.base import (list_dir, copy_dir, get_files)
import zrong.lua as lua
from zrong.gettext import Gettext
from tbbl.base import (write_by_jinja, print_sep)

class AniDef(object):
    def __init__(self, conf, aniDir, aniArg, gendef):
        self._conf = conf
        self._aniDir = aniDir
        self._aniArg = aniArg
        self._piecedirs = None
        self._pieces = None
        self._spritesheets = None
        self._gendef = gendef
        # 2015-01-13 DO NOT use _def no longer.
        # Will generate all of the def files automatically.
        # self.initDef()
    
    def checkAni(self):
        if not self.getPieceDirs() and self.getAnisInSpriteSheet():
            slog.error('No animation resources.')
            return False
        if not self.getAnisInPiece():
            return False
        return True

    def getPieceDirs(self):
        if not self._piecedirs:
            self._piecedirs = list(list_dir(self._aniDir, include_file=False))
        return self._piecedirs

    def getAniDefs(self):
        anidef = []
        for f in list_dir(self._aniDir):
            if f.startswith('ani_def_') and f.endswith('.lua'):
                anidef.append(f)
        return anidef

    def getAnisInSpriteSheet(self):
        if not self._spritesheets:
            sp = []
            for f in list_dir(self._aniDir):
                if f.startswith('ani_') and f.endswith('.plist'):
                    sp.append(os.path.splitext(f)[0])
            self._spritesheets = sp
        return self._spritesheets

    def getAnisInPiece(self):
        if not self._pieces:
            if not self._aniArg:
                self._pieces = self.getPieceDirs()
            else:
                anis = []
                for ani in self._aniArg:
                    if not ani.startswith('ani_'):
                        ani = 'ani_'+ani 
                    if not ani in self._piecedirs:
                        slog.error('%s is not an animation resource.', ani)
                        return None
                    anis.append(ani)
                self._pieces = anis
        return self._pieces

    def generateADef(self, ani):
        if not self._gendef:
            return
        pieceNum = len(list(list_dir(os.path.join(self._aniDir, ani))))
        sub = {
            'spritesheets':[ani],
            'animations'  :[{ 
                'name':ani,
                'delay_per_unit':0.042,
                'loops':1,
                'restore_original_frame':'false', 
                'range':{'start':1,'end':pieceNum},
                }],
        }
        # animation file is started by "ani_", main name starts from index 4.
        defName = 'ani_def_%s.lua'%ani[4:]
        defFile = self._conf.getClientPath('res', 'ani', defName)
        write_by_jinja(self._conf.getJinjaTempl('ani_def.lua'), defFile, sub)
        slog.info('Generate a ani_def file: %s.'%defFile)

    # 2015-01-13 DEPARTED
    def getPlistDirs(self, defName):
        path = os.path.join(self._aniDir, defName)
        try:
            aniDef = lua.decode_file(path)
        except ZrongError as e:
            slog.critical(e)
            return None
        return aniDef['spritesheets']

    # 2015-01-13 DEPARTED
    def initDef(self):
        for afile in list_dir(self._aniDir, includeFile=True):
            if os.path.isdir(afile):
                self._piecedirs.append(afile)
            elif afile != 'ani_def_sample.lua' \
            and afile.startswith('ani_def_') \
            and afile.endswith('.lua') :
                self._def.append(afile)

    # 2015-01-13 DEPARTED
    def getPlistDirsFromAniDef(self, defName):
        path = os.path.join(self._aniDir, defName)
        try:
            aniDef = lua.decode_file(path)
        except ZrongError as e:
            slog.critical(e)
            return None
        return aniDef['spritesheets']

    # 2015-01-13 DEPARTED
    def getNamesFromList(self, aniList):
        if len(aniList) == 0:
            return list(self._def)
        def _expendDef(self, name):
            return 
        existList = []
        for ani in aniList:
            if not ani.startswith('ani_def_'):
                fullName = 'ani_def_%s.lua'%ani
            else:
                fullName = ani+'.lua'
            if fullName in self._def:
                existList.append(fullName)
            else:
                slog.error('The ani_def file %s is not existed'%fullName)
        if len(existList) == 0:
            slog.error('No ani_def file in providing list!')
            return None
        return existList

class ResBase(object):

    def __init__(self, gconf, gargs, parser=None):
        self.conf = gconf
        self.args = gargs
        self.parser = parser

    def _print_copy(self, s, d):
        slog.info("Copying [%s] to [%s].", s, d)

    def _getSpecialDir(self, resType):
        lang = self.args.lang
        density = self.args.density
        vendor = self.args.vendor
        source = self.conf.getGit('resource', 'path')
        defaultDir = os.path.join(source, '%s@@@'%resType)
        if not os.path.isdir(defaultDir):
            slog.error('The directory [%s] is not existence!'%defaultDir)
            return None, None
        specialDir = os.path.join(source, '%s@%s@%s@%s'%(resType, density, lang, ''))
        if os.path.isdir(specialDir):
            return defaultDir, specialDir
        slog.warning('The directory [%s] is not existed!'%specialDir)
        return defaultDir, None

    def _copyDir(self, root, outputDir, name):
        sourcePath = os.path.join(root, name)
        destPath = os.path.join(outputDir, name)
        if os.path.isdir(sourcePath):
            self._print_copy(sourcePath, destPath)
            copy_dir(sourcePath, destPath)
        elif os.path.isfile(sourcePath):
            # Ignore py file, it maybe a tool script file.
            if not sourcePath.endswith('.py'):
                self._print_copy(sourcePath, destPath)
                shutil.copy(sourcePath, destPath)
        else:
            slog.warning('The directory [%s] is non-existence.'%sourcePath)

    def _rebuildDir(self, adir):
        if self.args.force and os.path.isdir(adir):
            slog.info('\nGot --force, remove directory [%s].\n', adir)
            shutil.rmtree(adir)

        os.makedirs(adir, exist_ok=True)

    def _merge2Tmp(self, default, special, dirList=None):
        tempDir = tempfile.mkdtemp(prefix='tbbl_')
        slog.info("Make a temporary directory: %s", tempDir)
        print_sep('Start to merge directory [%s] and [%s] to temporary directory.'
                %(default, special))
        # Merge sub-directory one by one.
        if dirList:
            self._mergeSpecial(dirList, tempDir, default, special)
        # Merge root directory.
        else:
            if os.path.isdir(default):
                slog.warning('The directory [%s] is not existed.'%sourcePath)
                return None
            copy_dir(default, tempDir)
            copy_dir(special, tempDir)
        print_sep('Merging has done.', False)
        return tempDir

    def _mergeSpecial(self, dirList, outputDir, default, special=None):
        if special:
            special_list = list(list_dir(special))
        # Copy default directory list.
        for adir in dirList:
            self._copyDir(default,  outputDir, adir)
            # Copy special directory list.
            if special and (adir in special_list):
                self._copyDir(special,  outputDir, adir)

    def _commonProcess(self, dirList, souName, outName=None):
        print_sep('\nStart to process %s in directory [%s].'
                %(dirList, souName), True, 40)
        default, special = self._getSpecialDir(souName)
        if not default:
            return
        if not outName:
            outName = souName
        # User don't provide any files.
        if len(dirList) == 0:
            dirList = list(list_dir(default))
            # Some dir maybe in specialDir but not in defaultDir.
            # Merge them into dirList
            if special:
                specialList = list(list_dir(special))
                if specialList:
                    dirList = list(set(dirList+specialList))
            if len(dirList) == 0:
                slog.error('The directory [%s] is empty.'%default)
                return
        outputDir = self.conf.getClientPath('res', outName)
        self._rebuildDir(outputDir)

        self._mergeSpecial(dirList, outputDir, default, special)
        print_sep('Process %s in directory [%s] has done.'
                %(dirList, souName), False, 40)

    def _convertSS(self, sourceDir, outputDir, dirName):
        plist_file = os.path.join(outputDir, dirName+".plist")
        png_file = os.path.join(outputDir, dirName+".png")
        slog.info("\n.... converting %s", dirName)
        tpOut = subprocess.check_output([ 
            self.conf.getExe("tp"),
            "--sheet", png_file,
            "--data", plist_file,
            os.path.join(sourceDir, dirName)
            ], universal_newlines=True)
        slog.info("%s\n", tpOut)
        
    def plst(self, plist):
        print_sep('Start to process %s in directory plst.'
                %plist, True, 40)
        default, special = self._getSpecialDir('plst')
        if not default:
            return
        if len(plist) == 0:
            plist = list_dir(default)
        outputDir = self.conf.getClientPath('res', 'plst')
        self._rebuildDir(outputDir)
        sourceDir = default

        tmpDir = None
        if special:
            tmpDir = self._merge2Tmp(default, special, plist)
            plist = list_dir(tmpDir)
            sourceDir = tmpDir
        print_sep('Start to convert spritesheet.')
        for dir_name in plist:
            self._convertSS(sourceDir, outputDir, dir_name)
        print_sep('Spritsheet converting has done.', False)
        if tmpDir:
            slog.info('Remove temporary directory [%s].'%tmpDir)
            shutil.rmtree(tmpDir)
        print_sep('Process %s in directory plst has done.'
                %list(plist), False, 40)

    def pdir(self, pdir):
        self._commonProcess(pdir, 'pdir')

    # 2015-01-13 DEPARTED
    # Use manual ani_def file
    def _processAniByCustomDef(self, ani):
        default, special = _getSpecialDir('ani')
        if not default:
            return

        if special:
            default = _merge2Tmp(default, special)
        aniDef = AniDef(default)
        aniDef.initDef()
        names = aniDef.getNamesFromList(ani)
        if not names:
            return

        outputDir = self.conf.getClientPath('res', 'ani')
        _rebuildDir(outputDir)

        print_sep('Start to convert animation.')
        for defName in names:
            plistDirs = aniDef.getPlistDirsFromAniDef(defName)
            if not plistDirs:
                continue
            for adir in plistDirs:
                _convertSS(default, outputDir, adir)
            shutil.copy(os.path.join(default, defName), 
                    os.path.join(outputDir, defName))
        print_sep('Animation convert done.', False)

    def arm(self, arm):
        self._commonProcess(arm, 'arm')

    def fnt(self, fnt):
        self._commonProcess(fnt, 'fnt')

    def snd(self, snd):
        self._commonProcess(snd, 'snd')

    def par(self, par):
        self._commonProcess(par, 'par')

    def oth(self, oth):
        self._commonProcess(oth, 'oth')

    def test(self):
        res = self.conf.getGit('resource', 'path')
        sourcedir = os.path.join(res, 'test')
        targetdir = self.conf.getClientPath('res', 'test')
        self._print_copy(sourcedir, targetdir)
        if os.path.exists(targetdir):
            shutil.rmtree(targetdir)
        shutil.copytree(sourcedir, targetdir)
        slog.info('Copy done.')

    def gettext(self, gettext):
        if self.conf.is_windows:
            gt = Gettext(True, self.conf.getExe('gettext'))
        else:
            gt = Gettext()
        po_file = self.conf.getClientPath("i18n", self.args.lang+'.po')
        mo_file = self.conf.getClientPath("res", self.args.lang)
        if not os.path.exists(po_file):
            slog.error('CANNOT find the po file: [%s]!'%po_file)
            return

        if gettext == 'mo':
            print_sep('\nStart to convert [%s] to [%s].'%(po_file, mo_file), True, 40)
            gt.fmt(po_file, mo_file)
            print_sep('Converting PO to MO has done.', False, 40)
        else:
            # Include (game/login/conf/root)
            lua_files = list(get_files(self.conf.getClientPath('src', 'conf'), ext=['.lua'])) + \
                list(get_files(self.conf.getClientPath('src', 'game'), ext=['.lua'])) + \
                list(get_files(self.conf.getClientPath('src', 'login'), ext=['.lua'])) + \
                list(get_files(self.conf.getClientPath('src', 'root'), ext=['.lua']))
            print_sep('\nStart to merge new translatations to [%s].'%po_file, True, 40)
            gt.merge(po_file, lua_files)
            print_sep('Merging has done.', False, 40)

    def all(self):
        resDir = self.conf.getClientPath('res')
        self._rebuildDir(resDir)

        self.plst([])
        self.pdir([])
        self.arm([])
        self.fnt([])
        self.par([])
        self.snd([])
        self.oth([])
        self.test()
        self.gettext('mo')

    def build(self):
        noAnyArgs = True
        if self.args.plst != None:
            self.plist(self.args.plst)
            noAnyArgs = False
        if self.args.pdir != None:
            self.pdir(self.args.pdir)
            noAnyArgs = False
        if self.args.arm != None:
            self.arm(self.args.arm)
            noAnyArgs = False
        if self.args.fnt != None:
            self.fnt(self.args.fnt)
            noAnyArgs = False
        if self.args.par != None:
            self.par(self.args.par)
            noAnyArgs = False
        if self.args.snd != None:
            self.snd(self.args.snd)
            noAnyArgs = False
        if self.args.oth != None:
            self.oth(self.args.oth)
            noAnyArgs = False
        if self.args.test:
            self.test()
            noAnyArgs = False
        if self.args.gettext:
            self.gettext(sef.args.gettext)
            noAnyArgs = False

        return noAnyArgs

