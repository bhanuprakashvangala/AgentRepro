#!/usr/bin/env python3
"""Network port scanner with service detection using socket and python-nmap."""

from __future__ import annotations

import argparse
import concurrent.futures
import ipaddress
import json
import socket
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import nmap

DEFAULT_PORTS = "22,80,443,3389"


@dataclass
class PortFinding:
    port: int
    state: str
    service: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    extrainfo: Optional[str] = None


@dataclass
class HostReport:
    host: str
    open_ports: List[PortFinding]
    scan_duration: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan IP ranges for open ports and detect running services")
    parser.add_argument("--targets", nargs="+", help="IP addresses, hostnames, or CIDR ranges to scan")
    parser.add_argument(
        "--ports",
        default=DEFAULT_PORTS,
        help="Ports to scan (e.g., '22,80,443' or '1-1024'). Default: %(default)s",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Socket connection timeout in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=32,
        help="Number of concurrent host scans (default: 32)",
    )
    parser.add_argument(
        "--report",
        default="scan_report.json",
        help="Path to write the security report (default: scan_report.json)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Report output format (default: json)",
    )
    return parser.parse_args()


def expand_targets(targets: Iterable[str]) -> List[str]:
    expanded: List[str] = []
    for target in targets:
        target = target.strip()
        if not target:
            continue
        try:
            if "/" in target:
                network = ipaddress.ip_network(target, strict=False)
                expanded.extend(str(host) for host in network.hosts())
            else:
                ipaddress.ip_address(target)  # validates IP
                expanded.append(target)
        except ValueError:
            # Treat as hostname
            expanded.append(target)
    return sorted(set(expanded))


def parse_ports(port_spec: str) -> List[int]:
    ports: List[int] = []
    for part in port_spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_str, end_str = part.split("-", 1)
            start = int(start_str)
            end = int(end_str)
            if start > end:
                start, end = end, start
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    unique_ports = sorted(set(port for port in ports if 0 < port <= 65535))
    if not unique_ports:
        raise ValueError("No valid ports specified")
    return unique_ports


def socket_check(host: str, port: int, timeout: float) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False


def service_detection(host: str, ports: List[int]) -> Dict[int, PortFinding]:
    findings: Dict[int, PortFinding] = {}
    if not ports:
        return findings
    scanner = nmap.PortScanner()
    port_spec = ",".join(str(port) for port in ports)
    try:
        result = scanner.scan(hosts=host, ports=port_spec, arguments="-sV")
    except nmap.PortScannerError as exc:
        print(f"Warning: nmap scan failed for {host}: {exc}", file=sys.stderr)
        return findings

    host_data = result.get("scan", {}).get(host, {})
    tcp_data = host_data.get("tcp", {})
    for port, data in tcp_data.items():
        findings[port] = PortFinding(
            port=port,
            state=data.get("state", "unknown"),
            service=data.get("name"),
            product=data.get("product"),
            version=data.get("version"),
            extrainfo=data.get("extrainfo"),
        )
    return findings


def scan_host(host: str, ports: List[int], timeout: float) -> HostReport:
    start = time.time()
    open_ports: List[int] = []
    for port in ports:
        if socket_check(host, port, timeout):
            open_ports.append(port)
    service_details = service_detection(host, open_ports)
    findings: List[PortFinding] = []
    for port in open_ports:
        detail = service_details.get(port)
        if detail:
            findings.append(detail)
        else:
            findings.append(PortFinding(port=port, state="open"))
    duration = time.time() - start
    return HostReport(host=host, open_ports=sorted(findings, key=lambda f: f.port), scan_duration=duration)


def generate_report(host_reports: List[HostReport], ports: List[int], report_format: str) -> Dict[str, object]:
    total_open_ports = sum(len(report.open_ports) for report in host_reports)
    hosts_with_open = [report for report in host_reports if report.open_ports]
    summary = {
        "scanned_hosts": len(host_reports),
        "scanned_ports": ports,
        "hosts_with_open_ports": len(hosts_with_open),
        "total_open_ports": total_open_ports,
    }
    report_data = {
        "summary": summary,
        "hosts": [
        {
            "host": report.host,
            "scan_duration_seconds": round(report.scan_duration, 2),
            "open_ports": [
                {
                    "port": finding.port,
                    "state": finding.state,
                    "service": finding.service,
                    "product": finding.product,
                    "version": finding.version,
                    "extrainfo": finding.extrainfo,
                }
                for finding in report.open_ports
            ],
        }
        for report in host_reports
        ],
    }

    if report_format == "json":
        return report_data

    # Markdown report
    lines: List[str] = []
    lines.append("# Port Scan Report")
    lines.append("")
    lines.append(f"**Scanned hosts:** {summary['scanned_hosts']}")
    lines.append(f"**Ports:** {', '.join(str(p) for p in ports)}")
    lines.append(f"**Hosts with open ports:** {summary['hosts_with_open_ports']}")
    lines.append(f"**Total open ports:** {summary['total_open_ports']}")
    lines.append("")

    for report in host_reports:
        lines.append(f"## Host {report.host}")
        lines.append("")
        lines.append(f"_Scan duration: {report.scan_duration:.2f} seconds_")
        lines.append("")
        if not report.open_ports:
            lines.append("No open ports detected.")
            lines.append("")
            continue
        lines.append("| Port | State | Service | Product | Version | Extra Info | Scan Time (s) |")
        lines.append("|------|-------|---------|---------|---------|-------------|---------------|")
        for finding in report.open_ports:
            lines.append(
                f"| {finding.port} | {finding.state or ''} | {finding.service or ''} | "
                f"{finding.product or ''} | {finding.version or ''} | {finding.extrainfo or ''} | "
                f"{report.scan_duration:.2f} |"
            )
        lines.append("")

    return {"markdown": "\n".join(lines)}


def write_report(report_path: Path, report_data: Dict[str, object], report_format: str) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    if report_format == "json":
        report_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    else:
        report_path.write_text(report_data["markdown"], encoding="utf-8")


def main() -> None:
    args = parse_args()
    try:
        targets = expand_targets(args.targets)
        ports = parse_ports(args.ports)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not targets:
        print("No valid targets to scan.")
        sys.exit(0)

    print(f"Scanning {len(targets)} hosts across {len(ports)} ports...")
    host_reports: List[HostReport] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_to_host = {
            executor.submit(scan_host, host, ports, args.timeout): host for host in targets
        }
        for future in concurrent.futures.as_completed(future_to_host):
            host = future_to_host[future]
            try:
                report = future.result()
            except Exception as exc:  # pylint: disable=broad-except
                print(f"Warning: host {host} scan failed: {exc}", file=sys.stderr)
            else:
                host_reports.append(report)
                if report.open_ports:
                    open_ports_str = ", ".join(str(f.port) for f in report.open_ports)
                    print(f"Host {host}: open ports -> {open_ports_str}")
                else:
                    print(f"Host {host}: no open ports detected")

    host_reports.sort(key=lambda r: r.host)
    report_data = generate_report(host_reports, ports, args.format)
    write_report(Path(args.report), report_data, args.format)
    print(f"Report written to {args.report}")


if __name__ == "__main__":
    main()
