#!/usr/bin/env python3
"""Analyze server logs for error patterns, anomalies, and performance statistics."""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import matplotlib

matplotlib.use("Agg")  # Headless environments
import matplotlib.pyplot as plt

DEFAULT_PATTERN = r"^(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] \"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^\"]+)\" (?P<status>\d{3}) (?P<size>\S+) \"(?P<referrer>[^\"]*)\" \"(?P<agent>[^\"]*)\" (?P<response_time>[\d\.]+)$"
DEFAULT_TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


@dataclass
class LogRecord:
    timestamp: datetime
    status: int
    path: str
    response_time: float


@dataclass
class AnalysisResult:
    total_requests: int
    error_count: int
    error_rate: float
    average_response_time: float
    median_response_time: float
    p95_response_time: float
    status_distribution: Dict[str, int]
    top_error_paths: List[Dict[str, object]]
    anomalies: List[Dict[str, object]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse logs and generate insights")
    parser.add_argument("--logs", required=True, help="Log file or directory containing logs")
    parser.add_argument(
        "--pattern",
        default=DEFAULT_PATTERN,
        help="Regex pattern with named groups (default matches extended combined logs)",
    )
    parser.add_argument(
        "--time-format",
        default=DEFAULT_TIME_FORMAT,
        help="Datetime format for the timestamp group (default Apache/Nginx style)",
    )
    parser.add_argument(
        "--report",
        default="summary.json",
        help="Path to write JSON report",
    )
    parser.add_argument(
        "--plot",
        default="metrics.png",
        help="Path to save visualization PNG",
    )
    parser.add_argument(
        "--time-bucket",
        default="minute",
        choices=["minute", "hour"],
        help="Grouping bucket for response time chart",
    )
    return parser.parse_args()


def collect_log_files(path: Path) -> List[Path]:
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    if path.is_file():
        return [path]
    files = sorted(p for p in path.rglob("*.log"))
    if not files:
        raise ValueError(f"No .log files found in {path}")
    return files


def parse_line(line: str, pattern: re.Pattern, time_format: str) -> Optional[LogRecord]:
    match = pattern.match(line.strip())
    if not match:
        return None
    try:
        timestamp = datetime.strptime(match.group("timestamp"), time_format)
        status = int(match.group("status"))
        path = match.group("path")
        response_time = float(match.group("response_time"))
        return LogRecord(timestamp=timestamp, status=status, path=path, response_time=response_time)
    except (ValueError, KeyError):
        return None


def parse_logs(files: Iterable[Path], pattern: re.Pattern, time_format: str) -> List[LogRecord]:
    records: List[LogRecord] = []
    for file_path in files:
        with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                record = parse_line(line, pattern, time_format)
                if record:
                    records.append(record)
    if not records:
        raise ValueError("No log entries matched the provided pattern")
    return records


def percentile(values: List[float], percent: float) -> float:
    if not values:
        return math.nan
    if percent <= 0:
        return min(values)
    if percent >= 100:
        return max(values)
    sorted_vals = sorted(values)
    k = (len(sorted_vals) - 1) * (percent / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    d0 = sorted_vals[int(f)] * (c - k)
    d1 = sorted_vals[int(c)] * (k - f)
    return d0 + d1


def analyze(records: List[LogRecord]) -> AnalysisResult:
    total_requests = len(records)
    status_counter = Counter(str(r.status) for r in records)
    error_records = [r for r in records if r.status >= 400]
    error_count = len(error_records)
    error_rate = error_count / total_requests if total_requests else 0.0

    response_times = [r.response_time for r in records]
    avg_resp = statistics.fmean(response_times)
    median_resp = statistics.median(response_times)
    p95_resp = percentile(response_times, 95)

    error_path_counter = Counter(r.path for r in error_records)
    top_error_paths = [
        {"path": path, "count": count, "rate": count / total_requests}
        for path, count in error_path_counter.most_common(5)
    ]

    anomalies = detect_anomalies(records, response_times)

    return AnalysisResult(
        total_requests=total_requests,
        error_count=error_count,
        error_rate=error_rate,
        average_response_time=avg_resp,
        median_response_time=median_resp,
        p95_response_time=p95_resp,
        status_distribution=dict(status_counter),
        top_error_paths=top_error_paths,
        anomalies=anomalies,
    )


def detect_anomalies(records: List[LogRecord], response_times: List[float]) -> List[Dict[str, object]]:
    if not response_times:
        return []
    mean = statistics.fmean(response_times)
    stdev = statistics.pstdev(response_times)
    threshold = mean + 3 * stdev if stdev > 0 else max(response_times)
    anomalies = [
        {"timestamp": rec.timestamp.isoformat(), "path": rec.path, "status": rec.status, "response_time": rec.response_time}
        for rec in records
        if rec.response_time >= threshold
    ]
    return anomalies[:20]


def build_time_series(records: List[LogRecord], bucket: str) -> Dict[datetime, Dict[str, float]]:
    aggregates: Dict[datetime, Dict[str, float]] = defaultdict(lambda: {"total": 0, "errors": 0, "sum_response": 0.0})
    for rec in records:
        if bucket == "hour":
            key = rec.timestamp.replace(minute=0, second=0, microsecond=0)
        else:
            key = rec.timestamp.replace(second=0, microsecond=0)
        agg = aggregates[key]
        agg["total"] += 1
        agg["sum_response"] += rec.response_time
        if rec.status >= 400:
            agg["errors"] += 1
    return dict(sorted(aggregates.items(), key=lambda item: item[0]))


def plot_metrics(records: List[LogRecord], result: AnalysisResult, output_path: Path, bucket: str) -> None:
    series = build_time_series(records, bucket)
    if not series:
        return

    times = list(series.keys())
    avg_response = [values["sum_response"] / values["total"] for values in series.values()]
    error_rate = [values["errors"] / values["total"] if values["total"] else 0 for values in series.values()]

    status_codes, counts = zip(*sorted(result.status_distribution.items(), key=lambda item: item[0]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(times, avg_response, marker="o", color="#1f77b4", label="Avg response time")
    ax1.plot(times, error_rate, marker="x", color="#d62728", label="Error rate")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Seconds / Rate")
    ax1.set_title("Response Time & Error Rate")
    ax1.legend()
    fig.autofmt_xdate()

    ax2.bar(status_codes, counts, color="#9467bd")
    ax2.set_xlabel("Status code")
    ax2.set_ylabel("Count")
    ax2.set_title("Status distribution")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def save_report(result: AnalysisResult, output_path: Path) -> None:
    report = {
        "total_requests": result.total_requests,
        "error_count": result.error_count,
        "error_rate": result.error_rate,
        "average_response_time": result.average_response_time,
        "median_response_time": result.median_response_time,
        "p95_response_time": result.p95_response_time,
        "status_distribution": result.status_distribution,
        "top_error_paths": result.top_error_paths,
        "anomalies": result.anomalies,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()

    pattern = re.compile(args.pattern)
    log_files = collect_log_files(Path(args.logs))
    records = parse_logs(log_files, pattern, args.time_format)
    analysis = analyze(records)

    save_report(analysis, Path(args.report))
    plot_metrics(records, analysis, Path(args.plot), args.time_bucket)

    print(f"Processed {len(records)} log entries across {len(log_files)} file(s).")
    print(f"Total requests: {analysis.total_requests}")
    print(f"Error rate: {analysis.error_rate:.2%}")
    print(f"Report saved to {Path(args.report).resolve()}")
    print(f"Plot saved to {Path(args.plot).resolve()}")


if __name__ == "__main__":
    main()
