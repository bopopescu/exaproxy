# encoding: utf-8
"""
configuration.py

Created by Thomas Mangin on 2011-11-29.
Copyright (c) 2011-2013  Exa Networks. All rights reserved.
"""

# NOTE: reloading mid-program not possible

import os
import sys
import logging
import pwd

_application = None
_config = None
_defaults = None

class ConfigurationError (Exception):
	pass

_syslog_name_value = {
	'CRITICAL'     : logging.CRITICAL,
	'ERROR'        : logging.ERROR,
	'WARNING'      : logging.WARNING,
	'INFO'         : logging.INFO,
	'DEBUG'        : logging.DEBUG,
}

_syslog_value_name = {
	logging.CRITICAL   : 'CRITICAL',
	logging.ERROR      : 'ERROR',
	logging.WARNING    : 'WARNING',
	logging.INFO       : 'INFO',
	logging.DEBUG      : 'DEBUG',
}



class NoneDict (dict):
	def __getitem__ (self,name):
		return None
nonedict = NoneDict()

class value (object):
	location = os.path.normpath(sys.argv[0]) if sys.argv[0].startswith('/') else os.path.normpath(os.path.join(os.getcwd(),sys.argv[0]))

	@staticmethod
	def root (path):
		roots = value.location.split(os.sep)
		location = []
		for index in range(len(roots)-1,-1,-1):
			if roots[index] in ('lib','bin'):
				if index:
					location = roots[:index]
				break
		root = os.path.join(*location)
		paths = [
			os.path.normpath(os.path.join(os.path.join(os.sep,root,path))),
			os.path.normpath(os.path.expanduser(value.unquote(path))),
			os.path.normpath(os.path.join('/',path)),
			os.path.normpath(os.path.join('/','usr',path)),
		]
		return paths

	@staticmethod
	def integer (_):
		value = int(_)
		if value <= 0:
			raise TypeError('the value must be positive')
		return value

	@staticmethod
	def lowunquote (_):
		return _.strip().strip('\'"').lower()

	@staticmethod
	def unquote (_):
		return _.strip().strip('\'"')

	@staticmethod
	def quote (_):
		return "'%s'" % str(_)

	@staticmethod
	def nop (_):
		return _

	@staticmethod
	def boolean (_):
		return _.lower() in ('1','yes','on','enable','true')

	@staticmethod
	def methods (_):
		return _.upper().split()

	@staticmethod
	def list (_):
		return "'%s'" % ' '.join(_)

	@staticmethod
	def lower (_):
		return str(_).lower()

	@staticmethod
	def user (_):
		try:
			pwd.getpwnam(_)
			# uid = answer[2]
		except KeyError:
			raise TypeError('user %s is not found on this system' % _)
		return _

	@staticmethod
	def folder(path):
		paths = value.root(path)
		options = [path for path in paths if os.path.exists(path)]
		if not options: raise TypeError('%s does not exists' % path)
		first = options[0]
		if not first: raise TypeError('%s does not exists' % first)
		return first

	@staticmethod
	def path (path):
		split = sys.argv[0].split('lib/%s' % _application)
		if len(split) > 1:
			prefix = os.sep.join(split[:1])
			if prefix and path.startswith(prefix):
				path = path[len(prefix):]
		home = os.path.expanduser('~')
		if path.startswith(home):
			return "'~%s'" % path[len(home):]
		return "'%s'" % path

	@staticmethod
	def conf(path):
		first = value.folder(path)
		if not os.path.isfile(first): raise TypeError('%s is not a file' % path)
		return first

	@staticmethod
	def resolver(path):
		global _application
		paths = value.root('etc/%s/dns/resolv.conf' % _application)
		paths.append(os.path.normpath(os.path.join('/','etc','resolv.conf')))
		for resolver in paths:
			if os.path.exists(resolver):
				with open(resolver) as r:
					if 'nameserver' in (line.strip().split(None,1)[0].lower() for line in r.readlines()):
						return resolver
		raise TypeError('resolv.conf can not be found (are you using DHCP without any network setup ?)')

	@staticmethod
	def exe (path):
		first = value.conf(path)
		if not os.access(first, os.X_OK): raise TypeError('%s is not an executable' % first)
		return first

	# @staticmethod
	# def syslog (path):
	# 	path = value.unquote(path)
	# 	if path in ('stdout','stderr'):
	# 		return path
	# 	if path.startswith('host:'):
	# 		return path
	# 	return path

	@staticmethod
	def redirector (name):
		if name == 'url' or name.startswith('icap://'):
			return name
		raise TypeError('invalid redirector protocol %s, options are url or header' % name)

	@staticmethod
	def syslog_int (log):
		if log not in _syslog_name_value:
			raise TypeError('invalid log level %s' % log)
		return _syslog_name_value[log]

	@staticmethod
	def syslog_value (log):
		if log not in _syslog_name_value:
			raise TypeError('invalid log level %s' % log)
		return _syslog_name_value[log]

	@staticmethod
	def syslog_name (log):
		if log not in _syslog_value_name:
			raise TypeError('invalid log level %s' % log)
		return _syslog_value_name[log]


import ConfigParser

class Store (dict):
	def __getitem__ (self,key):
		return dict.__getitem__(self,key.replace('_','-'))

	def __setitem__ (self,key,value):
		return dict.__setitem__(self,key.replace('_','-'),value)

	def __getattr__ (self,key):
		return dict.__getitem__(self,key.replace('_','-'))

	def __setattr__ (self,key,value):
		return dict.__setitem__(self,key.replace('_','-'),value)


def _configuration (conf):
	location = os.path.join(os.sep,*os.path.join(value.location.split(os.sep)))
	while location and location != '/':
		location, directory = os.path.split(location)
		if directory in ('lib','bin'):
			break

	_conf_paths = []
	if conf:
		_conf_paths.append(os.path.abspath(os.path.normpath(conf)))
	if location:
		_conf_paths.append(os.path.normpath(os.path.join(location,'etc',_application,'%s.conf' % _application)))
	_conf_paths.append(os.path.normpath(os.path.join('/','etc',_application,'%s.conf' % _application)))
	_conf_paths.append(os.path.normpath(os.path.join('/','usr','etc',_application,'%s.conf' % _application)))

	configuration = Store()
	ini = ConfigParser.ConfigParser()

	ini_files = [path for path in _conf_paths if os.path.exists(path)]
	if ini_files:
		ini.read(ini_files[0])

	for section in _defaults:
		default = _defaults[section]

		for option in default:
			convert = default[option][0]
			try:
				proxy_section = '%s.%s' % (_application,section)
				env_name = '%s.%s' % (proxy_section,option)
				rep_name = env_name.replace('.','_')

				if env_name in os.environ:
					conf = os.environ.get(env_name)
				elif rep_name in os.environ:
					conf = os.environ.get(rep_name)
				else:
					try:
						# raise and set the default
						conf = value.unquote(ini.get(section,option,nonedict))
					except (ConfigParser.NoSectionError,ConfigParser.NoOptionError):
						# raise and set the default
						conf = value.unquote(ini.get(proxy_section,option,nonedict))
					# name without an = or : in the configuration and no value
					if conf == None:
						conf = default[option][2]
			except (ConfigParser.NoSectionError,ConfigParser.NoOptionError):
				conf = default[option][2]
			try:
				configuration.setdefault(section,Store())[option] = convert(conf)
			except TypeError,error:
				raise ConfigurationError('invalid value for %s.%s : %s (%s)' % (section,option,conf,str(error)))

	return configuration

def load (application=None,defaults=None,conf=None):
	global _application
	global _defaults
	global _config
	if _config:
		return _config
	if conf is None:
		raise RuntimeError('You can not have an import using load() before main() initialised it')
	_application = application
	_defaults = defaults
	_config = _configuration(conf)
	return _config

def default ():
	for section in sorted(_defaults):
		for option in sorted(_defaults[section]):
			values = _defaults[section][option]
			default = "'%s'" % values[2] if values[1] in (value.list,value.path,value.quote,value.unquote) else values[2]
			yield '%s.%s.%s %s: %s. default (%s)' % (_application,section,option,' '*(20-len(section)-len(option)),values[3],default)

def ini (diff=False):
	for section in sorted(_config):
		if section in ('proxy','debug'):
			continue
		header = '\n[%s]' % section
		for k in sorted(_config[section]):
			v = _config[section][k]
			if diff and _defaults[section][k][0](_defaults[section][k][2]) == v:
				continue
			if header:
				print header
				header = ''
			print '%s = %s' % (k,_defaults[section][k][1](v))

def env (diff=False):
	print
	for section,values in _config.items():
		if section in ('proxy','debug'):
			continue
		for k,v in values.items():
			if diff and _defaults[section][k][0](_defaults[section][k][2]) == v:
				continue
			if _defaults[section][k][1] == value.quote:
				print "%s.%s.%s='%s'" % (_application,section,k,v)
				continue
			print "%s.%s.%s=%s" % (_application,section,k,_defaults[section][k][1](v))
