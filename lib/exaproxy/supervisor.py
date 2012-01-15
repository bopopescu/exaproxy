#!/usr/bin/env python
# encoding: utf-8
"""
supervisor.py

Created by Thomas Mangin on 2011-11-29.
Copyright (c) 2011 Exa Networks. All rights reserved.
"""

import os
import signal
from Queue import Queue

from .util.pid import PID
from .util.daemon import Daemon

from .classify.manager import WorkerManager
from .content.manager import ContentManager
from .client.manager import ClientManager
from .network.server import Server

from .reactor import Reactor


from .util.logger import logger

from .configuration import configuration

class Supervisor(object):
	# import os
	# clear = [hex(ord(c)) for c in os.popen('clear').read()]
	clear = ''.join([chr(int(c,16)) for c in ['0x1b', '0x5b', '0x48', '0x1b', '0x5b', '0x32', '0x4a']])

	def __init__ (self):
		self.pid = PID(configuration.PID)
		self.daemon = Daemon(configuration.DAEMONIZE,configuration.USER)

		# XXX : Should manager and Download moved into server ?
		self.manager = WorkerManager(configuration.PROGRAM)
		self.content = ContentManager(configuration.HTML)
		self.client = ClientManager()
		self.server = Server()

		self.reactor = Reactor(self.server, self.manager, self.content, self.client)

		self._shutdown = False
		self._reload = False

		signal.signal(signal.SIGTERM, self.sigterm)
		signal.signal(signal.SIGHUP, self.sighup)
		signal.signal(signal.SIGALRM, self.sigalrm)

		self.increase_spawn_limit = False

		
	def sigterm (self,signum, frame):
		logger.info('supervisor','SIG TERM received')
		self._shutdown = True

	def sighup (self,signum, frame):
		logger.info('supervisor','SIG HUP received')
		self._reload = True

	def sigalrm (self,signum, frame):
		logger.info('supervisor','SIG ALRM received')
		self.increase_spawn_limit = True

	def run (self):
		if self.daemon.drop_privileges():
			logger.warning('supervisor','Could not drop privileges to \'%s\' refusing to run as root' % self.daemon.user)
			logger.warning('supervisor','Set the environmemnt value USER to change the unprivileged user')
			return

		self.initialise()

		while True:
			try:
				if self._shutdown:
					self._shutdown = False
					self.shutdown()
					break
				elif self._reload and reload_completed:
					self._reload = False
					self.reload()

				if self.increase_spawn_limit:
					if self.manager.low == self.manager.high: self.manager.high += 1
					self.manager.low = min(self.manager.high,self.manager.low+1)
					self.increase_spawn_limit = False

				# make sure we have enough workers
				self.manager.provision()
				# check for IO change with select
				self.reactor.run(2)

				# Quit on problems which can not be fixed (like running out of file descriptor)
				self._shutdown = not self.reactor.running

			except KeyboardInterrupt:
				logger.info('supervisor','^C received')
				self._shutdown = True

			# XXX: need to handle errors from select()

#			finally:
#				from leak import objgraph
#				print objgraph.show_most_common_types(limit=20)
#				import random
#				obj = objgraph.by_type('ReceivedRoute')[random.randint(0,2000)]
#				objgraph.show_backrefs([obj], max_depth=10)

	def initialise (self):
		self.daemon.daemonise()
		self.pid.save()
		# start our threads
		self.manager.provision()

		# only start listening once we know we were able to fork our worker processes
		self.server.listen('0.0.0.0', 3128, 5, 200)

	def shutdown (self):
		"""terminate all the current BGP connections"""
		logger.info('supervisor','Performing shutdown')
		self.server.stop()   # accept no new connections
		self.manager.stop()  # shut down redirector children
		self.content.stop() # stop downloading data
		self.client.stop() # close client connections
		self.pid.remove()

	def reload (self):
		logger.info('supervisor','Performing reload of exaproxy %s' % configuration.VERSION ,'supervisor')
		self.manager.respawn()
