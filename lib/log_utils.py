#!/usr/bin/python
# -*- coding: UTF-8 -*-

from storageType import storageType
from logType import logType
import dateHelper
import cmd_color_printers

STORAGETYPE = storageType.STDOUTPUT
FILEPATH = ''

def WriteLog(msg = '', logType = logType.INFO):
    if msg.strip() == '':
        log = '\n'
    else:
        log = '[%s]%s\n'%(dateHelper.GetLocalTime(), msg)
    if  logType == logType.INFO:
        cmd_color_printers.printDarkGreen(log)
    elif logType == logType.WARN:
        cmd_color_printers.printDarkYellow(log)
    elif logType == logType.ERROR:
        cmd_color_printers.printRed(log)
    elif logType == logType.RESULT:
        cmd_color_printers.printYellow(log)
    elif logType == logType.TITLE:
        cmd_color_printers.printGreen(log)
    else:
        cmd_color_printers.printWhite(log)
    
    WriteToStorage(log)


def WriteToStorage(msg):
    if STORAGETYPE == storageType.STDOUTPUT:
        pass
    elif STORAGETYPE == storageType.FILE:
        fo = open(FILEPATH, 'a+')
        fo.writelines(msg)
        fo.flush()
        fo.close()
    else:
        print u'暂不支持当前存储方式'
        pass
        


