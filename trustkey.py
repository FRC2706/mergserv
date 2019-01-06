#!/usr/bin/env python3

import database
import sys

if len(sys.argv) != 3:
	print("Usage: " + sys.argv[0] + " [team number] [public key]")
	exit(1)

conn, db = database.get_db()
db.execute("UPDATE teams SET public_key=? WHERE team_number=?", sys.argv[1], sys.argv[2])
conn.commit()