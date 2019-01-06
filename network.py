import socket as socket
import _thread as thread
import threading
import json
import database

API_VERSION_MAJOR = 0
API_VERSION_MINOR = 0

REQUEST_PUSH = "push"
REQUEST_PULL = "pull"
REQUEST_DUMP_MATCHES = "dump_matches"
REQUEST_LIST_COMPETITIONS = "list_comps"

RESPONSE_OK = "ok"
RESPONSE_VERSION_MISMATCH = "version_mismatch"
RESPONSE_UNKNOWN = "unknown"
RESPONSE_INVALID_REQUEST = "invalid"
RESPONSE_SIGNATURE_REJECTED = "unauthorized"

PEER_CONNECT_TIMEOUT = 1
SOCKET_TIMEOUT = 3
PORT = 9999

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

def write_msg(sock, request_type, extra):
	data = extra.copy()
	data["version_major"] = API_VERSION_MAJOR
	data["version_minor"] = API_VERSION_MINOR
	data["type"] = request_type
	jstr = json.dumps(data)
	sock.sendall(jstr.encode('utf-8'))

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
		write_msg(sock, RESPONSE_INVALID_REQUEST, {})
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
		write_msg(sock, RESPONSE_VERSION_MISMATCH, {})
		sock.close()
		return

	# Switch by request type
	if data["type"] == REQUEST_PUSH:

		# Perform push
		if not "events" in data or not "competition" in data:
			write_msg(sock, RESPONSE_UNKNOWN, {})
			sock.close()
			return
		ret = database.push_events(data["competition"], data["events"])

		# Return push status
		response = RESPONSE_OK
		if ret == 1:
			response = RESPONSE_UNKNOWN
		elif ret == 2:
			response = RESPONSE_SIGNATURE_REJECTED
		write_msg(sock, response, {})

	elif data["type"] == REQUEST_PULL:

		# Fetch events from database
		if not "last_sync" in data or not "competition" in data:
			write_msg(sock, RESPONSE_UNKNOWN, {})
			sock.close()
			return
		events = database.get_events(data["competition"], data["last_sync"])
		write_msg(sock, RESPONSE_OK, {"events": events})
	elif data["type"] == REQUEST_DUMP_MATCHES:
		if not "competition" in data:
			write_msg(sock, RESPONSE_UNKNOWN, {})
			sock.close()
			return
		matches = database.dump_matches(data["competition"])
		write_msg(sock, RESPONSE_OK, {"matches": matches})

	elif data["type"] == REQUEST_LIST_COMPETITIONS:
		if not "year" in data:
			write_msg(sock, RESPONSE_UNKNOWN, {})
			sock.close()
			return
		comps = database.list_competitions(data["year"])
		write_msg(sock, RESPONSE_OK, {"competitions": comps})

	elif data["type"] == REQUEST_PEER_LIST:
		writemsg(sock, RESPONSE_OK, peers)

	else:
		write_msg(sock, RESPONSE_INVALID_REQUEST, {})
	sock.close()

# Find peers and connect to them
def peerscan():
	global peers

	# TODO: Discover nodes

	# Connect to discovered nodes
	for peer in peers:	# TODO: Multiple scan threads
		if not verifypeer(peer):
			peers.remove(peer)

def verifypeer(peer):
	try:
		# Connect to peer
		sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
		sock.settimeout(PEER_CONNECT_TIMEOUT)
		sock.connect((peer, PORT))
		sock.close()
		return True
	except Exception as e:
		print("Error while attempting connection to %s: %s" % (peer, e))
		return False
