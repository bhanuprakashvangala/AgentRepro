# Log Analyzer

Parses web server logs with a configurable regular expression, surfaces error patterns and anomalies, computes response-time statistics, and generates a matplotlib visualization.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python log_analyzer.py \
  --logs /path/to/access.log \
  --report summary.json \
  --plot metrics.png
```

- `--logs`: Single log file or directory of `.log` files (recursively scanned).
- `--pattern`: Custom regex with named groups (`timestamp`, `status`, `path`, `response_time`) if your format differs.
- `--time-format`: `datetime.strptime` format string for the timestamp (default Apache/Nginx `%d/%b/%Y:%H:%M:%S %z`).
- `--time-bucket`: Aggregate metrics per `minute` (default) or `hour`.

Outputs:
1. `summary.json` – totals, error rates, top failing endpoints, and high-latency anomalies.
2. `metrics.png` – dual-panel chart showing response time/error rate over time and status-code distribution.
