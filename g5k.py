from utils import *

############################# DB #####################################
def create_site_table(db, site):
	print (site)
	db.execute(f"""
		CREATE TABLE IF NOT EXISTS "{site}" (
			cluster TEXT PRIMARY KEY,
			ip TEXT NOT NULL
		)
	""")
	db.commit()

def print_site_table(db, site):
	cursor = db.cursor()
	cursor.execute(f'SELECT * FROM "{site}"')

	rows = cursor.fetchall()

	for row in rows:
		print(row)

def add_cluster(db, site, cluster, ip):
	db.execute(
		f'INSERT INTO "{site}" (cluster, ip) VALUES (?, ?)',
		(cluster, ip)
	)
	db.commit()
	print(f"{cluster} added.")

def delete_cluster(db, site, cluster):
	db.execute(
		f'DELETE FROM "{site}" WHERE cluster = ?',
		(cluster,)
	)
	db.commit()
	print(f"{cluster} deleted.")

def update_cluster(db, site, old_cluster, new_cluster, ip):
	db.execute(f"""
		UPDATE {site}
		SET cluster = ?, ip = ?
		WHERE cluster = ?
	""", (new_cluster, ip, old_cluster))

	db.commit()
	print(f"{new_cluster} updated.")

############################# PARSING #####################################
def	print_usage():
	print(f"{RED}Usage:")
	print("  python g5k.py <site> ADD <cluster> <ip>")
	print("  python g5k.py <site> DELETE <cluster>")
	print("  python g5k.py <site> UPDATE <old_cluster> <new_cluster> <new_ip>")
	print("  python g5k.py <site> PRINT")
	print(RESET, end="")

def check_site_name(site):
	if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", site):
		raise ValueError(f"{RED}Invalid site name{RESET}")

############################# MAIN #####################################
def main():
	try:
		size = len(sys.argv) 
		if size < 3:
			raise UsageError("missing required argument")

		site = sys.argv[1].lower()
		operation = sys.argv[2].upper()
		cluster = None

		if size == 3 and operation != "PRINT":
			raise UsageError("missing required argument")
		elif size > 3:
			cluster = sys.argv[3].lower()

		db = connect_db()

		check_site_name(site)
		create_site_table(db, site)

		if operation == "ADD":
			if size < 5:
				raise UsageError("missing required argument")
			ipaddress.ip_address(sys.argv[4])
			add_cluster(db, site, cluster, sys.argv[4])

		elif operation == "DELETE":
			delete_cluster(db, site, cluster)

		elif operation == "UPDATE":
			if size < 6:
				raise UsageError("missing required argument")
			check_site_name(sys.argv[4])
			ipaddress.ip_address(sys.argv[5])
			update_cluster(
				db,
				site,
				cluster,				# old name
				sys.argv[4].lower(),	# new name
				sys.argv[5]				# ip
			)

		elif operation == "PRINT":
			print_site_table(db, site)

		else:
			print_usage()

		db.close()

	except UsageError as e:
		print(f"{RED}usage error: {e}{RESET}")
		print_usage()

	except Exception as e:
		print(f"{RED}Error: {e}{RESET}")



if __name__ == "__main__":
	main()