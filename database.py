import sqlite3
import crypto
import log
import traceback
import json

DATABASE = "merg.db"

def init_database():
	conn, db = get_db()
	tables = [
		"CREATE TABLE events (sync_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, type VARCHAR(5) NOT NULL, team_number SMALLINT UNSIGNED NOT NULL, match_number TINYINT UNSIGNED NOT NULL, competition VARCHAR(16) NOT NULL, start_time TINYINT UNSIGNED NOT NULL, end_time TINYINT UNSIGNED NOT NULL, extra VARCHAR(64) NOT NULL, scout_name VARCHAR(16) NOT NULL, scout_team SMALLINT UNSIGNED NOT NULL, signature TEXT NOT NULL)",
		"CREATE TABLE matches (match_number TINYINT UNSIGNED NOT NULL, competition VARCHAR(16) NOT NULL, blue1 TINYINT UNSIGNED NOT NULL, blue2 TINYINT UNSIGNED NOT NULL, blue3 TINYINT UNSIGNED NOT NULL, red1 TINYINT UNSIGNED NOT NULL, red2 TINYINT UNSIGNED NOT NULL, red3 TINYINT UNSIGNED NOT NULL)",
		"CREATE TABLE competitions (competition VARCHAR(16) PRIMARY KEY NOT NULL, year SMALLINT UNSIGNED NOT NULL)",
		"CREATE TABLE teams (team TINYINT UNSIGNED PRIMARY KEY NOT NULL, name VARCHAR(32) NOT NULL, public_key TEXT)"
	]

	for table in tables:
		try:
			db.execute(table)
		except Exception as e:
			log.warn("Database","%s" % str(e))

def get_team(team):
	conn, db = get_db()
	db.execute("SELECT * FROM teams WHERE team=?", (team,))
	results = db.fetchall()
	columns = [x[0] for x in db.description]
	ret = []
	for i in range(len(results)):
		temp = {}
		for j in range(len(columns)):
			temp[columns[j]] = results[i][j]
		ret.append(temp)
	return ret[0] if len(ret) > 0 else {}

def get_teams():
	conn, db = get_db()
	db.execute("SELECT * FROM teams")
	results = db.fetchall()
	columns = [x[0] for x in db.description]
	ret = []
	for i in range(len(results)):
		temp = {}
		for j in range(len(columns)):
			temp[columns[j]] = results[i][j]
		ret.append(temp)
	return ret

def get_events(competition_name, match_number=None):
	conn, db = get_db()
	if match_number is None:
		db.execute("SELECT * FROM events WHERE competition=?", (competition_name,))
	else:
		db.execute("SELECT * FROM events WHERE competition=? AND match_number=?", (competition_name,match_number))
	results = db.fetchall()
	columns = [x[0] for x in db.description]
	ret = []
	for i in range(len(results)):
		temp = {}
		for j in range(len(columns)):
			temp[columns[j]] = results[i][j]
		ret.append(temp)
	return ret

def get_scores(competition_name, last_match_num):
	conn, db = get_db()
	db.execute("SELECT * FROM matches WHERE competition_name=? AND match_number > ?", (competition_name, last_match_num))
	results = db.fetchall()
	columns = [x[0] for x in db.description]
	ret = []
	for i in range(len(results)):
		temp = {}
		for j in range(len(columns)):
			temp[columns[j]] = results[i][j]
		ret.append(temp)
	return ret

def dump_matches(competition_name):
	conn, db = get_db()
	db.execute("SELECT * FROM matches WHERE competition=?", (competition_name,))
	results = db.fetchall()
	columns = [x[0] for x in db.description]
	ret = []
	for i in range(len(results)):
		temp = {}
		for j in range(len(columns)):
			temp[columns[j]] = results[i][j]
		ret.append(temp)
	return ret

def list_competitions(year):
	conn, db = get_db()
	db.execute("SELECT * FROM competitions WHERE year=?", (year,))
	results = db.fetchall()
	columns = [x[0] for x in db.description]
	ret = []
	for i in range(len(results)):
		temp = {}
		for j in range(len(columns)):
			temp[columns[j]] = results[i][j]
		ret.append(temp)
	return ret

'''
Return codes:
0: Success
1: Unknown error
2: Invalid signature
'''

def push_events(competition, events):
	conn, db = get_db()
	for event in events:
		ev_type = event["type"]
		team = event["team_number"]
		match = event["match_number"]
		start = event["start_time"]
		end = event["end_time"]
		success = event["success"]
		extra = event["extra"]
		scout_name = event["scout_name"]
		scout_team = event["scout_team"]
		signature = event["signature"]
		del event["signature"]
		db.execute("SELECT * FROM teams WHERE team=?", (team,))
		ht = db.fetchall()
		if len(ht) < 1:
			return 2
		public = ht[0][2]
		if public == None or not crypto.verify_row(event, public, signature):
			return 2
		stuff = (ev_type, team, match, competition, start, end, success, scout_name, scout_team, signature)
		db.execute("INSERT INTO events (type, team_number, match_number, competition, start_time, end_time, success, extra, scout_name, scout_team, signature) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", stuff)
	conn.commit()
	return 0

def get_db():
	conn = sqlite3.connect(DATABASE)
	return (conn, conn.cursor())

def insert_competition(code, year):
	try:
		conn, db = get_db()
		db.execute("INSERT INTO competitions (year, competition) VALUES (?, ?)", (year, code))
		conn.commit()
		return True
	except Exception as e:
		if "UNIQUE" not in str(e):
			traceback.print_exc()
		return False

def insert_match(number, event, red, blue):
	try:
		conn, db = get_db()
		db.execute("INSERT INTO matches (match, competition, red1, red2, red3, blue1, blue2, blue3) VALUES (?,?,?,?,?,?,?,?)", (number, event, red[0], red[1], red[2], blue[0], blue[1], blue[2]))
		conn.commit()
		return True
	except:
		if "UNIQUE" not in str(e):
			traceback.print_exc()
		return False

def insert_many_matches(matches, event):
	conn,db = get_db()
	for match in matches:
		number = match['match']
		red = [match["red1"], match["red2"], match["red3"]]
		blue = [match["blue1"], match["blue2"], match["blue3"]]
		try:
			db.execute("INSERT INTO matches (match, competition, red1, red2, red3, blue1, blue2, blue3) VALUES (?,?,?,?,?,?,?,?)", (number, event, red[0], red[1], red[2], blue[0], blue[1], blue[2]))
		except:
			if "UNIQUE" not in str(e):
				traceback.print_exc()


def insert_team(number, name, key):
	try:
		conn, db = get_db()
		db.execute("INSERT INTO teams (team, name, public_key) VALUES (?, ?, ?)", (number, name, key))
		conn.commit()
		log.ok("Database", "Added team %s to database" % number)
		return True
	except:
		# Probably the Unique Constraint
		return False

def create_event(event):
	conn, db = get_db()
	ev_type = event["type"]
	team = event["team_number"]
	match = event["match_number"]
	start = event["start_time"]
	end = event["end_time"]
	success = event["success"]
	extra = event["extra"]
	scout_name = event["scout_name"]
	scout_team = event["scout_team"]
	competition = event['competition']
	signature = crypto.sign_row(event)
	if not crypto.verify_row(event, crypto.pubkey, signature):
		print("crypto failed")
		return 2
	stuff = (ev_type, team, match, competition, start, end, success, extra, scout_name, scout_team, signature)
	db.execute("INSERT INTO events (type, team_number, match_number, competition, start_time, end_time, success, extra, scout_name, scout_team, signature) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", stuff)
	conn.commit()

init_database()
