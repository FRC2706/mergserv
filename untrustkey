#!/usr/bin/env python3

import database
import sys

if len(sys.argv) != 2:
	print("Usage: " + sys.argv[0] + " [team number]")
	exit(1)

conn, db = database.get_db()
db.execute("UPDATE teams SET public_key=NULL WHERE team_number=?", sys.argv[1])
conn.commit()