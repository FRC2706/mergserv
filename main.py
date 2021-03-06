import network
import database
import sys
from datetime import datetime
import json
import log
import traceback

args = sys.argv[1:]

network.start_server()

while True:
	command = input()

	if command == "net off":
		if not network.ENABLED:
			log.info("net", "Networking is already disabled. enable it with 'net on'")
		else:
			# Disable networking somehow
			log.info("net", "Disabling network...")
			network.ENABLED = False

	elif command == "net on":
		if network.ENABLED:
			log.info("net", "Networking is already enabled. Disable it with 'net off'")
		else:
			# Re-Enable networking somehow
			log.info("net", "Enabling network...")
			network.ENABLED = True
			network.start_server()

	elif command.startswith("sync "):
		year = int(command.split(" ")[1])
		if len(network.peers) == 0:
			print("No one to sync with!")
		else:
			for peer in network.peers:
				print("Starting sync with %s" % peer)
				network.request_season(peer, year)
				network.push_all(peer, year)
				for comp in database.list_competitions(year):
					log.debug("SYNC", "Pulling %s matches from '%s'" % (comp['competition'], peer))
					network.request_matches(peer, comp['competition'])
				print("Finished syncing with '%s" % peer)

	elif command == "listpeers":
		log.info("listpeers", "Server has %d peers" % len(network.peers))
		for peer in network.peers:
			print("\t" + str(peer))

	elif command.startswith("addpeer"):
		peer = command.split(" ")[1]
		network.add_peer(peer)

	elif command.startswith("mkevent"):
		competition = command.split(" ")[1]
		jstr = command[command.find("{"):command.rfind("}")+1]
		try:
			event = json.loads(jstr)
			database.create_event(event)
		except Exception as e:
			log.error("mkevent","Error while making event")
			traceback.print_exc()
		else:
			log.ok("mkevent","inserted into database")

	elif command.startswith("ftevent"):
		query = command.split(" ")[1]
		if query == "match":
			competition = command.split(" ")[2]
			match = command.split(" ")[3]
		elif query == "competition":
			competition = command.split(" ")[2]

	elif command == "rescan":
		network.scan_timer.cancel()
		network.peerscan()

	elif command.startswith("competitions"):
		year = int(command.split(" ")[1])
		print("Server has %d competitions in the database for season %d" % (len(database.list_competitions(year)),year))

	elif command == "quit":
		network.ENABLED = False
		break

	elif command == "":
		pass
	else:
		log.error("main", "Unrecognized command.")
