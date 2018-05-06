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
import time
from urlparse import urlparse
import io

URLPATTERN = '^(https?|ftp|file)://.+$'
URLLIST = []
ISPOST = False
POSTDATA = ''
OUTPUT_FILE = None
POST_FILE = None
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'
COOKIES = {}
COOKIEINFOPATH = 'cookies/cookieInfo.txt'
url = ''
batch = ''
output = ''
postFile = ''
isLogin = False
LOGINURL = ''

# 获取域名


def getDomain(url):
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain

# 加载cookies


def getCookieInfo():
    global COOKIES
    try:
        COOKIES = json.loads(open(COOKIEINFOPATH, 'r+').read())
    except IOError as e:
        log_utils.WriteLog(e, logType.ERROR)
        sys.exit()


def updateCookieInfo(domain, cookieInfo):
    try:
        cookieList = filter(
            lambda x: x['Domain'] == domain, COOKIES['Cookies'])
        if cookieList and len(cookieList) > 0:
            cookieList[0]['Cookie'] = cookieInfo
        else:
            new_cookieInfo = json.loads(
                '{"Domain":"%s", "Cookie":"%s"}' % (domain, cookieInfo))
            COOKIES['Cookies'].append(new_cookieInfo)
            file = open(COOKIEINFOPATH, 'w+')
            file.write(json.dumps(COOKIES))
            file.close()
    except IOError as e:
        log_utils.WriteLog(e, logType.ERROR)

# 构造请求头


def createRequestHeaders(url, isLogin):
    proto, rest = urllib.splittype(url)
    host, rest = urllib.splithost(rest)
    header_dict = {
        'Host': 'unkonw' if not host else host,
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/json'
    }
    if not isLogin:
        domain = getDomain(url)
        cookieList = filter(
            lambda x: x['Domain'] == domain, COOKIES['Cookies'])
        if cookieList and len(cookieList) > 0:
            header_dict['Cookie'] = cookieList[0]['Cookie']
    return header_dict


def invokeHttpRequest(url, data, isLogin):
    try:
        log_utils.WriteLog('current request url:%s' % (url), logType.TITLE)
        if re.match(URLPATTERN, url) is None:
            log_utils.WriteLog('ignored invalid url : %s' %
                               (url), logType.ERROR)
            return

        headers = createRequestHeaders(url, isLogin)
        req = urllib2.Request(url, headers=headers, data=data)

        startTime = time.time()
        res_data = urllib2.urlopen(req)
        endTime = time.time()

    except urllib2.URLError as e:
        log_utils.WriteLog(e, logType.ERROR)
        log_utils.WriteLog()
    else:
        log_utils.WriteLog('http status:%s  spend time:%s s' %
                           (res_data.code, endTime-startTime), logType.INFO)
        log_utils.WriteLog('parameters:%s' % (data), logType.TITLE)
        log_utils.WriteLog('request-headers:', logType.TITLE)
        for header in req.headers:
            log_utils.WriteLog('\t%s:%s' %
                               (header, req.headers[header]), logType.WARN)
        log_utils.WriteLog('response-headers:', logType.TITLE)
        for header in res_data.headers:
            if isLogin and header.lower() == 'set-cookie':
                updateCookieInfo(getDomain(url),
                                 res_data.headers[header])
            log_utils.WriteLog('\t%s:%s' % (
                header, res_data.headers[header]), logType.WARN)

        res = res_data.read()
        log_utils.WriteLog('response:', logType.TITLE)
        log_utils.WriteLog(res.strip().replace("\n", ""), logType.RESULT)
        log_utils.WriteLog()


def getUrlList(filePath):
    global LOGINURL
    global URLLIST
    try:
        urlJson = json.loads(open(filePath, 'r').read())
        LOGINURL = urlJson['Login']
        for url in urlJson['UrlList']:
            URLLIST.append(url)
    except IOError as e:
        log_utils.WriteLog(e, logType.ERROR)
        sys.exit()


def startRequest(currentUrl, isLogin):
    if ISPOST:
        newPostData = filter(
            lambda x: x['API'] == currentUrl, POSTDATA['PostData'])
        if not newPostData or len(newPostData) <= 0:
            invokeHttpRequest(currentUrl, None, isLogin)
        else:
            for data in newPostData:
                invokeHttpRequest(currentUrl, data['Data'].encode(
                    'unicode-escape').decode('string-escape'), isLogin)
    else:
        invokeHttpRequest(currentUrl, None, isLogin)


# banner
f = Figlet()
print f.renderText('liushaoting')

# 参数管理
parser = argparse.ArgumentParser(description='Test For API')
parser.add_argument('-U', '--url', help=u'API的完整路径')
parser.add_argument(
    '-B', '--batch', help=u'批量请求多个接口，指定接口列表文件，当有[-U]命令时,此命令不生效')
parser.add_argument('-O', '--output', help=u'输出结果到哪个文件')
parser.add_argument(
    '-F', '--file', help=u'post请求所需的参数文件，当有这个文件的时候才进行post请求，如果没有则默认都是get请求')
parser.add_argument('-L', '--login', action="store_true",
                    help=u'标识当前请求为登陆请求，会自动保存会话信息')
args = parser.parse_args()

url = args.url
batch = args.batch
output = args.output
postFile = args.file
isLogin = args.login

# 判断URL是否存在
if not url and not batch:
    parser.print_help()
    sys.exit()
elif not url and batch:
    getUrlList(batch)
else:
    if isLogin:
        LOGINURL = url
    else:
        URLLIST.append(url)

# 加载cookie信息
getCookieInfo()

# 判断是否是POST请求，并判断post文件是否可以访问，可以则读取里面的参数
if postFile:
    ISPOST = True
    if not os.access(postFile, os.R_OK):
        log_utils.WriteLog(u'所提供的post文件不存在或不可访问', logType.ERROR)
        sys.exit()
    else:
        try:
            POST_FILE = open(postFile, 'r+')
            POSTDATA = json.loads(POST_FILE.read())
            POST_FILE.close()
        except IOError as e:
            log_utils.WriteLog(e, logType.ERROR)
            sys.exit()

# 判断是否要输出结果到其他文件
if output:
    output = 'output/'+output
    try:
        OUTPUT_FILE = open(output, 'a+')
        log_utils.STORAGETYPE = storageType.FILE
        log_utils.FILEPATH = output
    except IOError as e:
        log_utils.WriteLog(e, logType.ERROR)
        sys.exit()

if LOGINURL:
    startRequest(LOGINURL, True)

for currentUrl in URLLIST:
    startRequest(currentUrl, False)
#print res
