# RFC Information #

If you do not understand the following, **do not be alarmed, you are unlikely to care**, this information is included for exhaustiveness.

**RFC (fully or partially) implemented** :
  * [RFC 2616](http://www.ietf.org/rfc/rfc2616.txt) - Hypertext Transfer Protocol -- HTTP/1.1
  * [RFC 6455](http://tools.ietf.org/html/rfc6455) - The WebSocket Protocol
  * [RFC 2817](http://tools.ietf.org/html/rfc2817) - Upgrading to TLS Within HTTP/1.1

**ExaProxy is known to violate the RFC 2116**

ExaProxy just implement enough code to not break websockets and TLS and forward them to backend webservers, instead of removing the Upgrade header from the request. It tunnels those requests the same way as it handles CONNECT requests.

ExaProxy by design does not parse and modify the response given by the HTTP servers, this is a choice made for performance.

The proxy parses just enough of the HTTP request to be able to deal with chunk-encoded data but does not correct transiting request. Therefore, for example, it does dot no add Content-Length to request containing chunked-encoded or multipart/byteranges.

This means that we are violating quite a few RFC statements :
  * no header is inserted in the message from the server, only the request
  * no Date or Via header is added if the server did not include it
  * no Warning header is removed if the time is past
  * we pass keep-alive and upgrade responses between the client and remote server
  * TE request-header fields are forwarded to the remote server. It is up to the remote server to provide a suitable response for us to parrot
  * 100 continue responses made to HTTP/1.0 clients are not filtered (continue message may include headers)

As in order to reduce memory footprint, ExaProxy mostly use the TCP stack memory buffer and does not store much of the data transfered either way, therefore it is not able to:
  * decode chunked-encoded data sent to (or received from) the server
    * convert post from chunk to not chunk to reach a server running HTTP/1.0.
    * remove from the response any range defined in the request
  * add Content-Length to the request when it is missing.

Those HTTP changes are to correct bad client or bad server behaviour. Proxies are expected by the RFC to fix invalid HTTP conversation (not sure why really). In effect making things work which would have not without a proxy.

ExaProxy does not perform transparently those protocol correction. To the best of our knowledge, what would have worked without ExaProxy will continue to work, even if technically it is violating the RFC.

ExaProxy does not support persistent HTTP connections as it would increase massively our CPU usage too. Many proxies do not support this feature (however it is a nice feature).