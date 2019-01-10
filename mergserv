#!/usr/bin/env python3

import network
import sys

args = sys.argv[1:]

network.start_server()

while True:
    command = input()

    if command == "net off":
        if not network.ENABLED:
            print("Networking is already disabled. enable it with 'enable-networking'")
        else:
            # Disable networking somehow
            print("Disabling network...")
            network.ENABLED = False

    elif command == "net on":
        if network.ENABLED:
            print("Networking is already enabled. Disable it with 'disable-networking'")
        else:
            # Re-Enable networking somehow
            print("Enabling network...")
            network.ENABLED = True
            network.start_server()

    elif command == "sync":
        pass

    elif command == "listpeers":
        print(("Server has %d peer" % len(network.peers)) + ("s" if len(network.peers) != 1 else "") + (":" if len(network.peers) != 0 else ""))
        for peer in network.peers:
            print("\t" + peer)

    elif command.startswith("addpeer"):
        peer = command.split(" ")[1]
        if network.verifypeer(peer):
            network.peers.append(peer)
            print("Peer test successful, added to peerlist")
        else:
            print("Peer test failed.")



    elif command == "":
        pass
    else:
        print("Unrecognized command.")
