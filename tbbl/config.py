# -*- coding: utf-8 -*-

import os
import argparse
import shutil
from zrong.base import slog

def checkConf(conf, name_list='zrong'):
    if conf.user_conf.name == 'master':
        slog.error('Please modify "user_conf.name" to a TRUE name'
                '(%s) in your config file.'%name_list)
        return False
    return True

def checkEnv(conf):
    if not shutil.which("git", mode=os.X_OK):
        if conf.is_windows:
            slog.error("git is unfindable. "
                'If you are using "Git for windows", please add '
                r'"C:\Program Files (x86)\Git\cmd" '
                "to PATH.")
        else:
            slog.error("git is unfindable.")
        return False

    if not conf.check_exe:
        return True

    for exe in conf.exe_conf.keys():
        if not conf.getExe(exe, True):
            slog.error('%s is unfindable. '
                'Please set its path in hhlb_conf.py'%exe)
            return False

    return True


class CommandLineBase(object):

    def __init__(self, prog):
        self.prog = prog

    def addCommonArgs(self, parser, *types):
        if len(types) == 0:
            types = ('lang', 'density', 'vendor')
        for typ in types:
            if typ == 'lang':
                parser.add_argument('--lang', type=str, 
                    default='zh_tw', choices=['en_us','zh_cn', 'zh_tw'],
                    help='指定语言版本。默认使用 zh_tw 。')
            elif typ == 'density':
                parser.add_argument('--density', type=str, 
                    default='sd', choices=['sd'],
                    help='指定分辨率。默认使用 sd 。')
            elif typ == 'vendor':
                parser.add_argument('--vendor', type=str, 
                        default='team1201', choices=['team1201'],
                    help='指定运营商。默认使用 team1201 。')

    def addGitArgs(self, parser, git_conf, init):
        gitreponames = sorted(git_conf.keys())
        fmt = '%s git 仓库 [%s]。'
        for repo in gitreponames:
            gitpath = git_conf[repo].git
            helptxt = fmt%('初始化', gitpath) if init else fmt%('更新', gitpath)
            parser.add_argument('--'+repo, action='store_true', help=helptxt)

    def addAdmin(self, conf):
        parserAdmin = self.subParsers.add_parser('admin', 
            help='管理员专用。一般为 zrong 使用。')
        parserAdmin.add_argument('--src', action='store_true', 
            help='打包 src 文件夹并上传到18 。当然包含 --lua 参数中的所有内容。')
        parserAdmin.add_argument('--res', action='store_true', 
            help='打包 res 文件夹并上传到18。')
        parserAdmin.add_argument('--reconf', action='store_true', 
            help='重建 yhqb_conf.py.')
        parserAdmin.add_argument('--cocos', action='store_true', 
            help='（zrong 专用）打包 cocos2d-x 源码，并上传到18。')
        parserAdmin.add_argument('--lua', action='store_true', 
            help='（zrong 专用）打包 lua 框架（包含src目录下的'
            'quick、cocos、zrong 三个文件夹）并上传到18。')
        parserAdmin.add_argument('--cpp', action='store_true', 
            help='（zrong 专用）打包 frameworks/runtime-src 文件夹并上传到18。')
        parserAdmin.add_argument('--toluaauto', type=str,
            choices = ['filter', 'dragonbones', 'webview'],
            help='（zrong 专用）创建 lua 自动绑定文件。')
        parserAdmin.add_argument('--toluamanual', type=str,
            choices = ['helperfunc', 'network', 'crypto', 'native'],
            help='（zrong 专用）创建 lua 手动绑定文件。')
        return parserAdmin

    def addInit(self, conf):
        parserInit = self.subParsers.add_parser('init', help='初始化月湖桥项目。')
        parserInit.add_argument('-f', '--force', action='store_true', 
            help='取消所有当前没有提交的修改，强制初始化。')
        parserInit.add_argument('-a', '--all', action='store_true', 
            help='初始化所有的 git 仓库和框架。')
        self.addGitArgs(parserInit, conf.git_conf, True)
        return parserInit

    def addUpdate(self, conf):
        parserUpdate = self.subParsers.add_parser('update', 
            help='更新所有的 git 仓库和框架。')
        parserUpdate.add_argument('-f', '--force', action='store_true', 
            help='在 git 仓库中执行 "git reset --hard" 并推送(pull)。')
        parserUpdate.add_argument('-a', '--all', action='store_true', 
            help='采用默认设置更新所有。')
        parserUpdate.add_argument('--cocos', action='store_true', 
            help='更新 cocos2d-x 框架。目标路径 client/frameworks/cocos2d-x 。')
        parserUpdate.add_argument('--lua', action='store_true', 
            help='更新 lua 框架。目标路径 client/src/[quick,cocos,zrong] 。')
        parserUpdate.add_argument('--cpp', action='store_true', 
            help='更新 C++ 项目文件。目标路径 client/framworks/runtime-src 。')
        return parserUpdate

    def addTempl(self, conf):
        parserTempl = self.subParsers.add_parser('templ', 
            help='基于 client/template 中的 templ.sub.[name].py 模版替换文件生成配置文件.')
        parserTempl.add_argument('-n', '--templ-sub-name', type=str, default='1',
            help='提供一个模版替换文件的名称。不提供则使用 client/template/templ.sub.1.py 。')
        parserTempl.add_argument('-a', '--all', action='store_true', 
            help='使用默认设置生成所有配置文件。')
        parserTempl.add_argument('--runapp', action='store_true', 
            help='生成 client/runapp.bat 或者 client/runapp.sh 用于快速启动模拟器。')
        parserTempl.add_argument('--resinfo', action='store_true', 
            help='生成 client/res/resinfo.lua 。')
        return parserTempl

    def addConf(self, conf):
        parserConf = self.subParsers.add_parser('conf', 
            help='处理 config 项目中的配置文件，处理后复制到 client/src/conf 文件夹。')
        self.addCommonArgs(parserConf, 'lang')
        parserConf.add_argument('-f', '--force', action='store_true', 
            help='在处理资源之前，先删除配置文件所在的文件夹。')
        parserConf.add_argument('-a', '--all', action='store_true', 
            help='使用默认设置处理所有配置文件。')
        parserConf.add_argument('--prot', action='store_true',
            help='转换网络协议文件。目标文件夹为 client/src/conf/c1/protocols.lua 。')
        return parserConf

    def addRes(self, conf):
        parserRes = self.subParsers.add_parser('res', 
            help='处理 resource、client/i18n 项目中的资源，处理后复制到 client/res 文件夹。')
        self.addCommonArgs(parserRes)
        parserRes.add_argument('-f', '--force', action='store_true', 
            help='在处理资源之前，先删除资源所在的文件夹。')
        parserRes.add_argument('-a', '--all', action='store_true', 
            help='使用默认设置处理所有资源。')
        parserRes.add_argument('--plst', type=str, nargs='*',
            help='处理碎图图像文件。'
            '将 plst 文件夹中的碎图转换成 SpriteSheet 格式。'
            '目标文件夹为 client/res/plst 。若不提供具体的文件，则处理所有文件。')
        parserRes.add_argument('--pdir', type=str, nargs='*',
            help='处理 pdir 中的独立图像资源。'
            '目标文件夹为 client/res/pdir 。'
            '若不提供具体的文件，则处理所有文件。')
        parserRes.add_argument('--arm', type=str, nargs='*',
            help='处理骨骼动画资源。'
            '目标文件夹为 client/res/pdir 。'
            '若不提供具体的文件，则处理所有文件。')
        parserRes.add_argument('--fnt', type=str, nargs='*',
            help='处理字体资源。目标文件夹为 client/res/fnt 。'
            '若不提供具体的文件，则处理所有文件。')
        parserRes.add_argument('--par', type=str, nargs='*',
            help='处理粒子资源。目标文件夹为 client/res/par 。'
            '若不提供具体的文件，则处理所有文件。')
        parserRes.add_argument('--snd', type=str, nargs='*',
            help='处理声音资源。目标文件夹为 client/res/snd 。'
            '若不提供具体的文件，则处理所有文件。')
        parserRes.add_argument('--ani', type=str, nargs='*',
            help='处理 ani 动画文件，转换碎图图像，'
            '复制已存在的 sprite sheet，'
            '复制已存在的 ani_def_*.lua 动画定义文件。'
            '目标文件夹为 client/res/ani 。若不提供具体的文件，则处理所有文件。')
        parserRes.add_argument('--oth', type=str, nargs='*',
            help='处理其它资源。目标文件夹为 client/res/oth 。'
            '若不提供具体的文件，则处理所有文件。')
        parserRes.add_argument('--test', action='store_true',
            help='处理测试用的资源资源。目标文件夹为 client/res/test 。')
        parserRes.add_argument('--gen-def', action='store_true',
            help='仅当 --ani 提供了具体值时有效。'
            '自动生成指定的 ani 动画文件的 ani_def_*.lua 。')
        parserRes.add_argument('--gettext', type=str,
            choices=['mo','po'],
            help='转换语言文件。'
            'mo 代表将已有的 po 文件转换成二进制的 mo 格式。'
            'po 代表从 lua 源码中生成 po 文件。'
            '目标文件为 client/res/[lang].mo')
        return parserRes

    def addPngquant(self, conf):
        parserPng = self.subParsers.add_parser('pngquant', 
            help='使用 pngquant 优化 client/res 文件夹中的 png 文件。')
        parserPng.add_argument('--dir', type=str, 
            choices = ['*', 'plst', 'pdir', 'arm', 'ani'], default='*',
            help='指定要处理的文件夹。* 代表所有4个文件夹，默认值为 * 。')
        parserPng.add_argument('--max', type=int, default=90,
            help='指定最高质量，最大值100，默认值为90。')
        parserPng.add_argument('--min', type=int, default=60,
            help='指定最低质量，最小值0，默认值为60。')
        parserPng.add_argument('--speed', type=int, default=3,
            help='速度质量平衡，从1（最慢）到10（最快）。'
            '速度 10 相比减少图片 5%% 质量, 但是 8 倍于默认的速度。默认值为3。')
        parserPng.add_argument('--size', type=int, default=768,
            help='大于这个尺寸的图像才会被转换，默认为768 KB。')
        return parserPng

    def addServer(self, conf):
        parserServer = self.subParsers.add_parser('server', help='服务器程序控制。')
        return parserServer

    def addAndroid(self, conf):
        parserAndroid = self.subParsers.add_parser('android', help='Android 打包和上传。')
        parserAndroid.add_argument('--upload', action='store_true',
            help='上传最新的包到 fir.im。')
        return parserAndroid

    def addIOS(self, conf):
        parserIOS = self.subParsers.add_parser('ios', help='iOS 打包和上传。')
        parserIOS.add_argument('--upload', action='store_true',
            help='上传最新的包到 fir.im。')
        return parserIOS

    def checkArgs(self, conf, argv=None):
        parser = argparse.ArgumentParser(prog=self.prog)
        self.subParsers = parser.add_subparsers(dest='sub_name', help='sub-commands')

        self.addAdmin(conf)
        self.addInit(conf)
        self.addUpdate(conf)
        self.addTempl(conf)
        self.addConf(conf)
        self.addRes(conf)
        self.addPngquant(conf)
        self.addServer(conf)
        self.addAndroid(conf)
        self.addIOS(conf)

        args = parser.parse_args(args=argv)
        if args.sub_name:
            return args, self.subParsers.choices[args.sub_name]
        parser.print_help()
        return None, None
