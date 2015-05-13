########################################
# tp.py
#
# Convert images to sprite sheet by TexturePacker
# Author: zrong
# Creation: 2015-05-06
########################################

import os
import shutil
import subprocess
from zrong import slog

def _get_args_list(options):
    return options.strip().split(' ')

def convert_to_cocos2d(tpexe, source, output, dirname, disable_rotation=False, options=None):
    plist_file = os.path.join(output, dirname+".plist")
    png_file = os.path.join(output, dirname+".png")
    imagefolder = os.path.join(source, dirname)
    xargs = ["--sheet", png_file, "--data", plist_file]
    if options:
        xargs = xargs + _get_args_list(options)
    if disable_rotation:
        xargs.append('--disable-rotation')
    succ = convert_by_options(tpexe, xargs, imagefolder)
    if succ:
        slog.info("\n.... converting %s", dirname)

def convert_by_options(tpexe, options, imagefolder):
    """
    options must be a list or a string
    """
    xargs = [tpexe]
    argslist = None
    if isinstance(options, list):
        argslist = options
    elif isinstance(options, str):
        argslist = _get_args_list(options)
    if not argslist:
        slog.error("Please give some options.")
        return False
    for value in argslist:
        xargs.append(value)
    xargs.append(imagefolder)
    tpout = subprocess.check_output(xargs, universal_newlines=True)
    slog.info("Call TexturePacker, command line is: \n")
    slog.warning("%s\n", " ".join(xargs))
    slog.info("%s\n", tpout)
    return True
