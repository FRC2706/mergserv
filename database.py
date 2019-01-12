import sqlite3
import crypto

DATABASE = "merg.db"

def init_database():
	conn, db = get_db()
	tables = [
		"CREATE TABLE events (sync_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, type VARCHAR(5) NOT NULL, team_number SMALLINT UNSIGNED NOT NULL, match_number TINYINT UNSIGNED NOT NULL, competition VARCHAR(16) NOT NULL, success TINYINT NOT NULL, start_time TINYINT UNSIGNED NOT NULL, end_time TINYINT UNSIGNED NOT NULL, extra VARCHAR(64) NOT NULL, scout_name VARCHAR(16) NOT NULL, scout_team SMALLINT UNSIGNED NOT NULL, signature TEXT NOT NULL)",
		"CREATE TABLE matches (match TINYINT UNSIGNED NOT NULL, competition VARCHAR(16) NOT NULL, blue1 TINYINT UNSIGNED NOT NULL, blue2 TINYINT UNSIGNED NOT NULL, blue3 TINYINT UNSIGNED NOT NULL, red1 TINYINT UNSIGNED NOT NULL, red2 TINYINT UNSIGNED NOT NULL, red3 TINYINT UNSIGNED NOT NULL)",
		"CREATE TABLE competitions (competition VARCHAR(16) PRIMARY KEY NOT NULL, year SMALLINT UNSIGNED NOT NULL)",
		"CREATE TABLE teams (team TINYINT UNSIGNED PRIMARY KEY NOT NULL, public_key TEXT NOT NULL, signature TEXT NOT NULL)"
	]

	for table in tables:
		try:
			db.execute(table)
		except Exception as e:
			print(e)

def get_events(competition_name):
	conn, db = get_db()
	db.execute("SELECT * FROM events WHERE competition=?", (competition_name,))
	return db.fetchall()

def get_scores(competition_name, last_match_num):
	conn, db = get_db()
	db.execute("SELECT * FROM matches WHERE competition_name=? AND match_number > ?", (competition_name, last_match_num))
	return db.fetchall()

def dump_matches(competition_name):
	conn, db = get_db()
	db.execute("SELECT * FROM matches WHERE competition=?", (competition,))
	return db.fetchall()

def list_competitions(year):
	conn, db = get_db()
	db.execute("SELECT * FROM competitions WHERE year=?", (year,))
	return db.fetchall()

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
		db.execute("SELECT * FROM teams WHERE team_number=?", (team,))
		public = db.fetch()['public_key']
		if public == None or not crypto.verify_row(event, public, signature):
			return 2
		stuff = (ev_type, team, match, competition, start, end, success, scout_name, scout_team, signature)
		db.execute("INSERT INTO events (type, team_number, match_number, competition, start_time, end_time, success, extra, scout_name, scout_team, signature) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", stuff)
	return 0


def push_scores(scores):
	conn, db = get_db()
	# TODO: Verify match scores
	for mscore in scores:
		stuff = (mscore["match_number"], mscore["blue_score"], mscore["red_score"])
		db.execute("UPDATE matches WHERE match_number=? AND blue_score IS NULL AND red_score IS NULL SET blue_score=? AND red_score=?", stuff)

def get_db():
	conn = sqlite3.connect(DATABASE)
	return (conn, conn.cursor())

def insert_competition(code, year):
	conn, db = get_db()
	db.execute("INSERT INTO competitions (year, competition) VALUES (?, ?)", (year, code))
	conn.commit()

def insert_match(number, event, red, blue):
	conn, db = get_db()
	db.execute("INSERT INTO matches (match_number, competition, red1, red2, red3, blue1, blue2, blue3) VALUES (?,?,?,?,?,?,?,?)", (number, event, red[0], red[1], red[2], blue[0], blue[1], blue[2]))
	conn.commit()

init_database()
