# Why another proxy ? #

For once, it's not a case of "not invented here" syndrome: we are not aware of any other open source proxy offering the same features as ExaProxy.

ExaProxy was born out of the necessity to filter web traffic. SQUID offers a very nice feature to that end, its [rewriters](http://www.squid-cache.org/Doc/config/url_rewrite_program/). Rewriters are long lived forked process receiving the requested URLs on STDIN and returning on STDOUT the URL we want to fetch for that page really.

Unfortunately, SQUID only allows filtering of HTTP traffic, and is limited to using the source IP of the TCP connection as the IP of the requester, preventing the use of L7 load balancing to spread the charge.

Furthermore SQUID does not support request manipulation through this interface (ie: ways to change cookies for example). Doing so requires the use of ICAP or ECAP which are much more heavy weight protocols as they require the use of a ICAP/ECAP server.

ICAP is a very interesting protocol but most implementations are closed sourced and not easy to deploy.

Before starting work on ExaProxy, we took a look at all other proxies we were aware of. A non-exhaustive list is available at [wikipedia](http://en.wikipedia.org/wiki/Http_proxy). None of them were acceptable candidates. The mainline ones could not perform filtering, or when they could were single threaded, meaning that complex filter code such as seen in [SurfProtect](http://www.surfprotect.co.uk/) would have to asynchronous and incompatible with the SQUID rewriter interface if we were to keep latency to a minimum.

Other Python proxies exist such as [django-webproxy](http://code.google.com/p/django-webproxy/) but they are unfortunately unsuitable for the very high volume traffic we must handle.

We could have built an engine around [twisted-web](http://twistedmatrix.com/trac/wiki/TwistedWeb) but decided against it as we wanted our proxy to work without dependencies.
Twisted is a wonderful piece of software and we use it extensively in our business, but we believe we can provide smaller and faster software by implementing only the features we use and tailoring them to our specific requirements. Only time will tell if we were arrogant or if we succeeded :D

ExaProxy implements its own HTTP parsing and non blocking IO, currently using epoll on linux and select on other platforms. Running development code in conjunction with [HAProxy](http://haproxy.1wt.eu/), we were able to note that on a single machine under heavy load, ExaProxy takes approximately 6 times more CPU than HAProxy, which is probably approaching as good a result as we can expect from a proxy running under cPython.

Should ExaProxy not be what you are after, you may want to consider similar proxies by [Benoit Chesneau](https://github.com/benoitc): [cowboy revproxy](https://github.com/benoitc/cowboy_revproxy) in Erlang, or [tproxy](https://github.com/benoitc/tproxy) in Python and Gevent.

We decided against it but if you need to write any high performance networking application in Python, I would suggest you look at [Thor](http://github.com/mnot/thor/) by [Mark Nottingham](http://www.mnot.net/), if you believe Twisted is too high level for you.