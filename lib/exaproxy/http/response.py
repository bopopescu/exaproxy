#!/usr/bin/env python
# encoding: utf-8
"""
http.py

Created by Thomas Mangin on 2011-12-02.
Copyright (c) 2011 Exa Networks. All rights reserved.
"""

import sys
import time
from exaproxy.configuration import configuration
from exaproxy.util.version import version


def file_header(code, size, message):
	date = time.strftime('%c %Z')

	return """HTTP/1.1 %s OK
Date: %s
Server: exaproxy/%s (%s)
Content-Length: %d
Proxy-Connection: close
Connection: close
Content-Type: text/html
Cache-control: private
Pragma: no-cache

""" % (str(code), date, str(version), str(sys.platform), size)




def http (code,message):
	return """\
HTTP/1.1 %s OK
Date: Fri, 02 Dec 2011 09:29:44 GMT
Server: exaproxy/%s (%s)
Content-Length: %d
Proxy-Connection: close
Connection: close
Content-Type: text/html
Cache-control: private
Pragma: no-cache

%s""" % (str(code),str(version),sys.platform,len(message),message)

image = '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\n'

def html (title,header,color='#FF0000',menu='',text='',):
	if header: header += '<br/>'
	return """\
<html>
	<head>
		<title>%s</title>
		<meta http-equiv="cache-control" content="no-cache">
	</head>
	<body leftmargin="0" topmargin="0" rightmargin="0" bgcolor="#FFFFFF" text="#000000" link="#0000FF" alink="#0000FF" vlink="#0000FF">
		<center>
			<div style="padding:15; color: #FFFFFF; background: %s; font-size: 40px; font-family: verdana,sans-serif,arial; font-weight: bold; border-bottom: solid 1px #A0A0A0;">
				%s
				<img src="data:image/png;base64,%s"/>
			</div>
		</center>
		<br/>
		%s
		<br/>
		<br/>
		%s
		<br/>
		<br/>
	</body>
</html>

""" % (title,color,header,image,menu,text)


