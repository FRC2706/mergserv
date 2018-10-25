import socket as SOCKET
import _thread as THREAD
import struct

NET_PROTOCOL_VERSION_MAJOR = 0
NET_PROTOCOL_VERSION_MINOR = 1

REQUEST_PUSH = 1
REQEUST_PULL = 2
REQUEST_PUSH_SCORES = 3
REQUEST_PULL_SCORES = 4
REQUEST_DUMP_MATCHES = 5
REQUEST_LIST_COMPETITIONS = 6

RESPONSE_OK = 0
RESPONSE_VERSION_MISMATCH = 1
RESPONSE_UNKNOWN = 2
RESPONSE_INVALID_MESSAGE = 3

PORT = 9999

def server():
	ss = SOCKET.socket(SOCKET.AF_INET, SOCKET.SOCK_STREAM)
	ss.setsockopt(SOCKET.SOL_SOCKET, SOCKET.SO_REUSEADDR, 1)
	ss.bind(("0.0.0.0", PORT))
	ss.listen()
	while True:
		socket, _ = ss.accept()
		THREAD.start_new_thread(handle_request, (socket,))

def handle_request(socket):
	
	# Check client version
	major_version, minor_version = struct.unpack("HH", socket.recv(4))
	if major_version != NET_PROTOCOL_VERSION_MAJOR:
		
		# Throw version mismatch error
		socket.sendall(struct.pack("HHB", NET_PROTOCOL_VERSION_MAJOR, NET_PROTOCOL_VERSION_MINOR, RESPONSE_VERSION_MISMATCH))
		socket.close()
		return
	
	request_type = struct.unpack("B", socket.recv(1))[0]
	# TODO: Pass to an actual function
