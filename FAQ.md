# FAQ #

**Why another python proxy ?**
> This is such a good question that we have a [full page](why.md) dedicate to answer it.


**Where can I ask for help ??**

> The best place to start is our google group
```
exaproxy-users@googlegroups.com
http://groups.google.com/group/exaproxy-users/
```

> But feel free to contact us: via **mail** and/or **jabber** at
```
> echo 'print ".".join(["thomas","mangin@exa-networks","co","uk"])' | python
> echo 'print ".".join(["david","farrar@exa-networks","co","uk"])' | python
```


**When can I ask for help ??**
> We normally answer mails as soon as we see them. Our timezone is BST/GMT (United Kingdom).


**Where is the documentation ?**
> Here and in the code .. really do you need more ??<br>
<blockquote>If so please feel free to contribute some, I am a terrible author.</blockquote>


<b>Is this code supported ?</b>
<blockquote>Yes - Should you find any bugs, please report it, and I will fix them</blockquote>


<b>Does it work on Linux, MAC OS X, Windows ?</b>
<blockquote>Linux: yes, it is our deployment environment <br>
MACOS: yes, it is developed on MAC OSX 10.7<br>
Windows: no, we are using Unix alarm, which is not supported on Windows</blockquote>

<b>Are you planning to add more features ?</b>
<blockquote>We will only really code new features for our own use, but feel free to ask or send us patches.</blockquote>


<b>As the main loop is single threaded, can a blocking network IO cause issues ?</b>
<blockquote>It is possible for a bug to cause the application to freeze but epoll is really the only way to get correct performance out of server for network I/O intensive applications. However it should only happen if we have bugs in the code, which hopefully will not be common at all.