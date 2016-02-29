
import socket, socks, struct
from dnslib import DNSRecord
from dnslib.server import DNSServer, DNSHandler, BaseResolver

class SocksDNSHandler(DNSHandler):

	def get_reply(self, data):
		
		request = DNSRecord.parse(data)
		
		if (self.use_resolver(request)):
			resolver = self.server.resolver
			reply = resolver.resolve(request,self)
			response = reply.pack()
		else:
			data = struct.pack("!H",len(data)) + data
			response = self.send_tcp(data, self.server.resolver.dns, self.server.resolver.dns_port)
			response = response[2:]
		
		if self.protocol == 'udp':
			if self.udplen and len(rdata) > self.udplen:
				truncated_reply = request.truncate()
				response = truncated_reply.pack()
		
		return response

	def use_resolver(self, request):
		# Alter this to define cases when you don't want to resolve using the SOCKS tunnel
		return False
		
	def send_tcp(self, data, host, port):
		sock = socks.socksocket()
		sock.set_proxy(socks.SOCKS5, self.server.resolver.socks, self.server.resolver.socks_port)
		sock.connect((host,port))
		sock.sendall(data)
		response = sock.recv(8192)
		length = struct.unpack("!H",bytes(response[:2]))[0]
		while len(response) - 2 < length:
			response += sock.recv(8192)
		sock.close()
		return response


class SocksResolver(BaseResolver):

	def __init__(self, socks_address, socks_port, dns_address, dns_port, timeout=5):
		self.socks = socks_address
		self.socks_port = socks_port
		self.dns = dns_address
		self.dns_port = dns_port
		self.timeout = timeout

if __name__ == '__main__':
	
	import argparse, time
	
	p = argparse.ArgumentParser(description="SocksDNS Proxy")
	p.add_argument("--port", "-p", type=int, default=53, metavar="<port>", help="Local proxy port (default:53)")
	p.add_argument("--address", "-a", default="", metavar="<address>", help="Local proxy listen address (default:all)")
	p.add_argument("--socks", "-s", default="127.0.0.1:1080", metavar="<socks server:port>", help="Upstream SOCKS proxy server:port (default:127.0.0.1:1080)")
	p.add_argument("--upstream", "-u", default="8.8.8.8:53", metavar="<dns server:port>", help="Upstream DNS server:port (default:8.8.8.8:53)")
	p.add_argument("--tcp", action='store_true', default=False, help="Enable TCP proxy (default: UDP only)")
	p.add_argument("--timeout", "-t", type=int, default=10, metavar="<timeout>", help="Connection timeout in seconds (default:10)")
	args = p.parse_args()
	args.socks, _, args.socks_port = args.socks.partition(':')
	args.socks_port = int(args.socks_port or 1080)
	args.dns, _, args.dns_port = args.upstream.partition(':')
	args.dns_port = int(args.dns_port or 53)
	
	resolver = SocksResolver(args.socks, args.socks_port, args.dns, args.dns_port, args.timeout)
	handler = SocksDNSHandler
   
	udp_server = DNSServer(
		resolver,
		port=args.port,
		address=args.address,
		handler=handler
	)
	udp_server.start_thread()
	
	if args.tcp:
		tcp_server = DNSServer(
			resolver,
			port=args.port,
			address=args.address,
			tcp=True,
			handler=handler
		)
		tcp_server.start_thread()

	while udp_server.isAlive():
		time.sleep(1)
