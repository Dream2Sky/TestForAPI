#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import argparse
from pyfiglet import Figlet
import urllib
import urllib2
from lib.log_utils import logType
from lib import log_utils
import re
import os

URLPATTERN = '^(https?|ftp|file)://.+$'
ISPOST = False
POSTDATA = ''
# banner
f = Figlet()
print f.renderText('liushaoting')

#参数管理
parser = argparse.ArgumentParser(description='Test For API')
parser.add_argument('-U','--url', help=u'API的完整路径')
parser.add_argument('-O', '--output', help=u'输出结果到哪个文件')
parser.add_argument('-F', '--file', help=u'post请求所需的参数文件，当有这个文件的时候才进行post请求，如果没有则默认都是get请求')
parser.add_argument('-L', '--login', action="store_true", help=u'标识当前请求为登陆请求，会自动保存会话信息')
args = parser.parse_args()

url = args.url
output = args.output
postFile = args.file
isLogin = args.login

log_utils.WriteLog(url,logType.WARN)
log_utils.WriteLog(url,logType.ERROR)
log_utils.WriteLog(url)
if not url:
    parser.print_help()
    sys.exit()

if re.match(URLPATTERN, url) is None:
    print u'不合法的URL链接'
    sys.exit()

if postFile:
    ISPOST = True
    if not os.access(postFile, os.R_OK):
        print u'所提供的post文件不存在或不可访问'
        sys.exit()
    else:
        paramFile = open(postFile, 'r+')
        POSTDATA = paramFile.read(paramFile.size)
# req = urllib2.Request(url)

# res_data = urllib2.urlopen(req)
# for header in res_data.headers:
#     print header+':'+res_data.headers[header]
# res = res_data.read()
#print res