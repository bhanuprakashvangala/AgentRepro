# Network Port Scanner with Service Detection

Scans IP addresses and networks for open ports, verifies access via raw sockets, and performs service fingerprinting with Nmap.

## Prerequisites
- Python 3.9+
- `nmap` command-line tool installed and available on `PATH` (e.g., `sudo apt install nmap` or `brew install nmap`).

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Scan a CIDR block across common ports
```bash
python port_scanner.py --targets 192.168.1.0/24 --ports 22,80,443 --report scan.json
```

### Scan specific hosts and port range, output Markdown report
```bash
python port_scanner.py \
  --targets 10.0.0.5 example.com \
  --ports 1-1024 \
  --timeout 1.5 \
  --workers 16 \
  --format markdown \
  --report security_report.md
```

Key options:
- `--targets`: One or more IPs, hostnames, or CIDR ranges.
- `--ports`: Comma-separated ports/ranges (default `22,80,443,3389`).
- `--timeout`: Socket connection timeout in seconds.
- `--workers`: Concurrent host scans.
- `--format`: Report format (`json` or `markdown`).
- `--report`: Output path for the security report.

The tool first confirms open ports using `socket` connections, then runs `nmap -sV` via `python-nmap` on confirmed ports to gather service names and versions. Results are summarized on stdout and written to the chosen report file.
