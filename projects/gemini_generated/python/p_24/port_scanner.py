import nmap
import argparse
import socket
import threading
import time

# --- Dummy Server for Reproducible Demo ---
# This server will run in the background to ensure there is an open port to find.
DUMMY_SERVER_HOST = '127.0.0.1'
DUMMY_SERVER_PORT = 12345

def start_dummy_server(stop_event):
    """A simple TCP server that listens on a port and sends a welcome message."""
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(1.0) # Timeout to allow checking the stop_event
        server_socket.bind((DUMMY_SERVER_HOST, DUMMY_SERVER_PORT))
        server_socket.listen(1)
        print(f"[INFO] Dummy server started on {DUMMY_SERVER_HOST}:{DUMMY_SERVER_PORT}")

        while not stop_event.is_set():
            try:
                conn, addr = server_socket.accept()
                with conn:
                    conn.sendall(b'Welcome to the dummy server!\n')
            except socket.timeout:
                continue # Loop to check stop_event again
    except Exception as e:
        print(f"[ERROR] Dummy server failed: {e}")
    finally:
        server_socket.close()
        print("[INFO] Dummy server stopped.")

# --- Core Scanner Logic ---
def scan_ports(target, ports):
    """Uses python-nmap to scan a target for open ports and services."""
    print(f"\nScanning target {target} for ports: {ports}...")
    nm = nmap.PortScanner()
    try:
        # -sV: Probe open ports to determine service/version info
        # -T4: Aggressive timing template for faster scans
        nm.scan(target, ports, arguments='-sV -T4')
        return nm
    except nmap.PortScannerError:
        print("\n[ERROR] Nmap not found on your system.")
        print("Please install Nmap and ensure it is in your system's PATH.")
        print("Download from: https://nmap.org/download.html")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during the scan: {e}")
        return None

def generate_report(scanner, target):
    """Prints a formatted report of the scan results."""
    print(f"\n--- Security Scan Report for {target} ---")
    if not scanner.all_hosts():
        print("Host seems to be down or not responding.")
        return

    for host in scanner.all_hosts():
        print(f"Host: {host} ({scanner[host].hostname()})")
        print(f"State: {scanner[host].state()}")
        
        for proto in scanner[host].all_protocols():
            print("----------")
            print(f"Protocol: {proto}")

            ports = scanner[host][proto].keys()
            sorted_ports = sorted(ports)

            if not sorted_ports:
                print("No open ports found for this protocol.")
                continue

            for port in sorted_ports:
                port_info = scanner[host][proto][port]
                print(f"  Port: {port}")
                print(f"    State:   {port_info['state']}")
                if port_info['state'] == 'open':
                    print(f"    Service: {port_info['name']}")
                    print(f"    Product: {port_info['product']}")
                    print(f"    Version: {port_info['version']}")
    print("\n--- End of Report ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Network port scanner with service detection.")
    parser.add_argument("-t", "--target", default="127.0.0.1", help="Target IP address to scan (default: 127.0.0.1).")
    parser.add_argument("-p", "--ports", default=f"22-1024,{DUMMY_SERVER_PORT}", help=f"Port range to scan (e.g., 1-1024, default: 22-1024,{DUMMY_SERVER_PORT}).")
    args = parser.parse_args()

    # Start the dummy server in a background thread for the demo
    stop_event = threading.Event()
    server_thread = threading.Thread(target=start_dummy_server, args=(stop_event,))
    server_thread.start()
    time.sleep(1) # Give the server a moment to start up

    try:
        scan_results = scan_ports(args.target, args.ports)
        if scan_results:
            generate_report(scan_results, args.target)
    finally:
        # Cleanly shut down the dummy server
        stop_event.set()
        server_thread.join()
