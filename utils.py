import re
import sys
import sqlite3
import ipaddress


# PARSE
RED = "\033[91m"
RESET = "\033[0m"

class UsageError(Exception):
    pass

# FILES
def	write_in_file(file, data):
	with open(file, "w") as f:
		f.write(f"{data}")
	f.close()

# DB 
DB_FILE = "g5k.db"

def connect_db():
	return sqlite3.connect(DB_FILE)