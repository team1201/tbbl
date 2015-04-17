import os
import sys
import logging
import importlib
from zrong import slog, add_log_handler
from tbbl import base, config

__all__ = ['base', 'admin', 'init', 'update', 'config', 'templ', 'res', 'server']

def TEAM1201Error(Exception):
    pass

def _build(name, conf, args, parser):
    pack = importlib.import_module("yhqb."+name)
    pack.build(conf, args, parser)


def main():
    add_log_handler(slog, 
            handler=logging.StreamHandler(sys.stdout),
            debug=logging.DEBUG)
    gconf = base.Conf()
    workDir = os.path.abspath(os.path.join(''))
    confFile = os.path.join(workDir, "yhqb_conf.py")
    if not os.path.exists(confFile):
        confFile = os.path.join(os.path.expanduser('~'), 'yhqb_conf.py')

    slog.info('\nconffile:%s\n', confFile)
    if os.path.exists(confFile):
        oldconf = base.Conf()
        oldconf.readFromFile(confFile)
        gconf.updateConf(oldconf)
    else:
        gconf.init(workDir, confFile)
    if not config.checkConf(gconf):
        exit(1)
    if not config.checkEnv(gconf):
        exit(1)

    gargs, subParser = config.checkArgs(gconf)
    if gargs:
        _build(gargs.sub_name, gconf, gargs, subParser)

