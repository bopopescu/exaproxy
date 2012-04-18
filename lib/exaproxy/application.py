# encoding: utf-8
"""
proxy.py

Created by Thomas Mangin on 2011-11-29.
Copyright (c) 2011 Exa Networks. All rights reserved.
"""

import sys
from leak import objgraph

def version_warning ():
	sys.stdout.write('\n')
	sys.stdout.write('************ WARNING *** WARNING *** WARNING *** WARNING *********\n')
	sys.stdout.write('*                                                                *\n')
	sys.stdout.write('* This program is only supported on Python version 2.6 or 2.7.   *\n')
	sys.stdout.write('* Please consider upgrading to the latest 2.x stable realease.   *\n')
	sys.stdout.write('*                                                                *\n')
	sys.stdout.write('************ WARNING *** WARNING *** WARNING *** WARNING *********\n')
	sys.stdout.write('\n')

def help ():
	sys.stdout.write('usage:\n exaproxy [options]\n')
	sys.stdout.write('\n')
	sys.stdout.write('  -h, --help      : this help\n')
	sys.stdout.write('  -c, --conf-file : configuration file to use (ini format)\n')
	sys.stdout.write('  -i, --ini       : display the configuration using the ini format\n')
	sys.stdout.write('  -e, --env       : display the configuration using the env format\n')
	sys.stdout.write(' -di, --diff-ini  : display non-default configurations values using the ini format\n')
	sys.stdout.write(' -de, --diff-env  : display non-default configurations values using the env format\n')
	sys.stdout.write('  -d, --debug     : shortcut to turn on all subsystems debugging to LOG_DEBUG\n')
	sys.stdout.write('  -p, --pdb       : on logging of serious errors start the python debugger\n')
	sys.stdout.write('  -m, --memory    : display memory usage information on exit\n')

	sys.stdout.write('\n')
	sys.stdout.write('ExaProxy will automatically look for its configuration file (in windows ini format)\n')
	sys.stdout.write(' - in the etc/exaproxy folder located within the extracted tar.gz \n')
	sys.stdout.write(' - in /etc/exaproxy/exaproxy.conf\n')
	sys.stdout.write('\n')
	sys.stdout.write('Every configuration value has a sensible built-in default\n')
	sys.stdout.write('\n')
	sys.stdout.write('Individual configuration options can be set using environment variables, such as :\n')
	sys.stdout.write('   > env exaproxy.dns.timeout=20 ./sbin/exaproxy\n')
	sys.stdout.write('or > env exaproxy_dns_timeout=20 ./sbin/exaproxy\n')
	sys.stdout.write('or > export exaproxy_dns_timeout=20; ./sbin/exaproxy\n')
	sys.stdout.write('\n')
	sys.stdout.write('Multiple environment values can be set\n')
	sys.stdout.write('and the order of preference is :\n')
	sys.stdout.write(' - 1 : command line env value using dot separated notation\n')
	sys.stdout.write(' - 2 : exported value from the shell using dot separated notation\n')
	sys.stdout.write(' - 3 : command line env value using underscore separated notation\n')
	sys.stdout.write(' - 4 : exported value from the shell using underscore separated notation\n')
	sys.stdout.write(' - 5 : the value in the ini configuration file\n')
	sys.stdout.write('\n')
	sys.stdout.write('Valid configuration options are :\n')
	sys.stdout.write('\n')
	for line in default():
			sys.stdout.write(' - %s\n' % line)
	sys.stdout.write('\n')

def __exit(memory,code):
	if memory:
		print "memory utilisation"
		print
		print objgraph.show_most_common_types(limit=20)
		print
		print
		print "generating memory utilisation graph"
		print
		obj = objgraph.by_type('Supervisor')
		objgraph.show_backrefs([obj], max_depth=10)
	sys.exit(code)

if __name__ == '__main__':
	main = int(sys.version[0])
	secondary = int(sys.version[2])

	if main != 2 or secondary < 4:
		sys.exit('This program can not work (is not tested) with your python version (< 2.4 or >= 3.0)')

	if main == 2 and secondary == 4:
		version_warning()

	from exaproxy.configuration import ConfigurationError,load,ini,env,default

	debug = False
	pdb = False
	memory = False
	next = ''
	arguments = {
		'configuration' : '',
	}

	for arg in sys.argv[1:]:
		if next:
			arguments[next] = arg
			next = ''
			continue
		if arg in ['-c','--conf-file']:
			next = 'configuration'

	try:
		configuration = load(arguments['configuration'])
	except ConfigurationError,e:
		print >> sys.stderr, 'configuration issue,', str(e)
		sys.exit(1)

	from exaproxy.util.log import Logger
	log = Logger('supervisor', configuration.log.supervisor)

	for arg in sys.argv[1:]:
		if arg in ['--',]:
			break
		if arg in ['-h','--help']:
			help()
			sys.exit(0)
		if arg in ['-i','--ini']:
			ini()
			sys.exit(0)
		if arg in ['-e','--env']:
			env()
			sys.exit(0)
		if arg in ['-di','--diff-ini']:
			ini(True)
			sys.exit(0)
		if arg in ['-de','--diff-env']:
			env(True)
			sys.exit(0)
		if arg in ['-d','--debug']:
			debug = True
		if arg in ['-p','--pdb']:
			pdb = True
			# The following may fail on old version of python
			os.environ['PDB'] = 'true'
		if arg in ['-m','--memory']:
			memory = True

	from exaproxy.supervisor import Supervisor

	if not configuration.profile.enable:
		Supervisor(debug,pdb).run()
		__exit(memory,0)

	try:
		import cProfile as profile
	except:
		import profile

	if not configuration.profile.destination or configuration.profile.destination == 'stdout':
		profile.run('Supervisor().run()')
		__exit(memory,0)

	notice = ''
	if os.path.isdir(configuration.profile.destination):
		notice = 'profile can not use this filename as outpout, it is not a directory (%s)' % profiled
	if os.path.exists(configuration.profile.destination):
		notice = 'profile can not use this filename as outpout, it already exists (%s)' % profiled

	if not notice:
		log.debug('profiling ....')
		profile.run('main()',filename=configuration.profile.destination)
	else:
		log.debug("-"*len(notice))
		log.debug(notice)
		log.debug("-"*len(notice))
		main()
	__exit(memory,0)
