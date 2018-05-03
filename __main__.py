#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import argparse
from pyfiglet import Figlet
import urllib
import urllib2
from lib.log_utils import logType
from lib.log_utils import storageType
from lib import log_utils
import re
import os
import json

URLPATTERN = '^(https?|ftp|file)://.+$'
ISPOST = False
POSTDATA = ''
OUTPUT_FILE = None
POST_FILE = None
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'
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

#判断URL是否存在
if not url:
    parser.print_help()
    sys.exit()

#判断URL是否合法
if re.match(URLPATTERN, url) is None:
    print u'不合法的URL链接'
    sys.exit()

#判断是否是POST请求，并判断post文件是否可以访问，可以则读取里面的参数
if postFile:
    ISPOST = True
    if not os.access(postFile, os.R_OK):
        log_utils.WriteLog(u'所提供的post文件不存在或不可访问',logType.ERROR)
        sys.exit()
    else:
        try:
            POST_FILE = open(postFile, 'r+')
            POSTDATA = json.loads(POST_FILE.read())
            print POSTDATA['PostData']
            POST_FILE.close()
        except IOError as e:
            log_utils.WriteLog(e,logType.ERROR)
            sys.exit()
                
#判断是否要输出结果到其他文件
if output:
    output = 'output/'+output
    try:
        OUTPUT_FILE = open(output, 'a+')
        log_utils.STORAGETYPE = storageType.FILE
        log_utils.FILEPATH = output
    except IOError as e:
        log_utils.WriteLog(e,logType.ERROR)
        sys.exit()

#开始请求URL
log_utils.WriteLog(u'request url:'+url)

#构造请求头
proto, rest = urllib.splittype(url)
host, rest = urllib.splithost(rest)
header_dict = {
    'Host':'unkonw' if not host else host,
    'User-Agent':USER_AGENT,
    'Content-Type':'application/json',
    'Connection':'Keep-Alive',
    'Cache-Control':'no-cache'
}
log_utils.WriteLog('request-headers:',logType.TITLE)
req = urllib2.Request(url,headers=header_dict)
for header in req.headers:
    log_utils.WriteLog('\t%s:%s' % (header, req.headers[header]), logType.RESULT)

log_utils.WriteLog('response-headers:',logType.TITLE)
try:
    res_data = urllib2.urlopen(req)
except urllib2.URLError as e:
    log_utils.WriteLog(e, logType.ERROR)
    sys.exit()
else:
    for header in res_data.headers:
        log_utils.WriteLog('\t%s:%s' % (header,res_data.headers[header]), logType.RESULT)
    res = res_data.read()

    log_utils.WriteLog('result for current request:',logType.TITLE)
    log_utils.WriteLog(res.strip().replace("\n",""),logType.RESULT)
    log_utils.WriteLog()

#print res