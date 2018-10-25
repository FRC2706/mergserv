import sqlite3

DATABASE = "merg.db"

conn = sqlite3.connect(DATABASE)
db = conn.cursor()

def init_database():
	pass

def get_events(last_update_time):
	db.execute("SELECT * FROM events WHERE sync_time > ?", (last_update_time,))

def get_scores(competition_name, match_num):
	db.execute("SELECT * FROM matches WHERE competition_name=? AND match_number=?", (competition_name, match_num))

def dump_matches(competition_name):
	db.execute("SELECT * FROM matches WHERE competition=?", (competition,))
	return db.fetchall()

def list_competitions(year):
	db.execute("SELECT * FROM competitions WHERE year=?", (year,))
	return db.fetchall()

def push_events(events):
	for event in events:
		pass
