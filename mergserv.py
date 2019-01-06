#!/usr/bin/env python3

import network
import sys

args = sys.argv[1:]

network.start_server()

while True:
    command = input()
    print(command)
