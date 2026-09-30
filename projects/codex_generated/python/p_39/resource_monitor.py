#!/usr/bin/env python3
"""System resource monitor with threshold alerts and usage logging."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import psutil

DEFAULT_INTERVAL = 5
DEFAULT_LOG_PATH = Path("resource_usage.log")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor system resources and trigger alerts")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL, help="Sampling interval in seconds")
    parser.add_argument("--log-file", default=str(DEFAULT_LOG_PATH), help="Path to append JSON logs")
    parser.add_argument("--cpu-threshold", type=float, default=90.0, help="CPU usage alert threshold (%)")
    parser.add_argument("--memory-threshold", type=float, default=90.0, help="Memory usage alert threshold (%)")
    parser.add_argument("--disk-threshold", type=float, default=90.0, help="Disk usage alert threshold (%)")
    parser.add_argument(
        "--disk-mount",
        default="/",
        help="Disk mount point to monitor (default: /)",
    )
    parser.add_argument("--duration", type=int, help="Optional duration to run in seconds")
    return parser.parse_args()


def read_metrics(disk_mount: str) -> dict[str, float]:
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(disk_mount)
    metrics = {
        "cpu_percent": cpu,
        "memory_percent": memory.percent,
        "disk_percent": disk.percent,
        "timestamp": dt.datetime.utcnow().isoformat() + "Z",
    }
    return metrics


def log_metrics(log_path: Path, metrics: dict[str, float]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(metrics) + "\n")


def check_alerts(metrics: dict[str, float], thresholds: dict[str, float]) -> None:
    alerts: list[str] = []
    if metrics["cpu_percent"] >= thresholds["cpu"]:
        alerts.append(f"CPU usage high: {metrics['cpu_percent']:.1f}%")
    if metrics["memory_percent"] >= thresholds["memory"]:
        alerts.append(f"Memory usage high: {metrics['memory_percent']:.1f}%")
    if metrics["disk_percent"] >= thresholds["disk"]:
        alerts.append(f"Disk usage high ({thresholds['disk_mount']}): {metrics['disk_percent']:.1f}%")

    for alert in alerts:
        print(f"ALERT {metrics['timestamp']}: {alert}", file=sys.stderr)


def main() -> None:
    args = parse_args()
    log_path = Path(args.log_file)
    thresholds = {
        "cpu": args.cpu_threshold,
        "memory": args.memory_threshold,
        "disk": args.disk_threshold,
        "disk_mount": args.disk_mount,
    }

    start_time = time.monotonic()
    while True:
        metrics = read_metrics(args.disk_mount)
        log_metrics(log_path, metrics)

        print(
            f"{metrics['timestamp']} | CPU: {metrics['cpu_percent']:.1f}% | "
            f"Memory: {metrics['memory_percent']:.1f}% | Disk({args.disk_mount}): {metrics['disk_percent']:.1f}%"
        )

        check_alerts(metrics, thresholds)

        if args.duration is not None and time.monotonic() - start_time >= args.duration:
            break

        time.sleep(max(1, args.interval))


if __name__ == "__main__":
    main()
