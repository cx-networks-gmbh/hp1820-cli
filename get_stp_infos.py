import os
import sys
from lib.cli import Cli

# List of switch IPs
switch_ips = [
    "192.168.1.211",
    "192.168.1.212",
    "192.168.1.221",
    "192.168.1.222",
    "192.168.1.231",
    "192.168.1.232",
    "192.168.1.241",
    "192.168.1.242",
    "192.168.1.21",
    "192.168.1.22",
    "192.168.1.11",
    "192.168.1.12"
]

# Folder to save the output files
output_folder = "stp_info_outputs"
os.makedirs(output_folder, exist_ok=True)

# Credentials for the switches
username = "admin"
password = "PRG0815$"


def get_spanning_tree_info(ip):
    """Retrieve spanning tree information from a switch."""
    cli = Cli("http", ip)

    file_path = os.path.join(output_folder, f"{ip}.txt")
    if cli.login(username, password):
        tem = sys.stdout
        file_path = os.path.join(output_folder, f"{ip}.txt")
        sys.stdout = f = open(file_path, 'w')
        cli.showSpanningTreeStatus()
        print("\n\nLLDP:")
        cli.showLLDPRemotes()
        sys.stdout = tem
        f.close()
        cli.logout()
    else:
        raise Exception("Login failed")


def main():
    for ip in switch_ips:
        try:
            print(f"Processing switch {ip}...")
            stp_info = get_spanning_tree_info(ip)
            print(f"Saved spanning tree info for {ip}.")
        except Exception as e:
            print(f"Failed to process switch {ip}: {e}")
        else:
            # If no exception occurred, print success message
            print(
                f"Successfully retrieved and saved spanning tree info for {ip}.")


if __name__ == "__main__":
    main()
