#! /usr/bin/env python
#coding=utf-8
from datetime import datetime

def GetLocalTime():
    dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')