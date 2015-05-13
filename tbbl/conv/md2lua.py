#!/usr/bin/env python
#coding:utf-8
'''
#=============================================================================
#     FileName: md2lua.py
#         Desc: Convert markdown to a lua file.
#       Author: sunminghong
#        Email: allen.fantasy@gmail.com
#     HomePage: http://weibo.com/5d13
#      Version: 0.1.1
#   LastChange: 2015-05-06 zrong
#      History:
#=============================================================================
'''

import sys
import os
from zrong import (slog)
from zrong.base import (write_file, read_file, list_dir)

lineno = 0
verNum = 0
protocolNum = 0

pclient = {}
pserver = {}
pupdate = {}

class Protocol():
    def __init__(self):
        self.code=0
        self.title = ''
        self.ver = 0
        self.datas = []

class ProtoData():
    def __init__(self):
        self.number = ""
        self.fieldname = ""
        self.datatype = ""
        self.comment = ""
        self.datas = []

def proc(fullname):
    global lineno
    slog.info('analyse:%s',fullname)

    f = open(fullname, mode='r', encoding='utf-8')
    flag = 0

    ps = []
    p = Protocol()
    datas = []
    pdatas = None
    indent = 0
    for line in f:
        lineno += 1

        line = line.replace('\t','    ')
        line = line.rstrip()
        if line[0:2] == '//' or not line: # or not (line.strip()):
            continue

        slog.info('lineno: %s, line: %s', lineno, line)
        #line = line.strip()
        if line[0:1] == '#' or flag == 0:
            if line[0:1] == "#":
                if indent == 0 :
                    ps.append(p)
                    p = Protocol()
                    flag = 0
                else:
                    indent -= 4
                    #pdatas = datas.pop()
                    ps.append(p)
                    p = Protocol()
                    flag = 0
            p = Protocol()
            datas = []
            pdatas = None
            indent = 0
            pdatas = p.datas
            datas.append(pdatas)

            if line[0:3] == "###" and line[3:5]=="**" and "**" in line[5:]:
                #proto start
                code = line[5:]
                ss = code.split('**')
                try:
                    p.code = int(ss[0])
                    p.title = ss[1].strip()
                    flag = 1
                    slog.info('code: %s, title: %s', p.code, p.title)
                except:
                    slog.error("%s has err!!!%s" ,lineno,line)
                    return
            continue
        elif flag == 1:
            if line[0:4] == "ver:":
                try:
                    p.ver=int(line[4:])
                    flag = 2
                except:
                    slog.info("%s has err!!!need ver ,but is :%s" ,lineno,line)
                    return
            else:
                slog.info("%s has err!!!need ver ,but is :%s" ,lineno,line)
                return
            continue

        elif flag == 2:
            #parse datas
            if line[0:5] == "data:":
                flag = 3
                continue
            slog.info("%s line has err!!!need data,but is :%s" ,lineno,line)
            return

        elif flag == 3:
            if line[0:1] == "#":
                if indent == 0 :
                    ps.append(p)
                    p = Protocol()
                    flag = 0
                    slog.info('------------------------')
                else:
                    indent -= 4
                    ps.append(p)
                    p = Protocol()
                    flag = 0
                    #pdatas = datas.pop()
                    slog.info('---...............---------------------')
                continue

            ss = line.split("+")
            if len(ss) == 1:
                if len(p.datas)==0:
                    slog.info("%s line has err!!!need '+ ',but is :%s" ,lineno,line)
                    flag = 0
                    continue
                else:
                    #parse one protocol ,then write to xml or other
                    if indent == 0 :
                        ps.append(p)
                        p = Protocol()
                        flag = 0
                    else:
                        indent -= 4
                        #pdatas = datas.pop()
                        ps.append(p)
                        p = Protocol()
                        flag = 0
                    continue

            if '[(' in ss[1] or ')...]' in ss[1]:
                continue

            if len(ss[0]) < indent:
                #this layer is end
                indent -= 4
                #pdatas = datas.pop()

            if indent > 0 :
                continue

            ss = ss[1]
            ss = ss.split(",")

            da = ProtoData()
            da.number = int(ss[0])
            da.datatype = ss[1].strip()
            if da.datatype == "":
                da.datatype = "uvint"

            if da.datatype not in ["uvint","vint","uint32","uint16","string","list"]:
                slog.info("%s datatype is wrong!!!" ,lineno)
                #slog.info("%s datatype is wrong!!!line:%s" ,lineno,line)
                return

            da.fieldname = ss[2].strip()
            da.comment = ss[3].strip()

            # slog.info(indent)
            # slog.info(da.number)
            # slog.info(da.fieldname)
            # slog.info(da.datatype)
            # slog.info(da.comment)

            pdatas.append(da)

            if da.datatype == "list":
                #da.datas= []
                #flag == 4
                indent += 4

                #datas.append(pdatas)
                #pdatas = da.datas

            continue

    slog.info('---------')
    if p and len(p.datas)>0:
        ps.append(p)

    f.close()
    renderLua(ps)

def renderLua(ps):
    global verNum, protocolNum

    slog.info('rendering ...')
    datatypes = {
        "uvint":"R",
        "vint":"r",
        "string":"S",
        "list":"t"
        }

    def _items(das):
        ts = []
        keys = []
        for da in das:
            #slog.info(da.datatype)
            ts.append(datatypes[da.datatype])
            keys.append(da.fieldname)

        d = {
            "fmt":''.join(ts),
            "keys":keys
        }
        return d

    for p in ps:
        _c = str(p.code)[0:1]
        if _c == '1':
            pps = pclient
        elif _c == '2':
            pps = pserver
        else:
            pps = pupdate

        p.code = int(p.code)
        if p.code not in pps:
            pps[p.code] = {}

        pps[p.code][int(p.ver)] = _items(p.datas)

        #slog.info('//-----// protocolNum:%d, code: %s',protocolNum,p.code)
        if p.code:
            protocolNum += 1
            verNum += p.ver + 1

def _dirfolder(adir):
    global lineno
    names = list_dir(adir)

    for name in names:
        if name.endswith('.md'):
            lineno = 0
            proc(os.path.join(adir, name))

def listToLuaString(data,indent):
    sout = ["{"]
    for l in data:
        if isinstance(l,(int,float)):
            sout.append(l + ",")
        else:
            sout.append('"%s",'%l)

    sout.append("},\n")
    return "".join(sout)

def dictToLuaString(data,indent):
    sout = ["{\n"]
    for k in data:
        if isinstance(k,str):
            sout.append(indent+'["%s"] = '%k)
        else:
            sout.append(indent+'[%s] = '%str(k))

        if isinstance(data[k],(dict)):
            sout.append(dictToLuaString(data[k],indent+ "    "))
        elif isinstance(data[k],(int,float)):
            sout.append(data[k] + ",")
        elif isinstance(data[k],(list)):
            sout.append(listToLuaString(data[k],indent+ "    "))
        else:
            sout.append('"%s",'%data[k])

    sout.append("\n%s},\n"%indent)
    return "".join(sout)


def convertProtocol(mddir, protfile):
    _dirfolder(mddir)
    buff = []
    buff.append("local _p = {")
    buff.append('["client"] = %s,' % dictToLuaString(pclient,"    ")[:-2])
    buff.append('["server"] = %s,' % dictToLuaString(pserver,"    ")[:-2])
    buff.append('["update"] = %s,' % dictToLuaString(pupdate,"    ")[:-2])
    buff.append("}")
    buff.append("return _p")

    slog.info('protocolNum:%d'%protocolNum)
    slog.info('protocolNum:%d'%verNum)

    slog.info('Write protocol to "%s".'%protfile)
    write_file(protfile, '\n'.join(buff))

def convertVersion(mddir, verfile):
    _dirfolder(mddir)
    slog.info('Write version "%d" to "%s".'%(verNum, verfile))
    slog.info('protocolNum:%d'%protocolNum)
    write_file(path, str(verNum))
