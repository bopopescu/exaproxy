#!/usr/bin/env python
# encoding: utf-8
"""
process.py

Created by Thomas Mangin on 2011-11-29.
Copyright (c) 2011 Exa Networks. All rights reserved.
"""

from threading import Thread
import subprocess
import errno

import os
import time
import socket

from Queue import Empty

from .http import HTTPParser,regex

from .logger import Logger
logger = Logger()

from .configuration import Configuration
configuration = Configuration()

class Worker (HTTPParser,Thread):
	
	# TODO : if the program is a function, fork and run :)
	
	def __init__ (self, name, request_box, program):
		self.wid = name                               # a unique name
		self.creation = time.time()                   # when the thread was created
		self.last_worked = self.creation              # when the thread last picked a task
		self.request_box = request_box                # queue with HTTP headers to process

		# XXX: all this could raise things
		r, w = os.pipe()                              # pipe for communication with the main thread
		self.response_box_write = os.fdopen(w,'w')    # results are written here
		self.response_box_read = os.fdopen(r,'r')     # read from the main thread

		self.program = program                        # the squid redirector program to fork 
		self.running = True                           # the thread is active
		Thread.__init__(self)

	def createProcess (self):
		try:
			process = subprocess.Popen([self.program,],
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				universal_newlines=True,
			)
			logger.worker('spawn process %s' % self.program, 'worker %d' % self.wid)
		except KeyboardInterrupt:
			process = None
		except (subprocess.CalledProcessError,OSError,ValueError):
			logger.worker('could not spawn process %s' % self.program, 'worker %d' % self.wid)
			process = None

		return process
	
	def _cleanup (self, process):
		logger.worker('terminating process', 'worker %d' % self.wid)
		# XXX: can raise
		self.response_box_read.close()
		try:
			process.terminate()
			process.wait()
		except OSError, e:
			# No such processs
			if e[0] != errno.ESRCH:
				logger.worker('PID %s died' % pid, 'worker %d' % self.wid)

	def resolveHost(self, host):
		# Do the hostname resolution before the backend check
		# We may block the page but filling the OS DNS cache can not harm :)
		try:
			#raise socket.error('UNCOMMENT TO TEST DNS RESOLUTION FAILURE')
			return socket.gethostbyname(host)
		except socket.error,e:
			return None

	def stop (self):
		self.running = False

	def _reply (self,cid,code,title,body):
		logger.worker(body, 'worker %d' % self.wid)
		self.response_box_write.write('%s %s %s %d %s\n' % (cid,'response',title.replace(' ','_'),code,body))
		self.response_box_write.flush()

	def run (self):
		if not self.running:
			logger.worker('can not start', 'worker %d' % self.wid)
			return

		logger.worker('starting', 'worker %d' % self.wid)
		process = self.createProcess()
		if not process:
			self.stop()

		while self.running:
			try:
				data = self.request_box.get(1)
				cid,peer,request = data
			except (ValueError, IndexError):
				logger.worker('received invalid message: %s' % data, 'worker %d' % self.wid)
				continue
			except Empty:
				continue

			logger.worker('some work came', 'worker %d' % self.wid)
			logger.worker('peer %s' % str(peer), 'worker %d' % self.wid)
			logger.worker('request %s' % ' '.join(request.split('\n',3)[:2]), 'worker %d' % self.wid)

			method, url, host, client = self.parseRequest(request)
			if method is None:
				self._reply(cid, 400, 'INVALID REQUEST','invalid request <!-- %s -->' % request)
				continue

			ip = self.resolveHost(host)
			if not ip:
				logger.worker('Could not resolve %s' % host, 'worker %d' % self.wid)
				self._reply(cid,503,'NO DNS','could not resolve DNS for %s' % host)
				continue

			squid = '%s %s - %s -' % (url,client,method)
			logger.worker('sending to classifier : [%s]' % squid, 'worker %d' % self.wid)
			try:
				process.stdin.write('%s%s' % (squid,os.linesep))
				process.stdin.flush()
				response = process.stdout.readline()
			except IOError,e:
				logger.worker('IO/Error when sending to process, %s' % str(e), 'worker %d' % self.wid)
				self._reply(cid,500,'Interal Problem','could get a classification for %s' % host)
				# XXX: Do something
				return

			logger.worker('received from classifier : [%s]' % response.strip(), 'worker %d' % self.wid)
			if response == '\n':
				response = host

			# prevent persistence : http://tools.ietf.org/html/rfc2616#section-8.1.2.1
			# XXX: We may have more than one Connection header : http://tools.ietf.org/html/rfc2616#section-14.10
			# XXX: We may need to remove every step-by-step http://tools.ietf.org/html/rfc2616#section-13.5.1
			# XXX: We NEED to add a Via field http://tools.ietf.org/html/rfc2616#section-14.45
			# XXX: We NEED to respect Keep-Alive rules http://tools.ietf.org/html/rfc2068#section-19.7.1
			# XXX: We may look at Max-Forwards
			# XXX: We need to reply to "Proxy-Connection: keep-alive", with "Proxy-Connection: close"
			# http://homepage.ntlworld.com./jonathan.deboynepollard/FGA/web-proxy-connection-header.html

			if regex.connection.match(request):
				request = re.sub('close',request)
			else:
				request = request.rstrip() + '\r\nConnection: Close\r\n\r\n'

			logger.worker('need to download data on %s at %s' % (host,ip), 'worker %d' % self.wid)
			self.response_box_write.write('%s %s %s %d %s\n' % (cid,'request',ip,80,request.replace('\n','\\n').replace('\r','\\r')))
			self.response_box_write.flush()
			##logger.worker('[%s %s %s %d %s]' % (cid,'request',ip,80,request), 'worker %d' % self.wid)
			self.last_worked = time.time()
			logger.worker('waiting for some work', 'worker %d' % self.wid)

		self._cleanup(process)
	
