########################################
# util/firim.py
# Upload package to fir.im
#
# Author zrong(zengrong.net)
# Creation 2015-03-10
########################################

import os
import requests
from zrong import slog
from tbbl.base import print_sep
import datetime

def _getInfo(appid, token, typ):
    return 'http://fir.im/api/v2/app/info/%s?token=%s&type=%s'%(appid,token,typ)

def upload(appid, token, typ, fil):
    if not os.path.exists(fil):
        print_sep('File [%s] is not found, please check '
                '[pub_conf.file.ios.file] in config file.'%fil, True, 40)
        return

    # 1. get upload info
    info = requests.get(_getInfo(appid,token,typ))
    infoJson = info.json()
    # 2. upload files
    slog.info('upload files ...')
    pkg = infoJson['bundle']['pkg']
    req = requests.post(
        url = pkg['url'],
        data={'key':pkg['key'], 'token':pkg['token']},
        files={ 'file':(os.path.split(fil)[1], open(fil,'rb'), 'application/octet-stream')}
    )
    reqJson = req.json()
    if reqJson['code'] == 0:
        if args.desc:
            desc = {'changelog': args.desc}
        else:
            desc = {'changelog': str(datetime.now().strftime('%y-%m-%d %I:%M:%S'))}

        req = requests.put(
            url = 'http://fir.im/api/v2/app/%s?token=%s'%(infoJson['id'], token),
            data=desc
        )
        print_sep(req.json()['short'] + ' upload complete!', False, 40)
