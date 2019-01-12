import socket as socket
import _thread as thread
import threading
import json
import database
import ipaddress
import ifaddr

API_VERSION_MAJOR = 0
API_VERSION_MINOR = 0

REQUEST_HANDSHAKE = "shake"
REQUEST_PUSH = "push"
REQUEST_PULL = "pull"
REQUEST_DUMP_MATCHES = "dump_matches"
REQUEST_LIST_COMPETITIONS = "list_comps"

RESPONSE_OK = "ok"
RESPONSE_VERSION_MISMATCH = "version_mismatch"
RESPONSE_UNKNOWN = "unknown"
RESPONSE_INVALID_REQUEST = "invalid"
RESPONSE_SIGNATURE_REJECTED = "unauthorized"

PEER_CONNECT_TIMEOUT = 4
SOCKET_TIMEOUT = 3
PORT = 31465

peers = []

ENABLED = True

def read_string(sock):
	val = ""
	while True:
		dat = sock.recv(1)
		if not dat:
			sock.close()
			return None
		char = dat.decode('utf-8')
		if char == '\x00' or char == '\n':
			return val
		val+= char

def write_msg_new(addr, request_type, extra):
	global peers
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((peer, PORT))
	except:
		if addr in peers:
			peers.remove(addr)
			print("Removed peer '" + peer + "'")
		return None
	return write_msg(sock, request_type, extra, True)

def write_msg(sock, request_type, extra, wait_for_response):
	data = extra.copy()
	data["version_major"] = API_VERSION_MAJOR
	data["version_minor"] = API_VERSION_MINOR
	data["type"] = request_type
	jstr = json.dumps(data) + "\00"
	sock.sendall(jstr.encode('utf-8'))
	
	if not wait_for_response:
		sock.close()
		return None
	
	# Read response
	jstr = read_string(sock)
	sock.close()
	if jstr is None:
		return None
	try:
		return json.loads(jstr)
	except:
		return None

def push_all(addr, year):
	for competition in database.list_competitions(year):
		push(addr, competition["competition"])

def push(addr, competition):
	write_msg_new(addr, REQUEST_PUSH, {"events": database.get_events(competition)})

def pull(addr, competition):
	resp = write_msg_new(addr, REQUEST_PULL, {"competition": competition})
	if resp != None:
		pass	# TODO: Handle pull

def request_matches(addr, competition):
	resp = write_msg_new(addr, REQUEST_DUMP_MATCHES, {"competition": competition})
	if resp != None:
		pass	# TODO: Handle matches

def request_comps(addr, year):
	resp = write_msg_new(addr, REQUEST_LIST_COMPETITIONS, {"year": year})
	if resp != None:
		pass	# TODO: Handle comps

def handshake(sock):
	resp = write_msg(sock, REQUEST_HANDSHAKE, {"peers": peers}, True)
	if resp["type"] != RESPONSE_OK or not "peers" in resp:
		return
	handle_handshake(resp)

def handle_handshake(data):
	# Add fed peers
	for peer in data["peers"]:
		fed_peers.append(peer)

def start_server():
	# Start the thread as a daemon, so it will stop when the main thread exits
	threading.Thread(target=server, daemon=True).start()

def server():
	ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ss.settimeout(SOCKET_TIMEOUT)
	ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	ss.bind(("0.0.0.0", PORT))
	ss.listen()
	thread.start_new_thread(peerscan, ())
	print("Network started!")
	while True:
		if ENABLED:
			try:
				sock, addr = ss.accept()
				thread.start_new_thread(handle_request, (sock,))
			except:
				# socket timed out.
				continue
		else:
			break
	print("Network stopped!")

def handle_request(sock):
	global peers
	global fed_peers
	
	# Add to our peers list if they aren't in it already
	ip = sock.getpeername()[0]
	if not ip in peers:
		peers.append(ip)
	
	# Read JSON request
	jstr = read_string(sock)
	if jstr is None:
		return
	try:
		data = json.loads(jstr)
	except:
		# Client send invalid json
		write_msg(sock, RESPONSE_INVALID_REQUEST, {}, False)
		return
	
	# Check that request is formatted correctly
	if not "version_major" in data or not "version_minor" in data or not "type" in data:
		sock.close()
		return
	
	# Check client version
	major_version = data["version_major"]
	minor_version = data["version_minor"]
	if major_version != API_VERSION_MAJOR:
		
		# Throw version mismatch error
		write_msg(sock, RESPONSE_VERSION_MISMATCH, {}, False)
		return
	
	# Add to peers list
	if not ip in peers:
		peers.append(ip)
		print("Added peer '" + ip + "'")
		write_peers()
	
	# Switch by request type
	if data["type"] == REQUEST_HANDSHAKE:
		if not "peers" in data:
			write_msg(sock, RESPONSE_UNKNOWN, {}, False)
			return
		
		handle_handshake(data)
		write_msg(sock, RESPONSE_OK, {"peers": peers}, False)
		
	elif data["type"] == REQUEST_PUSH:
		
		# Perform push
		if not "events" in data or not "competition" in data:
			write_msg(sock, RESPONSE_UNKNOWN, {}, False)
			return
		ret = database.push_events(data["competition"], data["events"])
		
		# Return push status
		response = RESPONSE_OK
		if ret == 1:
			response = RESPONSE_UNKNOWN
		elif ret == 2:
			response = RESPONSE_SIGNATURE_REJECTED
		write_msg(sock, response, {}, False)
		
	elif data["type"] == REQUEST_PULL:
		
		# Fetch events from database
		if not "competition" in data:
			write_msg(sock, RESPONSE_UNKNOWN, {}, False)
			sock.close()
			return
		events = database.get_events(data["competition"])
		write_msg(sock, RESPONSE_OK, {"events": events}, False)
	elif data["type"] == REQUEST_DUMP_MATCHES:
		if not "competition" in data:
			write_msg(sock, RESPONSE_UNKNOWN, {})
			sock.close()
			return
		matches = database.dump_matches(data["competition"])
		write_msg(sock, RESPONSE_OK, {"matches": matches}, False)
		
	elif data["type"] == REQUEST_LIST_COMPETITIONS:
		if not "year" in data:
			write_msg(sock, RESPONSE_UNKNOWN, {}, False)
			return
		comps = database.list_competitions(data["year"])
		write_msg(sock, RESPONSE_OK, {"competitions": comps}, False)
		
	else:
		write_msg(sock, RESPONSE_INVALID_REQUEST, {}, False)

# Find peers and connect to them
def peerscan():
	global peers
	global fed_peers
	
	# Discover peers
	tmp_peers = fed_peers
	tmp_peers = tmp_peers + peers
	#tmp_peers = tmp_peers + expand_lan()
	for peer in man_peers:
		if not peer in peers:
			tmp_peers.append(peer)
	fed_peers = []
	
	# Connect to discovered nodes
	for peer in tmp_peers:
		try:
			# Connect to peer
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(PEER_CONNECT_TIMEOUT)
			sock.connect((peer, PORT))
			sock.settimeout(None)
			if not peer in peers:
				peers.append(peer)
			print("Added peer '" + peer + "'")
			handshake(sock)
		except:
			if peer in peers:
				print("Removed peer '" + peer + "'")
				peers.remove(peer)
	write_peers()

def expand_lan():
	addrs = []
	for adapter in ifaddr.get_adapters():
		for localhost in adapter.ips:
			if type(localhost.ip) != str:
				continue
			for ip in ipaddress.ip_network(localhost.ip + "/24", False).hosts():
				addrs.append(ip)
	return addrs

def write_peers():
	f = open("disc_peers", "w+")
	for peer in peers:
		f.write(peer + "\n")
	f.close()

# Fed peers
fed_peers = []

# Load man_peers
man_peers = []
try:
	f = open("man_peers", "r")
	for line in f:
		line = line.strip()
		if not line == "" and not line.startswith("#"):
			man_peers.append(line)
	f.close()
except:
	f = open("man_peers", "w+")
	f.write("167.99.176.67")	# openfortress.xyz server
	f.close()

# Load discovered peers
peers = []
try:
	f = open("disc_peers", "r")
	for line in f:
		line = line.strip()
		if not line == "" and not line.startswith("#"):
			if not line in peers:
				peers.append(line)
	f.close()
except:
	pass
