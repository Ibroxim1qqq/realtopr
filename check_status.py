from utils.db import db
import sys

req_id = "1769843807"
if len(sys.argv) > 1:
    req_id = sys.argv[1]

print(f"Checking request {req_id}...")
req = db.get_request(req_id)
if req:
    print(f"Status: {req[6]}") # Index 6 is status
else:
    print("Request not found")
