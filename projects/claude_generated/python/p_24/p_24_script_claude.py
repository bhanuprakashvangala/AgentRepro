#!/usr/bin/env python3
"""
Network Port Scanner with Service Detection
For authorized security testing and network administration only.
"""

import socket
import nmap
import argparse
import ipaddress
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import sys

class PortScanner:
    def __init__(self, timeout=1, max_workers=50):
        self.timeout = timeout
        self.max_workers = max_workers
        self.nm = nmap.PortScanner()

    def scan_port(self, ip, port):
        """Scan a single port on a given IP address."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return port if result == 0 else None
        except socket.error:
            return None

    def basic_scan(self, ip, ports):
        """Perform basic port scan using sockets."""
        open_ports = []
        print(f"[*] Scanning {ip}...")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.scan_port, ip, port): port
                      for port in ports}

            for future in as_completed(futures):
                port = future.result()
                if port:
                    open_ports.append(port)
                    print(f"  [+] Port {port} is open")

        return sorted(open_ports)

    def detect_services(self, ip, ports):
        """Detect services running on open ports using nmap."""
        if not ports:
            return {}

        print(f"[*] Detecting services on {ip}...")
        port_string = ','.join(map(str, ports))

        try:
            self.nm.scan(ip, port_string, arguments='-sV --version-intensity 5')
            services = {}

            if ip in self.nm.all_hosts():
                for proto in self.nm[ip].all_protocols():
                    ports_data = self.nm[ip][proto]
                    for port in ports_data:
                        service_info = {
                            'port': port,
                            'state': ports_data[port]['state'],
                            'service': ports_data[port].get('name', 'unknown'),
                            'product': ports_data[port].get('product', ''),
                            'version': ports_data[port].get('version', ''),
                            'extrainfo': ports_data[port].get('extrainfo', ''),
                            'cpe': ports_data[port].get('cpe', '')
                        }
                        services[port] = service_info
                        print(f"  [+] Port {port}: {service_info['service']} "
                              f"{service_info['product']} {service_info['version']}")

            return services
        except Exception as e:
            print(f"  [!] Service detection failed: {e}")
            return {}

    def scan_network(self, ip_range, port_range):
        """Scan multiple IPs in a network range."""
        results = {}

        try:
            network = ipaddress.ip_network(ip_range, strict=False)
            ips = [str(ip) for ip in network.hosts()] if network.num_addresses > 2 else [str(network.network_address)]
        except ValueError:
            # Single IP address
            ips = [ip_range]

        print(f"\n[*] Starting scan of {len(ips)} host(s)")
        print(f"[*] Port range: {port_range[0]}-{port_range[-1]}")
        print(f"[*] Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        for ip in ips:
            try:
                # Check if host is up
                if not self.is_host_up(ip):
                    print(f"[!] Host {ip} appears to be down, skipping...")
                    continue

                # Basic port scan
                open_ports = self.basic_scan(ip, port_range)

                if open_ports:
                    # Service detection on open ports
                    services = self.detect_services(ip, open_ports)
                    results[ip] = {
                        'open_ports': open_ports,
                        'services': services,
                        'scan_time': datetime.now().isoformat()
                    }
                else:
                    print(f"[!] No open ports found on {ip}")

                print()  # Blank line between hosts

            except Exception as e:
                print(f"[!] Error scanning {ip}: {e}")

        return results

    def is_host_up(self, ip):
        """Quick check if host is responsive."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            # Try to connect to common ports
            for port in [80, 443, 22, 21]:
                result = sock.connect_ex((ip, port))
                if result == 0:
                    sock.close()
                    return True
            sock.close()
            return False
        except:
            return True  # Assume up if check fails

class ReportGenerator:
    @staticmethod
    def generate_report(results, output_file=None):
        """Generate a security report from scan results."""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("NETWORK PORT SCANNER - SECURITY REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Total Hosts Scanned: {len(results)}")
        report_lines.append("=" * 80)
        report_lines.append("")

        if not results:
            report_lines.append("[!] No open ports found on any scanned hosts.")
            report_text = "\n".join(report_lines)
            print(report_text)
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(report_text)
            return

        # Summary
        total_open_ports = sum(len(data['open_ports']) for data in results.values())
        report_lines.append("SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(f"Hosts with open ports: {len(results)}")
        report_lines.append(f"Total open ports found: {total_open_ports}")
        report_lines.append("")

        # Detailed findings
        report_lines.append("DETAILED FINDINGS")
        report_lines.append("-" * 80)

        for ip, data in results.items():
            report_lines.append(f"\nHost: {ip}")
            report_lines.append(f"Scan Time: {data['scan_time']}")
            report_lines.append(f"Open Ports: {len(data['open_ports'])}")
            report_lines.append("")

            for port in data['open_ports']:
                service_info = data['services'].get(port, {})
                report_lines.append(f"  Port {port}/tcp")
                report_lines.append(f"    State: {service_info.get('state', 'open')}")
                report_lines.append(f"    Service: {service_info.get('service', 'unknown')}")

                if service_info.get('product'):
                    report_lines.append(f"    Product: {service_info['product']}")
                if service_info.get('version'):
                    report_lines.append(f"    Version: {service_info['version']}")
                if service_info.get('extrainfo'):
                    report_lines.append(f"    Extra Info: {service_info['extrainfo']}")

                report_lines.append("")

        # Security recommendations
        report_lines.append("=" * 80)
        report_lines.append("SECURITY RECOMMENDATIONS")
        report_lines.append("-" * 80)
        report_lines.append("")
        report_lines.append("1. Review all open ports and ensure they are necessary for business operations")
        report_lines.append("2. Close or firewall any unnecessary ports")
        report_lines.append("3. Update all services to the latest secure versions")
        report_lines.append("4. Implement strong authentication for all exposed services")
        report_lines.append("5. Monitor these ports regularly for unauthorized changes")
        report_lines.append("6. Consider implementing network segmentation")
        report_lines.append("7. Enable logging and monitoring for all exposed services")
        report_lines.append("")
        report_lines.append("=" * 80)

        report_text = "\n".join(report_lines)
        print(report_text)

        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"\n[+] Report saved to: {output_file}")

            # Also save JSON version
            json_file = output_file.replace('.txt', '.json')
            with open(json_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"[+] JSON data saved to: {json_file}")

def parse_port_range(port_string):
    """Parse port range string (e.g., '1-1000' or '80,443,8080')."""
    ports = []

    if ',' in port_string:
        # Comma-separated ports
        for p in port_string.split(','):
            if '-' in p:
                start, end = map(int, p.split('-'))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(p))
    elif '-' in port_string:
        # Port range
        start, end = map(int, port_string.split('-'))
        ports = list(range(start, end + 1))
    else:
        # Single port
        ports = [int(port_string)]

    return ports

def main():
    parser = argparse.ArgumentParser(
        description='Network Port Scanner with Service Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s -t 192.168.1.1 -p 1-1000
  %(prog)s -t 192.168.1.0/24 -p 80,443,8080
  %(prog)s -t 10.0.0.1 -p 1-65535 -o report.txt
  %(prog)s -t 192.168.1.100 --common-ports

Note: This tool is for authorized security testing only.
Unauthorized port scanning may be illegal in your jurisdiction.
        '''
    )

    parser.add_argument('-t', '--target', required=True,
                        help='Target IP address or CIDR range (e.g., 192.168.1.1 or 192.168.1.0/24)')
    parser.add_argument('-p', '--ports',
                        help='Port range to scan (e.g., 1-1000, 80,443, or 1-65535)')
    parser.add_argument('--common-ports', action='store_true',
                        help='Scan only common ports (faster)')
    parser.add_argument('-o', '--output',
                        help='Output report file (default: report.txt)')
    parser.add_argument('--timeout', type=float, default=1,
                        help='Socket timeout in seconds (default: 1)')
    parser.add_argument('--workers', type=int, default=50,
                        help='Number of concurrent workers (default: 50)')

    args = parser.parse_args()

    # Define common ports if requested
    if args.common_ports:
        common_ports = [20, 21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
                       993, 995, 1723, 3306, 3389, 5900, 8080, 8443]
        port_range = common_ports
    elif args.ports:
        port_range = parse_port_range(args.ports)
    else:
        # Default to common ports
        print("[!] No port range specified, using common ports")
        common_ports = [20, 21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
                       993, 995, 1723, 3306, 3389, 5900, 8080, 8443]
        port_range = common_ports

    output_file = args.output or 'scan_report.txt'

    print("\n" + "=" * 80)
    print("NETWORK PORT SCANNER WITH SERVICE DETECTION")
    print("=" * 80)
    print("WARNING: Only use this tool on networks you have permission to scan!")
    print("=" * 80 + "\n")

    try:
        scanner = PortScanner(timeout=args.timeout, max_workers=args.workers)
        results = scanner.scan_network(args.target, port_range)

        print("\n" + "=" * 80)
        print("SCAN COMPLETE")
        print("=" * 80 + "\n")

        ReportGenerator.generate_report(results, output_file)

    except KeyboardInterrupt:
        print("\n\n[!] Scan interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
