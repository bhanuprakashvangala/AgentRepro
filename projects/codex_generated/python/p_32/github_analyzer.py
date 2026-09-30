#!/usr/bin/env python3
"""GitHub repository analyzer for commit trends, churn, and contributor stats."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

import requests

GITHUB_API = "https://api.github.com"
DEFAULT_WINDOW_DAYS = 90


@dataclass
class CommitStat:
    sha: str
    author: Optional[str]
    date: str
    additions: int
    deletions: int
    total: int


@dataclass
class ContributorSummary:
    author: str
    commits: int
    additions: int
    deletions: int
    churn: int


@dataclass
class RepositoryReport:
    repository: str
    analyzed_since: str
    analyzed_until: str
    total_commits: int
    total_additions: int
    total_deletions: int
    total_churn: int
    commits_per_day: Dict[str, int]
    top_contributors: List[ContributorSummary]


class GitHubAnalyzerError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze GitHub repo metrics (commit trends, churn, contributors)")
    parser.add_argument("repository", help="Repository in owner/name format")
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN"),
        help="GitHub personal access token (or set GITHUB_TOKEN env)",
    )
    parser.add_argument(
        "--since",
        help="Start date ISO 8601 (default: now - 90d)",
    )
    parser.add_argument(
        "--until",
        help="End date ISO 8601 (default: now)",
    )
    parser.add_argument(
        "--output",
        help="Optional path to save JSON report",
    )
    return parser.parse_args()


def parse_iso_date(value: Optional[str], default: dt.datetime) -> dt.datetime:
    if not value:
        return default
    try:
        return dt.datetime.fromisoformat(value)
    except ValueError as exc:
        raise GitHubAnalyzerError(f"Invalid date format: {value}") from exc


def request_json(url: str, token: Optional[str], params: Optional[Dict[str, str]] = None) -> Dict:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(url, headers=headers, params=params, timeout=15)
    if response.status_code == 403 and "rate limit" in response.text.lower():
        raise GitHubAnalyzerError("GitHub API rate limit exceeded. Provide a token or wait before retrying.")
    if response.status_code >= 400:
        raise GitHubAnalyzerError(f"GitHub API request failed ({response.status_code}): {response.text}")
    return response.json()


def fetch_commits(repo: str, token: Optional[str], since: dt.datetime, until: dt.datetime) -> List[CommitStat]:
    commits: List[CommitStat] = []
    page = 1
    while True:
        params = {
            "since": since.isoformat(),
            "until": until.isoformat(),
            "per_page": 100,
            "page": page,
        }
        data = request_json(f"{GITHUB_API}/repos/{repo}/commits", token, params=params)
        if not data:
            break
        for commit_data in data:
            sha = commit_data.get("sha")
            commit = commit_data.get("commit", {})
            author_data = commit_data.get("author") or {}
            stats = request_json(f"{GITHUB_API}/repos/{repo}/commits/{sha}", token)
            additions = stats.get("stats", {}).get("additions", 0)
            deletions = stats.get("stats", {}).get("deletions", 0)
            total = stats.get("stats", {}).get("total", additions + deletions)
            commits.append(
                CommitStat(
                    sha=sha,
                    author=author_data.get("login") or commit.get("author", {}).get("name"),
                    date=commit.get("author", {}).get("date"),
                    additions=additions,
                    deletions=deletions,
                    total=total,
                )
            )
        page += 1
    return commits


def aggregate_metrics(repo: str, commits: List[CommitStat], since: dt.datetime, until: dt.datetime) -> RepositoryReport:
    total_additions = sum(c.additions for c in commits)
    total_deletions = sum(c.deletions for c in commits)
    total_churn = total_additions + total_deletions
    commits_per_day: Dict[str, int] = Counter()
    contributor_stats: Dict[str, ContributorSummary] = {}

    for commit in commits:
        date = commit.date or ""
        day = date[:10]
        if day:
            commits_per_day[day] += 1
        if commit.author:
            entry = contributor_stats.get(commit.author)
            if entry is None:
                contributor_stats[commit.author] = ContributorSummary(
                    author=commit.author,
                    commits=1,
                    additions=commit.additions,
                    deletions=commit.deletions,
                    churn=commit.additions + commit.deletions,
                )
            else:
                entry.commits += 1
                entry.additions += commit.additions
                entry.deletions += commit.deletions
                entry.churn += commit.additions + commit.deletions

    top_contributors = sorted(contributor_stats.values(), key=lambda c: c.commits, reverse=True)[:10]

    return RepositoryReport(
        repository=repo,
        analyzed_since=since.isoformat(),
        analyzed_until=until.isoformat(),
        total_commits=len(commits),
        total_additions=total_additions,
        total_deletions=total_deletions,
        total_churn=total_churn,
        commits_per_day=dict(commits_per_day),
        top_contributors=top_contributors,
    )


def print_report(report: RepositoryReport) -> None:
    print(f"Repository: {report.repository}")
    print(f"Analyzed range: {report.analyzed_since} -> {report.analyzed_until}")
    print(f"Total commits: {report.total_commits}")
    print(f"Additions: {report.total_additions}")
    print(f"Deletions: {report.total_deletions}")
    print(f"Churn: {report.total_churn}")
    print("")
    print("Top contributors:")
    for contributor in report.top_contributors:
        print(
            f"  {contributor.author}: commits={contributor.commits}, "
            f"additions={contributor.additions}, deletions={contributor.deletions}, churn={contributor.churn}"
        )
    print("")
    print("Commit activity (per day):")
    for day in sorted(report.commits_per_day):
        print(f"  {day}: {report.commits_per_day[day]} commits")


def write_report(report: RepositoryReport, output: Path) -> None:
    payload = asdict(report)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Report saved to {output}")


def main() -> None:
    args = parse_args()
    token = args.token
    if not token:
        print("Warning: no GitHub token provided. You may hit rate limits.", file=sys.stderr)

    now = dt.datetime.utcnow()
    since_default = now - dt.timedelta(days=DEFAULT_WINDOW_DAYS)
    since = parse_iso_date(args.since, since_default)
    until = parse_iso_date(args.until, now)

    try:
        commits = fetch_commits(args.repository, token, since, until)
    except GitHubAnalyzerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    report = aggregate_metrics(args.repository, commits, since, until)
    print_report(report)

    if args.output:
        write_report(report, Path(args.output))


if __name__ == "__main__":
    main()
