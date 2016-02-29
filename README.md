# SocksDNS
A silly hacked-up DNS-over-SOCKS server to serve as a replacement to the unmaintained [ShadowDNS](https://github.com/shadowsocks/ShadowDNS) component.

Essentially, the script is simply an altered version of the [dnslib](https://pypi.python.org/pypi/dnslib) proxy [example](https://bitbucket.org/paulc/dnslib/src/04713cc4a9dffa82350093126034977b1f980ae8/dnslib/proxy.py?at=default&fileviewer=file-view-default) but it uses [PySocks](https://pypi.python.org/pypi/PySocks) to establish the socket to the remote DNS server.
