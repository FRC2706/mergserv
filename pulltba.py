#!/usr/bin/python3

# Nathan Gill, Team 2706: Merge Robotics

# Things to be pulled from TBA:
#   Competition codes, names
#   Matches (teams, number)

# Imports
import sys
import urllib.request
import json
import database

# Constants
baseurl = "https://www.thebluealliance.com/api/v3/"
apikey = ""

# Read TBA API key from file
try:
    with open("TBA.key") as f:
        apikey = f.read().strip()
        print("Using API key `%s`" % apikey)
except:
    print("The `TBA.key` file is missing, please create that file and put your TBA API key inside.")
    sys.exit(1)

# Generic request function
def get(url, headers):
    r = urllib.request.Request(baseurl+url)
    r.add_header('User-Agent', "Mergserv")
    r.add_header('X-TBA-Auth-Key', apikey)
    for k,v in headers.items():
        r.add_headers(k, v)

    try:
        response = urllib.request.urlopen(r).read().decode('utf-8')
        return json.loads(response)
    except Exception as e:
        print(e)
        return False

# Make status request to verify key and get current season
status = get("status", {})
if not status:
    print("There was an error making a request. This is most likely due to having an incorrect API key.")
    sys.exit(1)

# Inform the user
current_season = status['current_season']
print("Current season is %s" % current_season)

# Make request
events = get("events/%s" % current_season, {})
if not events:
    print("There was an error getting the events list.")
    sys.exit(1)

# Inform the user
print("Found %d events for the %s season" % (len(events), current_season))

for event in events:
    # Write event to database
    database.insert_competition(event['key'], current_season)
    print("pushed event %s" % event['key'])
