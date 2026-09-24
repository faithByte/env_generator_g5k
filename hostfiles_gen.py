import subprocess
from collections import defaultdict
from jinja2 import Template

from utils import *

hosts = defaultdict(list)
PATH = "/home/imarhesri/HPC-Cluster/inventories/"
MAKEFILE_PATH = "/home/imarhesri/Makefile"
# PATH = "./test/"

def parse_host(host):
	match = re.match(r'^([^-]+)-(\d+)', host)

	if not match:
		raise ValueError(f"Invalid hostname: {host}")

	return match.group(1), int(match.group(2))

def	get_hosts():
	process = subprocess.Popen(
		["oarprint", "host"],
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
		text=True,
		bufsize=1
	)

	for host in process.stdout:
		host = host.rstrip()
		name, index = parse_host(host)
		hosts[name].append(index)
	
	process.wait()

def	create_host_var(filename, ip):
	write_in_file(f"{PATH}/host_vars/{filename}.yml", f"ansible_host: {ip}\n")

def	create_host_file(all):
	template = Template(open("./templates/hosts.yml.j2").read())

	all = all.rsplit('\n', 1)
	output = template.render(
		nodes=all[0],
		master=all[1],
	)

	write_in_file(f"{PATH}/hosts.yml", output)

def	create_group_vars(site, master, ip):
	template = Template(open("./templates/all.yml.j2").read())

	network = ipaddress.ip_network(f"{ip}/20", strict=False)
	gateway = network.broadcast_address

	output = template.render(
		network=network,
		gateway=gateway,
		site=site,
		master_ip=ip
	)

	write_in_file(f"{PATH}/group_vars/all.yml", output)

	template = Template(open("./templates/cluster.yml.j2").read())

	output = template.render(
		master=f"{master}.{site}.grid5000.fr"
	)

	write_in_file(f"{PATH}/group_vars/cluster.yml", output)

def	create_makefile(master, site):
	template = Template(open("./templates/Makefile.j2").read())

	output = template.render(
		master=master,
		site=site,
	)

	write_in_file(f"{MAKEFILE_PATH}", output)

def	get_host_ip(site):
	db = connect_db()

	host = None
	ip = None
	index = 0

	all = ""

	for host in hosts:
		cursor = db.execute(
			f"SELECT * FROM {site} WHERE cluster = ?",
			(host,)
		)

		data = cursor.fetchone()
		for index in hosts[host]:
			# check =======================================================
			ip_data = int(data[1].rsplit(".", 1))
			ip = ip_data[0] + f".{index + ip_data[1]}"
			create_host_var(f"{host}-{index}", ip)
			all += f"      {host}-{index}:\n"

	if ip == None:
		return

	create_host_var("nfs", ip)
	create_host_file(all)
	create_group_vars(site, f"{host}-{index}", ip)
	create_makefile(f"{host}-{index}", site)
	
def	print_usage():
	print(f"{RED}Usage:")
	print("  python hostfiles_gen.py <site> {RESET}")

def main():
	try:
			
		if len(sys.argv) < 2:
			raise UsageError("ERROR: missing required argument")
			
		site = sys.argv[1].lower()

		get_hosts()
		get_host_ip(site)

	except Exception as e:
		print(f"{RED}Error: {e}{RESET}")

	except UsageError as e:
		print(f"{RED}usage error: {e}{RESET}")
		print_usage()

if __name__ == "__main__":
	main()