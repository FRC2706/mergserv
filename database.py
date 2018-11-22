import sqlite3

DATABASE = "merg.db"

def init_database():
	db.execute("CREATE TABLE events (sync_time DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, type VARCHAR(5) NOT NULL, team_number SMALLINT UNSIGNED NOT NULL, match_number TINYINT UNSIGNED NOT NULL, start_time TINYINT UNSIGNED NOT NULL, end_time TINYINT UNSIGNED NOT NULL, extra VARCHAR(64) NOT NULL, scout_name VARCHAR(16) NOT NULL, scout_team SMALLINT UNSIGNED NOT NULL, signature TEXT NOT NULL)")
	db.execute("CREATE TABLE matches (match_number TINYINT UNSIGNED PRIMARY KEY NOT NULL, competition VARCHAR(16) NOT NULL, blue1 TINYINT UNSIGNED NOT NULL, blue2 TINYINT UNSIGNED NOT NULL, blue3 TINYINT UNSIGNED NOT NULL, red1 TINYINT UNSIGNED NOT NULL, red2 TINYINT UNSIGNED NOT NULL, red3 TINYINT UNSIGNED NOT NULL, final_score_blue SMALLINT UNSIGNED, final_score_red SMALLINT UNSIGNED)")
	db.execute("CREATE TABLE competitions (competition VARCHAR(16) PRIMARY KEY NOT NULL, year SMALLINT UNSIGNED NOT NULL)")
	db.execute("CREATE TABLE scouts (scout_name VARCHAR(16) PRIMARY KEY NOT NULL, team SMALLINT UNSIGNED NOT NULL, time_registered DATETIME NOT NULL, signature TEXT NOT NULL)")
	db.execute("CREATE TABLE teams (team_number TINYINT UNSIGNED PRIMARY KEY NOT NULL, public_key TEXT NOT NULL, signature TEXT NOT NULL)")

def get_events(last_update_time):
	db.execute("SELECT * FROM events WHERE sync_time > from_unixtime(?)", (last_update_time,))

def get_scores(competition_name, match_num):
	db.execute("SELECT * FROM matches WHERE competition_name=? AND match_number=?", (competition_name, match_num))

def dump_matches(competition_name):
	db.execute("SELECT * FROM matches WHERE competition=?", (competition,))
	return db.fetchall()

def list_competitions(year):
	db.execute("SELECT * FROM competitions WHERE year=?", (year,))
	return db.fetchall()

'''
Return codes:
0: Success
1: Unknown error
2: Invalid signature
'''
def push_events(events):
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
		# TODO: Verify signature
		stuff = (ev_type, team, match, start, end, success, scout_name, scout_team, signature)
		db.execute("INSERT INTO events (type, team_number, match_number, start_time, end_time, success, extra, scout_name, scout_team, signature) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", stuff)
	return 0

def push_scores(scores):
	for mscore in scores:
		stuff = (mscore["match_number"], mscore["blue_score"], mscore["red_score"])
		db.execute("UPDATE matches WHERE match_number=? AND blue_score IS NULL AND red_score IS NULL SET blue_score=? AND red_score=?", stuff)

conn = sqlite3.connect(DATABASE)
db = conn.cursor()
init_database()

