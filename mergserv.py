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

    else:
        print("Unrecognized command.")
