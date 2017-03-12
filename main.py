#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, hashlib, os, random, urllib, urllib2
from datetime import *
# from PIL import Image
import json
import logging

logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
    datefmt='%a, %d %b %Y %H:%M:%S',\
    filename='myapp.log',\
    filemode='w')

class APIClient(object):
    def http_request(self, url, paramDict):
        post_content = ''
        for key in paramDict:
            post_content = post_content + '%s=%s&' % (key, paramDict[key])
        post_content = post_content[0:-1]
        # print post_content
        req = urllib2.Request(url, data=post_content)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        response = opener.open(req, post_content)
        return response.read()

    def http_upload_image(self, url, paramKeys, paramDict, filebytes):
        timestr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        boundary = '------------' + hashlib.md5(timestr).hexdigest().lower()
        boundarystr = '\r\n--%s\r\n' % (boundary)

        bs = b''
        for key in paramKeys:
            bs = bs + boundarystr.encode('ascii')
            param = "Content-Disposition: form-data; name=\"%s\"\r\n\r\n%s" % (key, paramDict[key])
            # print param
            bs = bs + param.encode('utf8')
        bs = bs + boundarystr.encode('ascii')

        header = 'Content-Disposition: form-data; name=\"image\"; filename=\"%s\"\r\nContent-Type: image/gif\r\n\r\n' % (
        'sample')
        bs = bs + header.encode('utf8')

        bs = bs + filebytes
        tailer = '\r\n--%s--\r\n' % (boundary)
        bs = bs + tailer.encode('ascii')

        import requests
        headers = {'Content-Type': 'multipart/form-data; boundary=%s' % boundary,
                   'Connection': 'Keep-Alive',
                   'Expect': '100-continue',
                   }
        response = requests.post(url, params='', data=bs, headers=headers)
        return response.text


def arguments_to_dict(args):
    argDict = {}
    if args is None:
        return argDict

    count = len(args)
    if count <= 1:
        print 'exit:need arguments.'
        return argDict

    for i in [1, count - 1]:
        pair = args[i].split('=')
        if len(pair) < 2:
            continue
        else:
            argDict[pair[0]] = pair[1]

    return argDict

nCount = 0
nSuccess = 0
nFailed = 0

if __name__ == '__main__':
    try:
        pid = os.fork()
        if pid > 0:
            print("pid: %s" % (pid, ))
            sys.exit(0)
    except OSError, e:
        print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    client = APIClient()
    paramDict = {}
    result = ''

    paramDict['username'] = "walt_y"
    paramDict['password'] = "Ab123145"
    paramDict['typeid'] = "3040"
    paramDict['timeout'] = "90"
    paramDict['softid'] = "59285"
    paramDict['softkey'] = "78170d4b372d4cc2baf25abd816aff60"
    paramKeys = ['username',
                 'password',
                 'typeid',
                 'timeout',
                 'softid',
                 'softkey'
                 ]

    dirs = os.listdir("images")
    # print ("File Count: %d" % (len[dirs]))

    for file in dirs:
        nCount += 1
        filebytes = open("images/" + file, "rb").read()

        # print "Doing " + file
        result = client.http_upload_image("http://api.ysdm.net/create.json", paramKeys, paramDict, filebytes)
        # print result
        jObj = json.loads(result)
        retCode = jObj["Result"]

        if (str(retCode+".jpg").lower() == file.lower()):
            nSuccess += 1
            logging.info("NO %d %s ==> %s" % (nCount, file.lower(), str(retCode).lower()))
        else:
            nFailed += 1
            logging.info("NO %d %s ==> %s" % (nCount, file.lower(), str(retCode).lower()))

        if (len(file) > 8):
            os.rename("images/" + file, "images/" + retCode+".jpg")
            logging.info("NO %d %s ==> %s" % (nCount, file.lower(), str(retCode).lower()))

        if (nCount % 50 == 0):
            logging.info("NO %d %s ==> %s" % (nCount, file.lower(), str(retCode).lower()))


    logging.info("Done All: %d Success: %d Failed: %d" % (nCount, nSuccess, nFailed))