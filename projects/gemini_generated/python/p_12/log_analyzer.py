import re
import pandas as pd
import matplotlib.pyplot as plt
import os
import random
from datetime import datetime, timedelta

LOG_FILE = "server.log"
REPORT_IMAGE = "log_analysis_report.png"

def generate_sample_log_file(filename=LOG_FILE, num_lines=1000):
    """Generates a realistic-looking server log file for demonstration."""
    if os.path.exists(filename):
        print(f"Log file '{filename}' already exists.")
        return

    print(f"Generating sample log file: {filename}")
    methods = ["GET", "POST", "PUT", "DELETE"]
    paths = ["/api/users", "/api/products", "/home", "/assets/style.css", "/login", "/api/orders/123"]
    status_codes = [200, 200, 200, 200, 200, 201, 302, 404, 500, 503]
    base_time = datetime.now()

    with open(filename, 'w') as f:
        for i in range(num_lines):
            timestamp = (base_time - timedelta(seconds=i)).strftime('%Y-%m-%d %H:%M:%S')
            ip = f"192.168.1.{random.randint(1, 100)}"
            method = random.choice(methods)
            path = random.choice(paths)
            status = random.choice(status_codes)
            # Make response times mostly fast, with some outliers
            response_time = random.randint(20, 300) if random.random() < 0.95 else random.randint(301, 2000)
            
            f.write(f'[{timestamp}] {ip} "{method} {path} HTTP/1.1" {status} {response_time}ms\n')

def parse_log_file(file_path):
    """Parses a log file using regex and returns a pandas DataFrame."""
    log_pattern = re.compile(
        r'\['(?P<timestamp>.*?)'\]\s+'
        r'(?P<ip>\S+)\s+"'
        r'(?P<method>\S+)\s+'
        r'(?P<path>\S+)\s+.*?")\s+'
        r'(?P<status>\d{3})\s+'
        r'(?P<response_time>\d+)ms'
    )
    
    with open(file_path, 'r') as f:
        lines = f.readlines()

    records = [log_pattern.match(line).groupdict() for line in lines if log_pattern.match(line)]
    df = pd.DataFrame(records)
    
    # Convert data types
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['status'] = df['status'].astype(int)
    df['response_time'] = df['response_time'].astype(int)
    
    return df

def analyze_logs(df):
    """Performs statistical analysis on the log data and prints a report."""
    print("\n--- Log Analysis Report ---")
    
    # Basic stats
    total_requests = len(df)
    error_rate = len(df[df['status'] >= 400]) / total_requests * 100
    print(f"Total Requests: {total_requests}")
    print(f"Error Rate: {error_rate:.2f}%")

    # Response time stats
    print("\nResponse Time Statistics (ms):")
    print(f"  - Average: {df['response_time'].mean():.2f}")
    print(f"  - Median: {df['response_time'].median():.2f}")
    print(f"  - 95th Percentile: {df['response_time'].quantile(0.95):.2f}")

    # Status code distribution
    print("\nStatus Code Distribution:")
    print(df['status'].value_counts().to_string())

    # Anomalies and patterns
    print("\nTop 5 Slowest Requests:")
    print(df.nlargest(5, 'response_time')[['timestamp', 'path', 'status', 'response_time']].to_string(index=False))

    print("\nTop 5 IP Addresses with Most Server Errors (5xx):")
    error_ips = df[df['status'] >= 500]['ip'].value_counts().nlargest(5)
    print(error_ips.to_string())
    print("-------------------------")

def create_visualizations(df, output_image):
    """Creates and saves visualizations of the log analysis."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))
    fig.suptitle('Server Log Analysis', fontsize=16)

    # Plot 1: Response Time Distribution
    ax1.hist(df['response_time'], bins=50, color='skyblue', edgecolor='black')
    ax1.set_title('Response Time Distribution')
    ax1.set_xlabel('Response Time (ms)')
    ax1.set_ylabel('Frequency')
    ax1.axvline(df['response_time'].mean(), color='red', linestyle='--', linewidth=1, label=f"Mean: {df['response_time'].mean():.2f}ms")
    ax1.legend()

    # Plot 2: Status Code Counts
    status_counts = df['status'].value_counts().sort_index()
    status_counts.plot(kind='bar', ax=ax2, color=['green' if c < 400 else 'red' for c in status_counts.index])
    ax2.set_title('HTTP Status Code Counts')
    ax2.set_xlabel('Status Code')
    ax2.set_ylabel('Count')
    ax2.tick_params(axis='x', rotation=0)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_image)
    print(f"\nVisual report saved as {output_image}")

if __name__ == "__main__":
    generate_sample_log_file()
    log_df = parse_log_file(LOG_FILE)
    analyze_logs(log_df)
    create_visualizations(log_df, REPORT_IMAGE)
