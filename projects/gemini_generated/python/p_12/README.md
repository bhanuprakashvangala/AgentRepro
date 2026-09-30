# Log Analyzer

This project is a Python script that parses and analyzes server logs to generate insights. It uses regular expressions for parsing, `pandas` for data analysis, and `matplotlib` for visualization.

## Features

- **Sample Log Generation**: Automatically creates a `server.log` file with 1000 lines of realistic log data, making the script instantly runnable and reproducible.
- **Regex Parsing**: Uses a regular expression to parse log lines into structured data, including timestamp, IP address, HTTP method, path, status code, and response time.
- **Statistical Analysis**: Calculates and prints key metrics:
    - Total requests and error rate.
    - Average, median, and 95th percentile response times.
    - Distribution of status codes.
- **Anomaly Detection**: Identifies the top 5 slowest requests and the top 5 IP addresses responsible for the most server errors (5xx).
- **Visualization**: Generates a PNG image (`log_analysis_report.png`) containing two plots:
    1.  A histogram of response time distribution.
    2.  A bar chart of status code counts.

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

3.  **Run the analyzer:**
    ```bash
    python log_analyzer.py
    ```

## Output

When you run the script, it will:

1.  Create a `server.log` file (if it doesn't exist).
2.  Print a detailed analysis report to the console.
3.  Generate a `log_analysis_report.png` file in the same directory with visualizations of the log data.
