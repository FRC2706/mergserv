# MergServ JSON API
The MergServ JSON API runs on port 9999. The client should first open a TCP socket and send their JSON request, and the server will then send a response (after which the socket will be closed).

TODO: Encryption

TODO: Event/match/competition JSON format

## Response codes
OK/Success: `"ok"`

API version mismatch: `"version_mismatch"`

Invalid request type: `"invalid"`

Unauthorized (usually due to broken crypto): `"unauthorized"`

Unknown/unspecified error: `"unknown"`

## Request/response templates
All messages will be in this format, regardless of any additional data encoded in the message:

Basic request format: `{"version_major": API_VERSION_MAJOR, "version_minor": API_VERSION_MINOR, "type": REQUEST_TYPE}`

Basic response format: `{"version_major": API_VERSION_MAJOR, "version_minor": API_VERSION_MINOR, "type": RESPONSE_TYPE}`

### Push events
Request: `"push"`

Extra: `{"events": [EVENTS]}`

### Pull events
Request: `"pull"`

Extra: `{"last_sync": LAST_SYNC_TIME}`

Response: `{"events": [EVENTS]}`

### Push match scores
Request: `"push_scores"

TODO: This

### Pull match scores
Request: `"pull_scores"`

Extra: `{"last_match": LAST_SYNCED_MATCH, "competition": COMPETITION}`. Note that `LAST_SYNCED_MATCH` is the latest match for which you've received scores from the server.

Response: `{"matches": [MATCHES]}`

### List all matches in competition
Request: `"dump_matches"`

Extra: `{"competition": COMPETITION}`

Response: `{"matches": [MATCHES]}`

### List all competitions this year
Request: `"list_comps"`

Extra: `{"year": YEAR}`

Response: `{"competitions": [COMPETITIONS]}`
