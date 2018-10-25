import sqlite3

DATABASE = "merg.db"

conn = sqlite3.connect(DATABASE)
db = conn.cursor()
init_database()

def init_database():
	db.execute("CREATE TABLE IF NOT EXISTS events (DATETIME sync_time DEFAULT NOW(), VARCHAR(5) type NOT NULL, UNSIGNED SMALLINT team_number NOT NULL, UNSIGNED TINYINT match_number NOT NULL, UNSIGNED TINYINT start_time NOT NULL, UNSIGNED TINYINT end_time NOT NULL, VARCHAR(64) extra NOT NULL, VARCHAR(16) scout_name NOT NULL, UNSIGNED SMALLINT scout_team NOT NULL, TEXT signature NOT NULL)")
	db.execute("CREATE TABLE IF NOT EXISTS matches (UNSIGNED TINYINT match_number PRIMARY KEY, VARCHAR(16) competition NOT NULL, UNSIGNED TINYINT blue1 NOT NULL, UNSIGNED TINYINT blue2 NOT NULL, UNSIGNED TINYINT blue2 NOT NULL, UNSIGNED TINYINT red1 NOT NULL, UNSIGNED TINYINT red2 NOT NULL, UNSIGNED TINYINT red3 NOT NULL, UNSIGNED SMALLINT final_score_blue, UNSIGNED SMALLINT final_score_red")
	db.execute("CREATE TABLE IF NOT EXISTS competitions (VARCHAR(16) competition PRIMARY KEY, UNSIGNED SMALLINT year NOT NULL)")
	db.execute("CREATE TABLE IF NOT EXISTS scouts (VARCHAR(16) scout_name PRIMARY KEY, UNSIGNED TINYINT team NOT NULL, DATETIME time_registered NOT NULL, ????? signature NOT NULL)")
	db.execute("CREATE TABLE IF NOT EXISTS teams (UNSIGNED TINYINT team_number PRIMARY KEY, TEXT public_key NOT NULL, TEXT signature NOT NULL)")

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
