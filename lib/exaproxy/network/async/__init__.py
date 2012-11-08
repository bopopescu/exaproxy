import select

from exaproxy.util.log.logger import Logger
from exaproxy.configuration import load

configuration = load()
log = Logger('supervisor', configuration.log.supervisor)

def Poller (configuration):
	reactor = configuration.reactor
	timeout = configuration.speed
	if reactor not in ('epoll','select'):
		log.warning('unknown reactor %s' % reactor)
	if reactor == 'epoll' and hasattr(select, 'epoll'):
		from epoll import EPoller as Poller
		return Poller(timeout)
	else:
		from selectpoll import SelectPoller as Poller
		return Poller(timeout)
