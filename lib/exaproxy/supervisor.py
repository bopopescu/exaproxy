# encoding: utf-8
"""
supervisor.py

Created by Thomas Mangin on 2011-11-29.
Copyright (c) 2011-2013  Exa Networks. All rights reserved.
"""

import os
import sys
import signal

from .util.pid import PID
from .util.daemon import Daemon

from .reactor.redirector.manager import RedirectorManager
from .reactor.content.manager import ContentManager
from .reactor.client.manager import ClientManager
from .reactor.resolver.manager import ResolverManager
from .network.async import Poller
from .network.server import Server
from .html.page import Page
from .monitor import Monitor

from .reactor import Reactor

from .configuration import load
from exaproxy.util.log.logger import Logger
from exaproxy.util.log.writer import SysLogWriter
from exaproxy.util.log.writer import UsageWriter

class Supervisor(object):
	alarm_time = 1             # how often we record history data
	increase_frequency = 5     # multiple of alarm_time for when we add workers
	decrease_frequency = 60    # multiple of alarm_time for when we remove workers
	saturation_frequency = 20  # multiple of alarm time for when we report connection saturation

	# import os
	# clear = [hex(ord(c)) for c in os.popen('clear').read()]
	# clear = ''.join([chr(int(c,16)) for c in ['0x1b', '0x5b', '0x48', '0x1b', '0x5b', '0x32', '0x4a']])

	def __init__ (self,configuration):
		configuration = load()
		self.configuration = configuration

		# Only here so the introspection code can find them
		self.log = Logger('supervisor', configuration.log.supervisor)
		self.log.error('Starting exaproxy version %s' % configuration.proxy.version)

		if configuration.daemon.reactor == 'epoll' and not sys.platform.startswith('linux'):
			print >> sys.stderr
			print >> sys.stderr, 'warning: exaproxy.daemon.reactor can only be epoll on Linux, changing the reactor to select'
			configuration.daemon.reactor = 'select'

		if configuration.daemon.reactor == 'select' and configuration.daemon.filemax + configuration.redirector.maximum > 1000:
			print >> sys.stderr
			print >> sys.stderr, 'error: Please change exaproxy.daemon.filemax to something lower than %d' % configuration.daemon.filemax
			print >> sys.stderr, 'error: Otherwise it is likely that under load, the program will crash.'
			print >> sys.stderr, 'error: (OS limit is 1024 and exaproxy requires some filedescriptors internally too.)'
			sys.exit(1)

		self.signal_log = Logger('signal', configuration.log.signal)
		self.log_writer = SysLogWriter('log', configuration.log.destination, configuration.log.enable, level=configuration.log.level)
		self.usage_writer = UsageWriter('usage', configuration.usage.destination, configuration.usage.enable)

		self.log_writer.setIdentifier(configuration.daemon.identifier)
		#self.usage_writer.setIdentifier(configuration.daemon.identifier)

		if configuration.debug.log:
			self.log_writer.toggleDebug()
			self.usage_writer.toggleDebug()

		self.log.info('starting %s' % sys.argv[0])
		self.log.info('python version %s' % sys.version.replace(os.linesep,' '))

		self.pid = PID(self.configuration)

		self.daemon = Daemon(self.configuration)
		self.poller = Poller(self.configuration.daemon)

		# We want to ensure that we will not try to open too many files at once
		max_admin_clients = 10
		max_resolver_clients = 10
		max_proxy_clients = (self.daemon.file_limit - max_admin_clients - max_resolver_clients)/2

		self.poller.setupRead('read_proxy')           # Listening proxy sockets
		self.poller.setupRead('read_web')             # Listening webserver sockets
		self.poller.setupRead('read_workers')         # Pipes carrying responses from the child processes
		self.poller.setupRead('read_resolver')        # Sockets currently listening for DNS responses

		self.poller.setupRead('read_client')          # Active clients
		self.poller.setupRead('opening_client')       # Clients we have not yet read a request from
		self.poller.setupWrite('write_client')        # Active clients with buffered data to send
		self.poller.setupWrite('write_resolver')      # Active DNS requests with buffered data to send

		self.poller.setupRead('read_download')        # Established connections
		self.poller.setupWrite('write_download')      # Established connections we have buffered data to send to
		self.poller.setupWrite('opening_download')    # Opening connections

		self.monitor = Monitor(self)
		self.page = Page(self)
		self.manager = RedirectorManager(
			self.configuration,
			self.poller,
		)
		self.content = ContentManager(self.poller, self.configuration.web.html, self.page, configuration)
		self.client = ClientManager(self.poller, configuration)
		self.resolver = ResolverManager(self.poller, self.configuration, max_resolver_clients)
		self.proxy = Server('http proxy',self.poller,'read_proxy', max_proxy_clients)
		self.web = Server('web server',self.poller,'read_web', max_admin_clients)

		self.reactor = Reactor(self.configuration, self.web, self.proxy, self.manager, self.content, self.client, self.resolver, self.log_writer, self.usage_writer, self.poller)

		self._shutdown = False
		self._reload = False
		self._toggle_debug = False
		self._decrease_spawn_limit = 0
		self._increase_spawn_limit = 0
		self._refork = False
		self._pdb = False

		signal.signal(signal.SIGTERM, self.sigterm)
		signal.signal(signal.SIGHUP, self.sighup)
		signal.signal(signal.SIGALRM, self.sigalrm)
		signal.signal(signal.SIGUSR1, self.sigusr1)
		signal.signal(signal.SIGUSR2, self.sigusr2)
		#signal.signal(signal.SIGTRAP, self.sigtrap)
		#signal.signal(signal.SIGABRT, self.sigabrt)

		# make sure we always have data in history, here as record() requires self to be partially initialised to run
		self.monitor.record()

	def sigterm (self,signum, frame):
		self.signal_log.info('SIG TERM received, shutdown request')
		if os.environ.get('PDB',False):
			self._pdb = True
		else:
			self._shutdown = True

	def sighup (self,signum, frame):
		self.signal_log.info('SIG HUP received, reload request')
		self._reload = True

	def sigtrap (self,signum, frame):
		self.signal_log.info('SIG TRAP received, toggle debug')
		self._toggle_debug = True

	def sigusr1 (self,signum, frame):
		self.signal_log.info('SIG USR1 received, decrease worker number')
		self._decrease_spawn_limit += 1

	def sigusr2 (self,signum, frame):
		self.signal_log.info('SIG USR2 received, increase worker number')
		self._increase_spawn_limit += 1

	def sigabrt (self,signum, frame):
		self.signal_log.info('SIG INFO received, refork request')
		self._refork = True

	def sigalrm (self,signum, frame):
		self.signal_log.debug('SIG ALRM received, timed actions')
		self.reactor.running = False
		signal.alarm(self.alarm_time)

	def run (self):
		if self.daemon.drop_privileges():
			self.log.stdout('Could not drop privileges to \'%s\'. Refusing to run as root' % self.daemon.user)
			self.log.stdout('Set the environment value USER to change the unprivileged user')
			return

		ok = self.initialise()
		if not ok:
			self._shutdown = True

		signal.alarm(self.alarm_time)

		count_increase = 0
		count_decrease = 0
		count_saturation = 0

		while True:
			count_increase = (count_increase + 1) % self.increase_frequency
			count_decrease = (count_decrease + 1) % self.decrease_frequency
			count_saturation = (count_saturation + 1) % self.saturation_frequency

			try:
				if self._toggle_debug:
					self._toggle_debug = False
					self.log_writer.toggleDebug()

				if self._shutdown:
					self._shutdown = False
					self.shutdown()
					break
				elif self._reload:
					self._reload = False
					self.reload()
				elif self._refork:
					self._refork = False
					self.signal_log.warning('refork not implemented')
					# stop listening to new connections
					# refork the program (as we have been updated)
					# just handle current open connection

				if self._increase_spawn_limit:
					number = self._increase_spawn_limit
					self._increase_spawn_limit = 0
					self.manager.low += number
					self.manager.high = max(self.manager.low,self.manager.high)
					for _ in range(number):
						self.manager.increase()

				if self._decrease_spawn_limit:
					number = self._decrease_spawn_limit
					self._decrease_spawn_limit = 0
					self.manager.high = max(1,self.manager.high-number)
					self.manager.low = min(self.manager.high,self.manager.low)
					for _ in range(number):
						self.manager.decrease()

				if self._pdb:
					self._pdb = False
					import pdb
					pdb.set_trace()

				# check for IO change with select
				self.reactor.run()

				# Quit on problems which can not be fixed (like running out of file descriptor)
				#self._shutdown = not self.reactor.running

				# save our monitoring stats
				self.monitor.record()
				# make sure we have enough workers
				if count_increase == 0:
					self.manager.provision()
				# and every so often remove useless workers
				if count_decrease == 0:
					self.manager.deprovision()

				# report if we saw too many connections
				if count_saturation == 0:
					self.proxy.saturation()
					self.web.saturation()

			except KeyboardInterrupt:
				self.log.info('^C received')
				self._shutdown = True
			except OSError,e:
				# XXX: we need to stop listening and re-fork ourselves
				if e.errno == 24:  # Too many open files
					self.log.critical('Too many opened files, shutting down')
					self._shutdown = True
				else:
					# Not sure we can get here, let the user know by raising
					raise

			finally:
				pass
#				try:
#					from exaproxy.leak import objgraph
#					if objgraph:
#						count += 1
#						if count >= 30:
#							print "*"*10, time.strftime('%d-%m-%Y %H:%M:%S')
#							print objgraph.show_most_common_types(limit=20)
#							print "*"*10
#							print
#				except KeyboardInterrupt:
#					self.log.info('^C received')
#					self._shutdown = True

	def initialise (self):
		self.daemon.daemonise()
		self.pid.save()
		# start our threads
		self.manager.start()


		# only start listening once we know we were able to fork our worker processes
		tcp4 = self.configuration.tcp4
		tcp6 = self.configuration.tcp6

		ok = bool(tcp4.listen or tcp6.listen)
		if not ok:
			self.log.error('Not listening on IPv4 or IPv6.')

		if ok and tcp4.listen:
			s = self.proxy.listen(tcp4.host,tcp4.port, tcp4.timeout, tcp4.backlog)
			ok = bool(s)
			if not s:
				print >> sys.stderr, 'IPv4 proxy, unable to listen on %s:%s' % (tcp4.host,tcp4.port)
				self.log.error('IPv4 proxy, unable to listen on %s:%s' % (tcp4.host,tcp4.port))

		if ok and tcp6.listen:
			s = self.proxy.listen(tcp6.host,tcp6.port, tcp6.timeout, tcp6.backlog)
			ok = bool(s)
			if not s:
				print >> sys.stderr, 'IPv6 proxy, unable to listen on %s:%s' % (tcp6.host,tcp6.port)
				self.log.error('IPv6 proxy, unable to listen on %s:%s' % (tcp6.host,tcp6.port))


		if ok and self.configuration.web.enable:
			s = self.web.listen(self.configuration.web.host,self.configuration.web.port, 10, 10)
			if not s:
				print >> sys.stderr, 'internal web server, unable to listen on %s:%s' % (self.configuration.web.host, self.configuration.web.port)
				self.log.error('internal web server, unable to listen on %s:%s' % (self.configuration.web.host, self.configuration.web.port))
				ok = False

		return ok

	def shutdown (self):
		"""terminate all the current BGP connections"""
		self.log.info('Performing shutdown')
		try:
			self.web.stop()  # accept no new web connection
			self.proxy.stop()  # accept no new proxy connections
			self.manager.stop()  # shut down redirector children
			os.kill(os.getpid(),signal.SIGALRM)
			self.content.stop()  # stop downloading data
			self.client.stop()  # close client connections
			self.pid.remove()
		except KeyboardInterrupt:
			self.log.info('^C received while shutting down. Exiting immediately because you insisted.')
			sys.exit()

	def reload (self):
		self.log.info('Performing reload of exaproxy %s' % self.configuration.proxy.version ,'supervisor')
		self.manager.respawn()
