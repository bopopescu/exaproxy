# Help #

(retake output, to show memory and identifier options)

```
»› ./sbin/exaproxy -h
usage:
 exaproxy [options]

  -h, --help      : this help
  -i, --ini       : display the configuration using the ini format
  -e, --env       : display the configuration using the env format
 -di, --diff-ini  : display non-default configurations values using the ini format
 -de, --diff-env  : display non-default configurations values using the env format
  -d, --debug     : shortcut to turn on all subsystems debugging to LOG_DEBUG

ExaProxy will automatically look for its configuration file (in windows ini format)
 - in the etc/exaproxy folder located within the extracted tar.gz 
 - in /etc/exaproxy/exaproxy.conf

Every configuration value has a sensible built-in default

Individual configuration options can be set using environment variables, such as :
   > env exaproxy.dns.timeout=20 ./sbin/exaproxy
or > env exaproxy_dns_timeout=20 ./sbin/exaproxy
or > export exaproxy_dns_timeout=20; ./sbin/exaproxy

Multiple environment values can be set
and the order of preference is :
 - 1 : command line env value using dot separated notation
 - 2 : exported value from the shell using dot separated notation
 - 3 : command line env value using underscore separated notation
 - 4 : exported value from the shell using underscore separated notation
 - 5 : the value in the ini configuration file

Valid configuration options are :

 - exaproxy.daemon.daemonize      : should we run in the background. default (false)
 - exaproxy.daemon.filemax        : the maximum number of open file descriptors, tcp connections and programs. default (10240)
 - exaproxy.daemon.pidfile        : where to save the pid if we manage it. default ('')
 - exaproxy.daemon.reactor        : what event mechanism to use (select/epoll). default ('epoll')
 - exaproxy.daemon.speed          : when waiting for connection how long are we sleeping for. default (2)
 - exaproxy.daemon.user           : user to run as. default ('nobody')
 - exaproxy.dns.definitions       : location of file defining dns query types. default ('etc/exaproxy/dns/types')
 - exaproxy.dns.expire            : maximum number of cached dns entries we will expire during each cleanup. default (200)
 - exaproxy.dns.resolver          : resolver file. default ('/etc/resolv.conf')
 - exaproxy.dns.timeout           : how long to wait for DNS replies. default (10)
 - exaproxy.dns.ttl               : amount of time (in seconds) we will cache dns results for. default (120)
 - exaproxy.http.allow-connect    : allow client to use CONNECT and https connections. default (true)
 - exaproxy.http.extensions       : allow new HTTP method (space separated). default ('')
 - exaproxy.http.transparent      : do not insert Via headers. default (false)
 - exaproxy.http.x-forwarded-for  : insert X-Forwarded-For headers to webservers. default (true)
 - exaproxy.logger.client         : log messages from the client subsystem. default (true)
 - exaproxy.logger.configuration  : log messages from the configuration subsystem. default (true)
 - exaproxy.logger.daemon         : log messages from the daemon subsystem. default (true)
 - exaproxy.logger.destination    : where syslog should log. default ('stdout')
 - exaproxy.logger.download       : log messages from the download subsystem. default (true)
 - exaproxy.logger.http           : log messages from the http subsystem. default (true)
 - exaproxy.logger.level          : log message with at least the priority SYSLOG.<level>. default (LOG_ERR)
 - exaproxy.logger.logger         : log messages from the logger subsystem. default (true)
 - exaproxy.logger.manager        : log messages from the manager subsystem. default (true)
 - exaproxy.logger.server         : log messages from the server subsystem. default (true)
 - exaproxy.logger.signal         : log messages from the signal subsystem. default (true)
 - exaproxy.logger.supervisor     : log messages from the supervisor subsystem. default (true)
 - exaproxy.logger.worker         : log messages from the worker subsystem. default (true)
 - exaproxy.profile.destination   : save profiling to file (instead of to the screen on exit). default ('stdout')
 - exaproxy.profile.enable        : enable profiling. default (false)
 - exaproxy.redirector.enable     : use redirector programs to filter http request. default (false)
 - exaproxy.redirector.maximum    : maximum number of worker threads (forked program). default (25)
 - exaproxy.redirector.minimum    : minimum number of worker threads (forked program). default (5)
 - exaproxy.redirector.program    : the program used to know where to send request. default ('etc/exaproxy/redirector/url-allow')
 - exaproxy.redirector.protocol   : what protocol to use (url: squid like / icap:://<uri> icap like). default ('url')
 - exaproxy.tcp4.backlog          : when busy how many connection should the OS queue for us. default (200)
 - exaproxy.tcp4.host             : the host the proxy listen on. default ('127.0.0.1')
 - exaproxy.tcp4.listen           : should we listen for connections over IPv4. default (true)
 - exaproxy.tcp4.out              : allow connections to remote web servers over IPv4. default (true)
 - exaproxy.tcp4.port             : the port the proxy listen on. default (3128)
 - exaproxy.tcp4.timeout          : time before we abandon inactive established connections. default (5)
 - exaproxy.tcp6.backlog          : when busy how many connection should the OS queue for us. default (200)
 - exaproxy.tcp6.host             : the host the proxy listen on. default ('::1')
 - exaproxy.tcp6.listen           : should we listen for connections over IPv6. default (false)
 - exaproxy.tcp6.out              : allow connections to remote web servers over IPv6. default (true)
 - exaproxy.tcp6.port             : the port the proxy listen on. default (3128)
 - exaproxy.tcp6.timeout          : time before we abandon inactive established connections. default (5)
 - exaproxy.web.enable            : enable the built-in webserver. default (true)
 - exaproxy.web.host              : the address the web server listens on. default ('127.0.0.1')
 - exaproxy.web.html              : where internal proxy html pages are served from. default ('etc/exaproxy/html')
 - exaproxy.web.port              : port the web server listens on. default (8080)



```

# Show the current setting using the INI fomat #

```
»› ./sbin/exaproxy -i

[exaproxy.daemon]
daemonize = false
user = 'nobody'
reactor = 'epoll'
speed = 2
pidfile = ''
filemax = 10240

[exaproxy.dns]
definitions = 'etc/exaproxy/dns/types'
expire = 200
resolver = '/etc/resolv.conf'
timeout = 10
ttl = 120

[exaproxy.http]
x-forwarded-for = true
allow-connect = true
extensions = ''
transparent = false

[exaproxy.logger]
daemon = true
supervisor = true
level = LOG_ERR
signal = true
destination = 'stdout'
worker = true
server = true
manager = true
client = true
download = true
http = true
logger = true
configuration = true

[exaproxy.profile]
enable = false
destination = 'stdout'

[exaproxy.redirector]
protocol = 'url'
enable = false
program = 'etc/exaproxy/redirector/url-allow'
minimum = 5
maximum = 25

[exaproxy.tcp4]
host = '127.0.0.1'
timeout = 5
listen = true
port = 3128
backlog = 200
out = true

[exaproxy.tcp6]
host = '::1'
timeout = 5
listen = false
port = 3128
backlog = 200
out = true

[exaproxy.web]
host = '127.0.0.1'
enable = true
html = 'etc/exaproxy/html'
port = 8080



```

# Show the current setting using the ENV fomat #

```
»› ./sbin/exaproxy -e

exaproxy.profile.enable=false
exaproxy.profile.destination='stdout'
exaproxy.web.host='127.0.0.1'
exaproxy.web.enable=true
exaproxy.web.html='etc/exaproxy/html'
exaproxy.web.port=8080
exaproxy.daemon.reactor='epoll'
exaproxy.daemon.filemax=10240
exaproxy.daemon.daemonize=false
exaproxy.daemon.user='nobody'
exaproxy.daemon.speed=2
exaproxy.daemon.pidfile=''
exaproxy.http.x-forwarded-for=true
exaproxy.http.allow-connect=true
exaproxy.http.extensions=''
exaproxy.http.transparent=false
exaproxy.tcp6.host='::1'
exaproxy.tcp6.timeout=5
exaproxy.tcp6.listen=false
exaproxy.tcp6.port=3128
exaproxy.tcp6.backlog=200
exaproxy.tcp6.out=true
exaproxy.dns.definitions='etc/exaproxy/dns/types'
exaproxy.dns.expire=200
exaproxy.dns.resolver='/etc/resolv.conf'
exaproxy.dns.timeout=10
exaproxy.dns.ttl=120
exaproxy.tcp4.host='127.0.0.1'
exaproxy.tcp4.timeout=5
exaproxy.tcp4.listen=true
exaproxy.tcp4.port=3128
exaproxy.tcp4.backlog=200
exaproxy.tcp4.out=true
exaproxy.logger.daemon=true
exaproxy.logger.supervisor=true
exaproxy.logger.level=LOG_ERR
exaproxy.logger.signal=true
exaproxy.logger.destination='stdout'
exaproxy.logger.worker=true
exaproxy.logger.server=true
exaproxy.logger.manager=true
exaproxy.logger.client=true
exaproxy.logger.download=true
exaproxy.logger.http=true
exaproxy.logger.logger=true
exaproxy.logger.configuration=true
exaproxy.redirector.protocol='url'
exaproxy.redirector.enable=false
exaproxy.redirector.program='etc/exaproxy/redirector/url-allow'
exaproxy.redirector.minimum=5
exaproxy.redirector.maximum=25



```

The changes from the default configuration (a.k.a minimum configuration)

```
»› ./sbin/exaproxy -di

[exaproxy.daemon]
reactor = 'select'

»› ./sbin/exaproxy -de

exaproxy.daemon.reactor='select'



```

# Output with full debugging #

```
»› env INTERPRETER=python ./sbin/exaproxy -d
Tue, 28 Feb 2012 17:45:20 INFO      24650  supervisor    starting /Users/thomas/source/hg/exaproxy/lib/exaproxy/application.py
Tue, 28 Feb 2012 17:45:20 INFO      24650  supervisor    python version 2.7.2 (default, Feb 23 2012, 10:00:52)  [GCC 4.2.1 (Based on Apple Inc. build 5658) (LLVM build 2335.15.00)]
Tue, 28 Feb 2012 17:45:20 INFO      24650  manager       starting workers.
Tue, 28 Feb 2012 17:45:20 INFO      24650  manager       spawning 5 more worker
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  manager       added a worker
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  manager       we have 1 workers. defined range is ( 5 / 25 )
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  worker 1      waiting for some work
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  manager       added a worker
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  manager       we have 2 workers. defined range is ( 5 / 25 )
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  worker 2      waiting for some work
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  manager       added a worker
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  manager       we have 3 workers. defined range is ( 5 / 25 )
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  worker 3      waiting for some work
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  manager       added a worker
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  manager       we have 4 workers. defined range is ( 5 / 25 )
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  worker 4      waiting for some work
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  manager       added a worker
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  manager       we have 5 workers. defined range is ( 5 / 25 )
Tue, 28 Feb 2012 17:45:20 DEBUG     24650  worker 5      waiting for some work
Tue, 28 Feb 2012 17:45:20 WARNING   24650  signal        refork not implemented
Tue, 28 Feb 2012 17:45:21 DEBUG     24650  signal        SIG ALRM received, timed actions
Tue, 28 Feb 2012 17:45:21 DEBUG     24650  supervisor    events : write_resolver, write_client, opening_download, write_download
Tue, 28 Feb 2012 17:45:22 DEBUG     24650  signal        SIG ALRM received, timed actions
Tue, 28 Feb 2012 17:45:22 DEBUG     24650  supervisor    events : write_resolver, write_client, opening_download, write_download
Tue, 28 Feb 2012 17:45:23 DEBUG     24650  signal        SIG ALRM received, timed actions
Tue, 28 Feb 2012 17:45:23 DEBUG     24650  supervisor    events : write_resolver, write_client, opening_download, write_download
^CTue, 28 Feb 2012 17:45:24 INFO      24650  supervisor    ^C received
Tue, 28 Feb 2012 17:45:24 INFO      24650  supervisor    Performing shutdown
Tue, 28 Feb 2012 17:45:24 INFO      24650  manager       stopping 5 workers.
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  manager       we are killing worker 1
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  worker 1      shutdown
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  manager       we are killing worker 3
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  worker 3      shutdown
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  manager       we are killing worker 2
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  worker 2      shutdown
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  manager       we are killing worker 5
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  worker 5      shutdown
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  manager       we are killing worker 4
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  worker 4      shutdown
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  worker 2      Consumed a message before we knew we should stop. Handling it before hangup
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  worker 1      Consumed a message before we knew we should stop. Handling it before hangup
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  worker 3      Consumed a message before we knew we should stop. Handling it before hangup
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  worker 5      Consumed a message before we knew we should stop. Handling it before hangup
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  worker 4      Consumed a message before we knew we should stop. Handling it before hangup
Tue, 28 Feb 2012 17:45:24 DEBUG     24650  signal        SIG ALRM received, timed actions

.



```