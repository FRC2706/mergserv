import socket as socket
import _thread as thread
import json
import database

API_VERSION_MAJOR = 0
API_VERSION_MINOR = 0

REQUEST_PUSH = "push"
REQUEST_PULL = "pull"
REQUEST_PUSH_SCORES = "push_scores"
REQUEST_PULL_SCORES = "pull_scores"
REQUEST_DUMP_MATCHES = "dump_matches"
REQUEST_LIST_COMPETITIONS = "list_comps"

RESPONSE_OK = "ok"
RESPONSE_VERSION_MISMATCH = "version_mismatch"
RESPONSE_UNKNOWN = "unknown"
RESPONSE_INVALID_REQUEST = "invalid"
RESPONSE_SIGNATURE_REJECTED = "unauthorized"

PORT = 9999

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

def server():
	ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	ss.bind(("0.0.0.0", PORT))
	ss.listen()
	while True:
		sock, addr = ss.accept()
		thread.start_new_thread(handle_request, (sock,))

def handle_request(sock):

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
		if not "events" in data:
			write_msg(sock, RESPONSE_UNKNOWN, {})
			sock.close()
			return
		ret = database.push_events(data["events"])

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

	elif data["type"] == REQUEST_PUSH_SCORES:
		# TODO: Push match scores
		pass

	elif data["type"] == REQUEST_PULL_SCORES:

		# Fetch scores from database
		if not "last_match" in data or not "competition" in data:
			write_msg(sock, RESPONSE_UNKNOWN, {})
			sock.close()
			return
		matches = database.get_scores(data["competition"], data["last_match"])
		write_msg(sock, RESPONSE_OK, {"matches": matches})

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

	else:
		write_msg(sock, RESPONSE_INVALID_REQUEST, {})
	sock.close()
