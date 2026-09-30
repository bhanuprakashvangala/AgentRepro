# GitHub Repository Analyzer

This is a command-line tool that fetches and analyzes metrics for a public GitHub repository, including contributor statistics and code churn.

## ⚠️ Important: API Rate Limiting

This script makes unauthenticated requests to the GitHub API, which are subject to a rate limit (typically 60 requests per hour per IP address). 

- The script is designed to work on small to medium-sized repositories under this limit.
- If you analyze very large repositories or run the script frequently, you may hit the rate limit and see an error.
- **To increase the limit**, you can generate a [GitHub Personal Access Token (PAT)](https://github.com/settings/tokens) and paste it into the `GITHUB_TOKEN` variable at the top of the `github_analyzer.py` script.

## Features

- **Contributor Statistics**: Fetches a list of repository contributors and ranks them by total commits, showing their total lines added and deleted.
- **Code Churn Analysis**: Uses the Code Frequency API to calculate and display the total lines added and deleted per week.
- **Clean Reporting**: Uses the `pandas` library to present the data in clean, readable tables in your console.

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Analyzer:**

    **To run on the default repository (`pallets/flask`):**
    ```bash
    python github_analyzer.py
    ```

    **To analyze a different public repository:**
    Use the `--repo` flag with the `owner/repository` format.
    ```bash
    python github_analyzer.py --repo "psf/requests"
    ```

## Expected Output

The script will print a formatted report to the console, including tables for contributor stats and weekly code churn.

```
--- Analyzing Repository: pallets/flask ---

Fetching contributor statistics...
Fetching code frequency (churn)...

--- Analysis Report for pallets/flask ---

Top 10 Contributors by Commits:
      contributor  commits  additions  deletions
0      davidism     2289     101338      66394
1      mitsuhiko    1290      87224      32381
...

Weekly Code Churn (Last 12 Weeks):
        week  additions  deletions  churn
10   2023-08-13         20         10     30
11   2023-08-20          5          5     10
...

Lifetime Stats: +200,000 lines added, -100,000 lines deleted.

--- End of Report ---
```
*(Note: Numbers are illustrative and will vary.)*
