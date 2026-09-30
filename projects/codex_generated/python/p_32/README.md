# GitHub Repository Analyzer

Fetches commit history from the GitHub API to summarize commit trends, code churn, and contributor activity over a configurable date range.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python github_analyzer.py owner/repo --token YOUR_GITHUB_TOKEN --since 2023-06-01 --until 2023-08-31 --output report.json
```

Arguments:
- `repository`: Repo in `owner/name` form (e.g., `torvalds/linux`).
- `--token`: GitHub personal access token (otherwise uses `GITHUB_TOKEN` env or unauthenticated requests).
- `--since` / `--until`: ISO dates bounding the analysis window (default last 90 days).
- `--output`: Optional JSON output path.

### Sample Output
Console report includes total commits, additions/deletions, churn, top contributors, and daily commit activity. The JSON report (if requested) contains the same data in machine-readable form.

> **Note:** GitHub's API rate limits unauthenticated requests to 60/hour. Provide a token for higher limits.
