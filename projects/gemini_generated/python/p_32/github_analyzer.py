import requests
import argparse
import pandas as pd
from datetime import datetime

# --- Configuration ---
GITHUB_API_URL = "https://api.github.com"
# To increase rate limits, generate a personal access token (PAT) from GitHub
# and uncomment the following line, replacing "your_token_here".
# GITHUB_TOKEN = "your_token_here"
GITHUB_TOKEN = None

def make_request(endpoint):
    """Makes a request to a GitHub API endpoint and handles errors."""
    url = f"{GITHUB_API_URL}{endpoint}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    try:
        response = requests.get(url, headers=headers)
        # Check for rate limit exceeded
        if response.status_code == 403 and 'rate limit' in response.text.lower():
            print("[ERROR] GitHub API rate limit exceeded. Please wait or use a personal access token.")
            return None
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return None

def analyze_repository(repo_name):
    """Fetches and analyzes data for a given repository."""
    print(f"--- Analyzing Repository: {repo_name} ---")

    # --- 1. Fetch Contributor Statistics ---
    print("\nFetching contributor statistics...")
    # This endpoint can take a moment for GitHub to compute
    contributor_stats = make_request(f"/repos/{repo_name}/stats/contributors")
    if not contributor_stats:
        print("Could not fetch contributor stats. The repository may be empty or new.")
        return

    # --- 2. Fetch Code Frequency (Churn) ---
    print("Fetching code frequency (churn)...")
    code_frequency = make_request(f"/repos/{repo_name}/stats/code_frequency")
    if not code_frequency:
        print("Could not fetch code frequency stats.")
        return

    # --- 3. Generate Report ---
    generate_report(repo_name, contributor_stats, code_frequency)

def generate_report(repo_name, contributor_data, frequency_data):
    """Processes the fetched data with pandas and prints a report."""
    print(f"\n--- Analysis Report for {repo_name} ---")

    # --- Contributor Report ---
    if contributor_data:
        df_contrib = pd.DataFrame([{
            'contributor': contributor['author']['login'],
            'commits': contributor['total'],
            'additions': sum(week['a'] for week in contributor['weeks']),
            'deletions': sum(week['d'] for week in contributor['weeks'])
        } for contributor in contributor_data])
        
        df_contrib = df_contrib.sort_values(by='commits', ascending=False).reset_index(drop=True)
        print("\nTop 10 Contributors by Commits:")
        print(df_contrib.head(10).to_string())
    
    # --- Code Churn Report ---
    if frequency_data:
        df_freq = pd.DataFrame(frequency_data, columns=['timestamp', 'additions', 'deletions'])
        df_freq['week'] = df_freq['timestamp'].apply(lambda ts: datetime.fromtimestamp(ts).strftime('%Y-%m-%d'))
        df_freq['deletions'] = df_freq['deletions'].abs() # Show as positive numbers
        df_freq['churn'] = df_freq['additions'] + df_freq['deletions']
        df_freq = df_freq[['week', 'additions', 'deletions', 'churn']]

        print("\nWeekly Code Churn (Last 12 Weeks):")
        print(df_freq.tail(12).to_string(index=False))

        total_additions = df_freq['additions'].sum()
        total_deletions = df_freq['deletions'].sum()
        print(f"\nLifetime Stats: +{total_additions:,} lines added, -{total_deletions:,} lines deleted.")

    print("\n--- End of Report ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze a GitHub repository.")
    parser.add_argument("-r", "--repo", default="pallets/flask", help='The repository to analyze in "owner/repo" format (default: pallets/flask).')
    args = parser.parse_args()

    analyze_repository(args.repo)
