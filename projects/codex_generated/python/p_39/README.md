# System Resource Monitor

Monitors CPU, memory, and disk usage using `psutil`, logs metrics to a file, and emits threshold-based alerts.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python resource_monitor.py \
  --interval 5 \
  --log-file logs/resource_usage.log \
  --cpu-threshold 85 \
  --memory-threshold 90 \
  --disk-threshold 90 \
  --disk-mount /
```

Options:
- `--interval`: Sampling interval in seconds (default `5`).
- `--duration`: Optional total runtime in seconds; otherwise runs indefinitely.
- `--log-file`: Append-only JSON log of metrics.
- `--cpu-threshold`, `--memory-threshold`, `--disk-threshold`: Alert thresholds in percent.
- `--disk-mount`: Filesystem mount point to check disk usage (default `/`).

Console output shows live readings, while alerts are written to stderr. Logs accumulate JSON lines like:
```json
{"cpu_percent": 23.1, "memory_percent": 61.4, "disk_percent": 72.0, "timestamp": "2023-10-29T12:34:56.789Z"}
```
