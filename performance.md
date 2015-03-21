# Performance tips #

say a word about network and CPU affinity ...

## load balancing ##

For servers under high load, run one instance of exaproxy per CPU core and load balance traffic with haproxy.

## tune your OS ##

extracted from :
**http://antmeetspenguin.blogspot.co.uk/2011/01/high-performance-linux-router.html** http://www.speedguide.net/articles/linux-tweaking-121

### Increasing count of connections tracking ###

To carry out its tasks, NAT-server is "remember" all the connections that pass through it. Whether it’s "ping" or someone’s "ICQ" – NAT-server "remembers" and follows in his memory in a special table all of these sessions. When the session closes, information about it is deleted from the connection tracking table. The size of this table is fixed. That is why, if the traffic through the server is quite a lot but lacks the size of the table, – then NAT-server starts to drop packets and just breaks sessions. To avoid such horrors, it is necessary to adequately increase the size of the connection tracking table – in accordance with the traffic passing through NAT:

Default value is 65536, you may always just double this value or triple this value when necessary.

/sbin/sysctl -w net.netfilter.nf\_conntrack\_max = 196608

To make it permanent after reboot, please add these values to the sysctl.conf

echo net.ipv4.netfilter.ip\_conntrack\_max = 196608 >> /etc/sysctl.conf

It is not recommended to put so big value if you have less than 1 gigabyte of RAM in your NAT-server. To show the current value you can use something like this:

/sbin/sysctl net.netfilter.nf\_conntrack\_max

See how connection tracking table is already full can be like this:

/sbin/sysctl net.netfilter.nf\_conntrack\_count

### Increasing the size of hash-table ###

Hash table, which stores lists of conntrack-entries, should be increased proportionately.
Here is the rule of adjusting: hashsize = nf\_conntrack\_max / 8
Default value will be 16384, and you can't set this value in the /etc/sysctl.conf file.
To change on the fly,

echo 24576 > /sys/module/nf\_conntrack/parameters/hashsize

and add to the /etc/modprobe.conf

options ip\_conntrack hashsize=24576

### Decreasing time-out values ###

NAT-server only tracks "live" session which pass through it. When the session is closed – information about it is removed so that the connection tracking table does not overflow. Information about the sessions is removed as a timeout. That is, if a session is empty a long time, it is closed and information about it is just removed from the connectionn tracking table.

However, the default value of time-outs are quite large. Therefore, for large flows of traffic even if you stretch nf\_conntrack\_max to the limit – you can still run the risk of quickly run into the overflow table, and the connection is broken. To this did not happen, you must correctly set the timeout connection tracking on NAT-server. Current values can be seen, for example:

sysctl -a | grep conntrack | grep timeout

As a result, you’ll see something like this:

net.netfilter.nf\_conntrack\_generic\_timeout = 600
net.netfilter.nf\_conntrack\_tcp\_timeout\_syn\_sent = 120
net.netfilter.nf\_conntrack\_tcp\_timeout\_syn\_recv = 60
net.netfilter.nf\_conntrack\_tcp\_timeout\_established = 432000
net.netfilter.nf\_conntrack\_tcp\_timeout\_fin\_wait = 120
net.netfilter.nf\_conntrack\_tcp\_timeout\_close\_wait = 60
net.netfilter.nf\_conntrack\_tcp\_timeout\_last\_ack = 30
net.netfilter.nf\_conntrack\_tcp\_timeout\_time\_wait = 120
net.netfilter.nf\_conntrack\_tcp\_timeout\_close = 10
net.netfilter.nf\_conntrack\_tcp\_timeout\_max\_retrans = 300 net.netfilter.nf\_conntrack\_tcp\_timeout\_unacknowledged = 300
net.netfilter.nf\_conntrack\_udp\_timeout = 30
net.netfilter.nf\_conntrack\_udp\_timeout\_stream = 180
net.netfilter.nf\_conntrack\_icmp\_timeout = 30
net.netfilter.nf\_conntrack\_events\_retry\_timeout = 15

This is the value of timeouts in seconds. As you can see, the value net.netfilter.nf\_conntrack\_generic\_timeout is 600 (10 minutes). Ie NAT-server keeps in mind about the session as long as it is to "run over" anything at least once every 10 minutes.

At first glance, that’s okay – but in fact it is very, very bad. If you look at net.netfilter.nf\_conntrack\_tcp\_timeout\_established – you will see there is value 432000. In other words, your NAT-server will support a simple TCP-session as long as it does runs on some bag at least once every 5 days (!).

to adjust,

echo "net.ipv4.netfilter.ip\_conntrack\_tcp\_timeout\_established = 86400" >> /etc/sysctl.conf

This does not requires a reboot, instead, the value will be effective when the timeout value has reached and new value will take effect.

Speaking even more simply, it is just easy to DDOS such NAT-server: his connection-tracking table (nf\_conntrack\_max) overflows with simple flood – so that he will break the connection and in the worst case quickly turns into a black hole.
The time-outs it is recommended to set within 30-120 seconds. This is quite sufficient for normal users, and this is quite sufficient for the timely clearing NAT-table, which excludes its overflow. And do not forget to enter the appropriate
changes to /etc/rc.local and /etc/sysctl.conf


The TCP/IP parameters for tweaking a Linux-based machine for fast internet connections are located in /proc/sys/net/... (assuming 2.1+ kernel). This location is volatile, and changes are reset at reboot. There are a couple of methods for reapplying the changes at boot time, ilustrated below.



Locating the TCP/IP related parameters

All TCP/IP tunning parameters are located under /proc/sys/net/...  For example, here is a list of the most important tunning parameters, along with short description of their meaning:

/proc/sys/net/core/rmem\_max - Maximum TCP Receive Window
/proc/sys/net/core/wmem\_max - Maximum TCP Send Window
/proc/sys/net/ipv4/tcp\_rmem - memory reserved for TCP receive buffers
/proc/sys/net/ipv4/tcp\_wmem - memory reserved for TCP send buffers
/proc/sys/net/ipv4/tcp\_timestamps - timestamps (RFC 1323) add 12 bytes to the TCP header...
/proc/sys/net/ipv4/tcp\_sack - tcp selective acknowledgements.
/proc/sys/net/ipv4/tcp\_window\_scaling - support for large TCP Windows (RFC 1323). Needs to be set to 1 if the Max TCP Window is over 65535.

Keep in mind everything under /proc is volatile, so any changes you make are lost after reboot.



There are some additional internal memory buffers for the TCP Window, allocated for each connection:
/proc/sys/net/ipv4/tcp\_rmem - memory reserved for TCP rcv buffers (reserved memory per connection default)
/proc/sys/net/ipv4/tcp\_wmem  - memory reserved for TCP snd buffers (reserved memory per connection default)

The tcp\_rmem and tcp\_wmem contain arrays of three parameter values: the 3 numbers represent minimum, default and maximum memory values. Those 3 values are used to bound autotunning and balance memory usage while under global memory stress.



Applying TCP/IP Parameters at System Boot

You can edit /etc/rc.local, or /etc/boot.local depending on your distribution so the parameters get automatically reapplied at boot time. The TCP/IP parameters should be self-explanatory: we're basically setting the TCP Window to 256960, disabling timestamps (to avoid 12 byte header overhead), enabling tcp window scaling, and selective acknowledgements:

echo 256960 > /proc/sys/net/core/rmem\_default
echo 256960 > /proc/sys/net/core/rmem\_max
echo 256960 > /proc/sys/net/core/wmem\_default
echo 256960 > /proc/sys/net/core/wmem\_max




echo 0 > /proc/sys/net/ipv4/tcp\_timestamps
echo 1 > /proc/sys/net/ipv4/tcp\_sack
echo 1 > /proc/sys/net/ipv4/tcp\_window\_scaling
Change the values above as desired, depending on your internet connection and maximum bandwidth/latency. There are other parameters you can change from the default if you're confident in what you're doing - just find the correct syntax of the values in /proc/sys/net/... and add a line in the above code analogous to the others. To revert to the default parameters, you can just comment or delete the above code from /etc/rc.local and restart.

Another method to reapply the values upon boot is to include the following in your /etc/sysctl.conf (adjust RWIN values as needed):

net.core.rmem\_default = 256960
net.core.rmem\_max = 256960
net.core.wmem\_default = 256960
net.core.wmem\_max = 256960

net.ipv4.tcp\_timestamps = 0
net.ipv4.tcp\_sack = 1
net.ipv4.tcp\_window\_scaling = 1
Notes:
Execute sysctl -p to make these new settings take effect.
To manually set the MTU value under Linux, use the command: ifconfig eth0 mtu 1500   (where 1500 is the desired MTU size)



Changing Current Values without rebooting

The current TCP/IP parameters can be edited without the need for reboot in the following locations:

/proc/sys/net/core/
rmem\_default = Default Receive Window
rmem\_max = Maximum Receive Window
wmem\_default = Default Send Window
wmem\_max = Maximum Send Window

/proc/sys/net/ipv4/
You'll find timestamps, window scalling, selective acknowledgements, etc.

Keep in mind the values in /proc will be reset upon reboot. You still need to add the code in /etc/rc.local or /etc/boot.local in order to have the changes applied at boot time as described above.



Other TCP Parameters to consider

TCP\_FIN\_TIMEOUT
This setting determines the time that must elapse before TCP/IP can release a closed connection and reuse its resources. During this TIME\_WAIT state, reopening the connection to the client costs less than establishing a new connection. By reducing the value of this entry, TCP/IP can release closed connections faster, making more resources available for new connections. Addjust this in the presense of many connections sitting in the TIME\_WAIT state:

# echo 30 > /proc/sys/net/ipv4/tcp\_fin\_timeout
(default: 60 seconds, recommended 15-30 seconds)

Notes:
You can use any of the earlier described methods to reapply these settings at boot time.
Here is a quick way to view the number of connections and their states:

netstat -tan | grep ':80 ' | awk '{print $6}' | sort | uniq -c



TCP\_KEEPALIVE\_INTERVAL
This determines the wait time between isAlive interval probes. To set:

echo 30 > /proc/sys/net/ipv4/tcp\_keepalive\_intvl
(default: 75 seconds, recommended: 15-30 seconds)



TCP\_KEEPALIVE\_PROBES
This determines the number of probes before timing out. To set:

echo 5 > /proc/sys/net/ipv4/tcp\_keepalive\_probes
(default: 9, recommended 5)



TCP\_TW\_RECYCLE
It enables fast recycling of TIME\_WAIT sockets. The default value is 0 (disabled). The sysctl documentation incorrectly states the default as enabled. It can be changed to 1 (enabled) in many cases. Known to cause some issues with hoststated (load balancing and fail over) if enabled, should be used with caution.

echo 1 > /proc/sys/net/ipv4/tcp\_tw\_recycle
(boolean, default: 0)

TCP\_TW\_REUSE
This allows reusing sockets in TIME\_WAIT state for new connections when it is safe from protocol viewpoint. Default value is 0 (disabled). It is generally a safer alternative to tcp\_tw\_recycle

echo 1 > /proc/sys/net/ipv4/tcp\_tw\_reuse
(boolean, default: 0)

Note: The tcp\_tw\_reuse setting is particularly useful in environments where numerous short connections are open and left in TIME\_WAIT state, such as web servers. Reusing the sockets can be very effective in reducing server load.



Kernel Recompile Option

There is another method one can use to set TCP/IP parameters, involving kernel recompile... If you're brave enough. Look for the parameters in the following files:
/LINUX-SOURCE-DIR/include/linux/skbuff.h
Look for SK\_WMEM\_MAX & SK\_RMEM\_MAX
/LINUX-SOURCE-DIR/include/net/tcp.h
Look for MAX\_WINDOW & MIN\_WINDOW

