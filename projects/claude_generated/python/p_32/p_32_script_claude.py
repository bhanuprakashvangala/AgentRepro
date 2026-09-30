"""
GitHub Repository Analyzer
Extracts metrics including commit history, trends, code churn, and contributor statistics.
"""

import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple
import json

try:
    from github import Github, GithubException
    from dateutil.relativedelta import relativedelta
except ImportError:
    print("Error: Required packages not installed.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


class GitHubAnalyzer:
    """Analyze GitHub repository metrics."""

    def __init__(self, token: str = None):
        """
        Initialize the analyzer.

        Args:
            token: GitHub personal access token (optional but recommended for higher rate limits)
        """
        self.github = Github(token) if token else Github()

    def analyze_repository(self, repo_name: str, months: int = 6) -> Dict:
        """
        Analyze a GitHub repository and extract comprehensive metrics.

        Args:
            repo_name: Repository in format "owner/repo"
            months: Number of months to analyze (default: 6)

        Returns:
            Dictionary containing all metrics
        """
        print(f"\n{'='*60}")
        print(f"Analyzing repository: {repo_name}")
        print(f"{'='*60}\n")

        try:
            repo = self.github.get_repo(repo_name)
        except GithubException as e:
            print(f"Error: Unable to access repository '{repo_name}'")
            print(f"Details: {e}")
            return {}

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)

        print(f"Repository: {repo.full_name}")
        print(f"Description: {repo.description}")
        print(f"Stars: {repo.stargazers_count}")
        print(f"Forks: {repo.forks_count}")
        print(f"Analysis period: {start_date.date()} to {end_date.date()}\n")

        # Gather metrics
        metrics = {
            'repository': repo_name,
            'analysis_date': end_date.isoformat(),
            'period_months': months,
            'basic_info': self._get_basic_info(repo),
            'commit_history': self._analyze_commits(repo, start_date, end_date),
            'code_churn': self._calculate_code_churn(repo, start_date, end_date),
            'contributors': self._analyze_contributors(repo, start_date, end_date),
            'trends': {}
        }

        # Calculate trends
        metrics['trends'] = self._calculate_trends(metrics['commit_history'])

        return metrics

    def _get_basic_info(self, repo) -> Dict:
        """Extract basic repository information."""
        return {
            'full_name': repo.full_name,
            'description': repo.description,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'watchers': repo.watchers_count,
            'open_issues': repo.open_issues_count,
            'language': repo.language,
            'created_at': repo.created_at.isoformat() if repo.created_at else None,
            'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
            'size_kb': repo.size
        }

    def _analyze_commits(self, repo, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze commit history and patterns."""
        print("Analyzing commit history...")

        commits_by_date = defaultdict(int)
        commits_by_weekday = defaultdict(int)
        commits_by_hour = defaultdict(int)
        total_commits = 0

        try:
            commits = repo.get_commits(since=start_date, until=end_date)

            for commit in commits:
                total_commits += 1
                commit_date = commit.commit.author.date

                # By date
                date_key = commit_date.date().isoformat()
                commits_by_date[date_key] += 1

                # By weekday (0=Monday, 6=Sunday)
                weekday = commit_date.weekday()
                commits_by_weekday[weekday] += 1

                # By hour
                hour = commit_date.hour
                commits_by_hour[hour] += 1

                if total_commits % 100 == 0:
                    print(f"  Processed {total_commits} commits...")

            print(f"  Total commits analyzed: {total_commits}\n")

        except GithubException as e:
            print(f"  Warning: Error fetching commits: {e}\n")

        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        return {
            'total_commits': total_commits,
            'commits_by_date': dict(sorted(commits_by_date.items())),
            'commits_by_weekday': {weekday_names[k]: v for k, v in sorted(commits_by_weekday.items())},
            'commits_by_hour': dict(sorted(commits_by_hour.items())),
            'average_commits_per_day': round(total_commits / ((end_date - start_date).days or 1), 2)
        }

    def _calculate_code_churn(self, repo, start_date: datetime, end_date: datetime) -> Dict:
        """Calculate code churn metrics (additions, deletions, changes)."""
        print("Calculating code churn metrics...")

        total_additions = 0
        total_deletions = 0
        total_changes = 0
        files_changed = set()
        churn_by_date = defaultdict(lambda: {'additions': 0, 'deletions': 0, 'net': 0})
        commit_count = 0

        try:
            commits = repo.get_commits(since=start_date, until=end_date)

            for commit in commits:
                commit_count += 1
                date_key = commit.commit.author.date.date().isoformat()

                try:
                    # Get commit stats
                    stats = commit.stats
                    additions = stats.additions
                    deletions = stats.deletions

                    total_additions += additions
                    total_deletions += deletions
                    total_changes += (additions + deletions)

                    churn_by_date[date_key]['additions'] += additions
                    churn_by_date[date_key]['deletions'] += deletions
                    churn_by_date[date_key]['net'] += (additions - deletions)

                    # Track files changed
                    for file in commit.files:
                        files_changed.add(file.filename)

                except Exception as e:
                    # Some commits might not have accessible stats
                    pass

                if commit_count % 100 == 0:
                    print(f"  Processed {commit_count} commits for churn analysis...")

            print(f"  Code churn analysis complete\n")

        except GithubException as e:
            print(f"  Warning: Error calculating code churn: {e}\n")

        return {
            'total_additions': total_additions,
            'total_deletions': total_deletions,
            'total_changes': total_changes,
            'net_change': total_additions - total_deletions,
            'unique_files_changed': len(files_changed),
            'average_churn_per_commit': round(total_changes / commit_count, 2) if commit_count > 0 else 0,
            'churn_by_date': dict(sorted(churn_by_date.items()))
        }

    def _analyze_contributors(self, repo, start_date: datetime, end_date: datetime) -> Dict:
        """Analyze contributor statistics."""
        print("Analyzing contributor statistics...")

        contributor_stats = defaultdict(lambda: {
            'commits': 0,
            'additions': 0,
            'deletions': 0,
            'net_contribution': 0
        })

        total_contributors = set()

        try:
            commits = repo.get_commits(since=start_date, until=end_date)

            for commit in commits:
                try:
                    author = commit.author.login if commit.author else commit.commit.author.name
                    total_contributors.add(author)

                    contributor_stats[author]['commits'] += 1

                    stats = commit.stats
                    contributor_stats[author]['additions'] += stats.additions
                    contributor_stats[author]['deletions'] += stats.deletions
                    contributor_stats[author]['net_contribution'] += (stats.additions - stats.deletions)

                except Exception:
                    pass

            print(f"  Found {len(total_contributors)} contributors\n")

        except GithubException as e:
            print(f"  Warning: Error analyzing contributors: {e}\n")

        # Sort by commits
        sorted_contributors = sorted(
            contributor_stats.items(),
            key=lambda x: x[1]['commits'],
            reverse=True
        )

        return {
            'total_contributors': len(total_contributors),
            'top_contributors': [
                {
                    'name': name,
                    **stats
                }
                for name, stats in sorted_contributors[:10]  # Top 10
            ],
            'all_contributors': dict(sorted_contributors)
        }

    def _calculate_trends(self, commit_history: Dict) -> Dict:
        """Calculate trends from commit history."""
        commits_by_date = commit_history.get('commits_by_date', {})

        if not commits_by_date:
            return {}

        dates = sorted(commits_by_date.keys())
        if len(dates) < 2:
            return {}

        # Calculate weekly trends
        weekly_commits = []
        current_week = []
        current_week_start = None

        for date_str in dates:
            date = datetime.fromisoformat(date_str).date()
            if current_week_start is None:
                current_week_start = date

            # Check if we've moved to a new week
            if (date - current_week_start).days >= 7:
                if current_week:
                    weekly_commits.append(sum(current_week))
                current_week = [commits_by_date[date_str]]
                current_week_start = date
            else:
                current_week.append(commits_by_date[date_str])

        # Add last week
        if current_week:
            weekly_commits.append(sum(current_week))

        # Most active day
        most_active_day = max(commits_by_date.items(), key=lambda x: x[1]) if commits_by_date else (None, 0)

        return {
            'most_active_day': {
                'date': most_active_day[0],
                'commits': most_active_day[1]
            } if most_active_day[0] else {},
            'weekly_average': round(sum(weekly_commits) / len(weekly_commits), 2) if weekly_commits else 0,
            'weekly_trend': weekly_commits[-4:] if len(weekly_commits) >= 4 else weekly_commits  # Last 4 weeks
        }

    def generate_report(self, metrics: Dict, output_file: str = None):
        """
        Generate a comprehensive report from metrics.

        Args:
            metrics: Metrics dictionary from analyze_repository
            output_file: Optional file to save the report (JSON format)
        """
        if not metrics:
            print("No metrics to report.")
            return

        print(f"\n{'='*60}")
        print("ANALYSIS REPORT")
        print(f"{'='*60}\n")

        # Basic Info
        basic = metrics.get('basic_info', {})
        print(f"Repository: {basic.get('full_name', 'N/A')}")
        print(f"Language: {basic.get('language', 'N/A')}")
        print(f"Stars: {basic.get('stars', 0)} | Forks: {basic.get('forks', 0)} | Watchers: {basic.get('watchers', 0)}")
        print(f"Open Issues: {basic.get('open_issues', 0)}")
        print(f"Size: {basic.get('size_kb', 0)} KB\n")

        # Commit History
        commits = metrics.get('commit_history', {})
        print(f"Commit Analysis:")
        print(f"  Total Commits: {commits.get('total_commits', 0)}")
        print(f"  Average Commits/Day: {commits.get('average_commits_per_day', 0)}")

        weekday_commits = commits.get('commits_by_weekday', {})
        if weekday_commits:
            print(f"\n  Commits by Weekday:")
            for day, count in weekday_commits.items():
                print(f"    {day}: {count}")

        # Code Churn
        churn = metrics.get('code_churn', {})
        print(f"\nCode Churn Metrics:")
        print(f"  Total Additions: +{churn.get('total_additions', 0)} lines")
        print(f"  Total Deletions: -{churn.get('total_deletions', 0)} lines")
        print(f"  Net Change: {churn.get('net_change', 0):+d} lines")
        print(f"  Total Changes: {churn.get('total_changes', 0)} lines")
        print(f"  Files Changed: {churn.get('unique_files_changed', 0)}")
        print(f"  Avg Churn/Commit: {churn.get('average_churn_per_commit', 0)} lines")

        # Contributors
        contributors = metrics.get('contributors', {})
        print(f"\nContributor Statistics:")
        print(f"  Total Contributors: {contributors.get('total_contributors', 0)}")

        top_contributors = contributors.get('top_contributors', [])
        if top_contributors:
            print(f"\n  Top Contributors:")
            for i, contributor in enumerate(top_contributors[:5], 1):
                print(f"    {i}. {contributor['name']}")
                print(f"       Commits: {contributor['commits']} | "
                      f"+{contributor['additions']}/-{contributor['deletions']} lines")

        # Trends
        trends = metrics.get('trends', {})
        most_active = trends.get('most_active_day', {})
        if most_active:
            print(f"\nActivity Trends:")
            print(f"  Most Active Day: {most_active.get('date', 'N/A')} "
                  f"({most_active.get('commits', 0)} commits)")
            print(f"  Weekly Average: {trends.get('weekly_average', 0)} commits")

            weekly_trend = trends.get('weekly_trend', [])
            if weekly_trend:
                print(f"  Recent Weeks Trend: {' -> '.join(map(str, weekly_trend))}")

        print(f"\n{'='*60}\n")

        # Save to file if requested
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    json.dump(metrics, f, indent=2)
                print(f"Report saved to: {output_file}\n")
            except Exception as e:
                print(f"Error saving report: {e}\n")


def main():
    """Main entry point for the analyzer."""
    print("GitHub Repository Analyzer")
    print("=" * 60)

    # Get GitHub token from environment variable (optional)
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("\nNote: No GITHUB_TOKEN found in environment variables.")
        print("You can set one for higher API rate limits:")
        print("  export GITHUB_TOKEN='your_token_here'  # Linux/Mac")
        print("  set GITHUB_TOKEN=your_token_here       # Windows")
        print("\nContinuing with unauthenticated access (lower rate limits)...\n")

    # Get repository name
    if len(sys.argv) > 1:
        repo_name = sys.argv[1]
    else:
        repo_name = input("Enter repository (format: owner/repo): ").strip()

    if not repo_name or '/' not in repo_name:
        print("Error: Invalid repository format. Use 'owner/repo'")
        sys.exit(1)

    # Get analysis period
    try:
        if len(sys.argv) > 2:
            months = int(sys.argv[2])
        else:
            months_input = input("Enter number of months to analyze (default: 6): ").strip()
            months = int(months_input) if months_input else 6
    except ValueError:
        months = 6

    # Initialize analyzer and run analysis
    analyzer = GitHubAnalyzer(token=token)
    metrics = analyzer.analyze_repository(repo_name, months=months)

    if metrics:
        # Generate report
        output_file = f"{repo_name.replace('/', '_')}_analysis.json"
        analyzer.generate_report(metrics, output_file=output_file)

        print("Analysis complete!")
    else:
        print("Analysis failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
