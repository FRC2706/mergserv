#!/usr/bin/env python3

import network
import sys

args = sys.argv[1:]

network.start_server()

while True:
    command = input()

    if command == "disable-networking":
        if not network.ENABLED:
            print("Networking is already disabled. enable it with 'enable-networking'")
        else:
            # Disable networking somehow
            print("Disabling network...")
            network.ENABLED = False

    elif command == "enable-networking":
        if network.ENABLED:
            print("Networking is already enabled. Disable it with 'disable-networking'")
        else:
            # Re-Enable networking somehow
            print("Enabling network...")
            network.ENABLED = True
            network.start_server()

    elif command == "sync-all-peers":
        pass

    elif command == "list-peers":
        for peer in network.peers:
            print(peer)

    elif command.startswith("add-peer"):
        peer = command.split(" ")[1]
        if network.verifypeer(peer):
            network.peers.append(peer)
            print("Peer test successful, added to peerlist")
        else:
            print("Peer test failed.")

    

    else:
        print("Unrecognized command.")
