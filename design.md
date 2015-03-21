# Overview #

ExaProxy is composed of several subsystems :
  * a thread manager, [forking](http://en.wikipedia.org/wiki/Fork_(operating_system)) [rewriters](http://www.squid-cache.org/Doc/config/url_rewrite_program/) to make sure HTTP request are handled promptly
  * a select / epoll loop recording the state of every incoming, outgoing connection as well as when our rewriters have results.
  * connections are handled using python [co-routine](http://en.wikipedia.org/wiki/Coroutine)

# Redirectors #

The syntax of the rewriters is compatible with SQUID own. However it is possible to indicate to the proxy that a local file should be served by using the prefix "file://" instead of "http://". The files MUST be within ExaProxy configuration folder, to prevent any possible information leak.