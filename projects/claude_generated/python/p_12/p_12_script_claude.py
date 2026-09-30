import re
import sys
from datetime import datetime
from collections import defaultdict, Counter
from typing import List, Dict, Tuple
import statistics
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path


class LogEntry:
    """Represents a single log entry"""
    def __init__(self, timestamp, level, ip, method, endpoint, status_code, response_time, message):
        self.timestamp = timestamp
        self.level = level
        self.ip = ip
        self.method = method
        self.endpoint = endpoint
        self.status_code = status_code
        self.response_time = response_time
        self.message = message


class LogAnalyzer:
    """Analyzes server logs and generates insights"""

    # Common log patterns (Apache/Nginx combined format + custom application logs)
    LOG_PATTERNS = [
        # Apache/Nginx combined log format
        # 192.168.1.1 - - [01/Jan/2024:12:00:00 +0000] "GET /api/users HTTP/1.1" 200 1234 0.152
        re.compile(
            r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[(?P<timestamp>[^\]]+)\]\s+'
            r'"(?P<method>\w+)\s+(?P<endpoint>[^\s]+)\s+HTTP/[\d.]+"\s+'
            r'(?P<status>\d+)\s+(?P<size>\d+)(?:\s+(?P<response_time>[\d.]+))?'
        ),
        # Custom application log format
        # 2024-01-01 12:00:00 ERROR 192.168.1.1 GET /api/users 500 0.342 Database connection failed
        re.compile(
            r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
            r'(?P<level>\w+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+'
            r'(?P<method>\w+)\s+(?P<endpoint>[^\s]+)\s+'
            r'(?P<status>\d+)\s+(?P<response_time>[\d.]+)\s+'
            r'(?P<message>.*)'
        ),
        # Simplified format
        # [2024-01-01 12:00:00] INFO: 192.168.1.1 GET /api/users 200 0.152
        re.compile(
            r'\[(?P<timestamp>[^\]]+)\]\s+(?P<level>\w+):\s+'
            r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<method>\w+)\s+'
            r'(?P<endpoint>[^\s]+)\s+(?P<status>\d+)(?:\s+(?P<response_time>[\d.]+))?'
        ),
    ]

    TIMESTAMP_FORMATS = [
        '%d/%b/%Y:%H:%M:%S %z',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
    ]

    def __init__(self):
        self.entries: List[LogEntry] = []
        self.error_patterns: Dict[str, int] = defaultdict(int)
        self.anomalies: List[Tuple[LogEntry, str]] = []

    def parse_timestamp(self, ts_string: str) -> datetime:
        """Parse timestamp with multiple format support"""
        for fmt in self.TIMESTAMP_FORMATS:
            try:
                return datetime.strptime(ts_string, fmt)
            except ValueError:
                continue
        # Fallback: try without timezone
        try:
            return datetime.strptime(ts_string.split()[0] + ' ' + ts_string.split()[1],
                                    '%Y-%m-%d %H:%M:%S')
        except:
            return datetime.now()

    def parse_log_line(self, line: str) -> LogEntry:
        """Parse a single log line using regex patterns"""
        for pattern in self.LOG_PATTERNS:
            match = pattern.match(line)
            if match:
                data = match.groupdict()

                timestamp = self.parse_timestamp(data.get('timestamp', ''))
                level = data.get('level', 'INFO')
                ip = data.get('ip', 'unknown')
                method = data.get('method', 'GET')
                endpoint = data.get('endpoint', '/')
                status_code = int(data.get('status', 0))
                response_time = float(data.get('response_time', 0) or 0)
                message = data.get('message', '')

                return LogEntry(timestamp, level, ip, method, endpoint,
                              status_code, response_time, message)

        return None

    def load_logs(self, log_file: str):
        """Load and parse log file"""
        print(f"Loading logs from {log_file}...")
        parsed_count = 0

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    entry = self.parse_log_line(line)
                    if entry:
                        self.entries.append(entry)
                        parsed_count += 1
                    else:
                        print(f"Warning: Could not parse line {line_num}: {line[:50]}...")

        except FileNotFoundError:
            print(f"Error: File {log_file} not found!")
            sys.exit(1)

        print(f"Successfully parsed {parsed_count} log entries\n")

    def identify_error_patterns(self):
        """Identify common error patterns and categorize them"""
        print("Identifying error patterns...")

        for entry in self.entries:
            # HTTP error codes
            if entry.status_code >= 500:
                self.error_patterns['5xx Server Errors'] += 1
                if 'database' in entry.message.lower() or 'db' in entry.message.lower():
                    self.error_patterns['Database Errors'] += 1
                elif 'timeout' in entry.message.lower():
                    self.error_patterns['Timeout Errors'] += 1
                elif 'memory' in entry.message.lower():
                    self.error_patterns['Memory Errors'] += 1

            elif entry.status_code >= 400:
                self.error_patterns['4xx Client Errors'] += 1
                if entry.status_code == 404:
                    self.error_patterns['404 Not Found'] += 1
                elif entry.status_code == 401 or entry.status_code == 403:
                    self.error_patterns['Authentication/Authorization'] += 1

        # Log level errors
        for entry in self.entries:
            if entry.level in ['ERROR', 'CRITICAL', 'FATAL']:
                self.error_patterns[f'{entry.level} Level'] += 1

    def detect_anomalies(self, response_time_threshold: float = 1.0):
        """Detect anomalies in logs"""
        print("Detecting anomalies...")

        response_times = [e.response_time for e in self.entries if e.response_time > 0]

        if not response_times:
            print("No response time data available for anomaly detection")
            return

        mean_rt = statistics.mean(response_times)
        stdev_rt = statistics.stdev(response_times) if len(response_times) > 1 else 0

        # Detect slow requests (beyond threshold or 3 std devs)
        slow_threshold = max(response_time_threshold, mean_rt + 3 * stdev_rt)

        for entry in self.entries:
            # Slow response times
            if entry.response_time > slow_threshold:
                self.anomalies.append((entry, f'Slow response: {entry.response_time:.3f}s'))

            # Repeated errors from same IP
            if entry.status_code >= 500:
                ip_errors = sum(1 for e in self.entries
                              if e.ip == entry.ip and e.status_code >= 500)
                if ip_errors > 10:
                    self.anomalies.append((entry, f'Repeated errors from IP {entry.ip}'))

        # Remove duplicates
        self.anomalies = list(set(self.anomalies))

    def generate_statistics(self) -> Dict:
        """Generate comprehensive statistics"""
        print("Generating statistics...")

        if not self.entries:
            return {}

        # Response times
        response_times = [e.response_time for e in self.entries if e.response_time > 0]

        # Status codes
        status_codes = Counter(e.status_code for e in self.entries)

        # Endpoints
        endpoint_hits = Counter(e.endpoint for e in self.entries)
        endpoint_response_times = defaultdict(list)
        for entry in self.entries:
            if entry.response_time > 0:
                endpoint_response_times[entry.endpoint].append(entry.response_time)

        # Methods
        methods = Counter(e.method for e in self.entries)

        # Time-based
        entries_by_hour = defaultdict(int)
        for entry in self.entries:
            hour = entry.timestamp.hour
            entries_by_hour[hour] += 1

        # Error rate
        total_requests = len(self.entries)
        errors_4xx = sum(1 for e in self.entries if 400 <= e.status_code < 500)
        errors_5xx = sum(1 for e in self.entries if e.status_code >= 500)
        error_rate = (errors_4xx + errors_5xx) / total_requests * 100 if total_requests > 0 else 0

        stats = {
            'total_requests': total_requests,
            'unique_ips': len(set(e.ip for e in self.entries)),
            'error_rate': error_rate,
            'errors_4xx': errors_4xx,
            'errors_5xx': errors_5xx,
            'response_times': {
                'min': min(response_times) if response_times else 0,
                'max': max(response_times) if response_times else 0,
                'mean': statistics.mean(response_times) if response_times else 0,
                'median': statistics.median(response_times) if response_times else 0,
                'stdev': statistics.stdev(response_times) if len(response_times) > 1 else 0,
            },
            'top_endpoints': endpoint_hits.most_common(10),
            'slowest_endpoints': sorted(
                [(ep, statistics.mean(times)) for ep, times in endpoint_response_times.items()],
                key=lambda x: x[1], reverse=True
            )[:10],
            'status_codes': dict(status_codes),
            'methods': dict(methods),
            'hourly_distribution': dict(entries_by_hour),
        }

        return stats

    def print_report(self, stats: Dict):
        """Print text-based analysis report"""
        print("\n" + "="*70)
        print("LOG ANALYSIS REPORT")
        print("="*70)

        print(f"\n📊 OVERVIEW")
        print(f"  Total Requests: {stats['total_requests']:,}")
        print(f"  Unique IPs: {stats['unique_ips']:,}")
        print(f"  Error Rate: {stats['error_rate']:.2f}%")
        print(f"  4xx Errors: {stats['errors_4xx']:,}")
        print(f"  5xx Errors: {stats['errors_5xx']:,}")

        print(f"\n⏱️  RESPONSE TIMES")
        rt = stats['response_times']
        print(f"  Min: {rt['min']:.3f}s")
        print(f"  Max: {rt['max']:.3f}s")
        print(f"  Mean: {rt['mean']:.3f}s")
        print(f"  Median: {rt['median']:.3f}s")
        print(f"  Std Dev: {rt['stdev']:.3f}s")

        print(f"\n🔥 TOP 10 ENDPOINTS")
        for endpoint, count in stats['top_endpoints']:
            print(f"  {count:6,} hits - {endpoint}")

        print(f"\n🐌 SLOWEST ENDPOINTS")
        for endpoint, avg_time in stats['slowest_endpoints']:
            print(f"  {avg_time:.3f}s avg - {endpoint}")

        print(f"\n❌ ERROR PATTERNS")
        if self.error_patterns:
            for pattern, count in sorted(self.error_patterns.items(),
                                        key=lambda x: x[1], reverse=True):
                print(f"  {count:6,} - {pattern}")
        else:
            print("  No errors detected")

        print(f"\n⚠️  ANOMALIES DETECTED: {len(self.anomalies)}")
        if self.anomalies:
            for entry, reason in list(self.anomalies)[:10]:
                print(f"  [{entry.timestamp}] {reason} - {entry.endpoint}")
            if len(self.anomalies) > 10:
                print(f"  ... and {len(self.anomalies) - 10} more")

        print("\n" + "="*70 + "\n")

    def create_visualizations(self, output_dir: str = '.'):
        """Create visualization charts"""
        print("Generating visualizations...")

        if not self.entries:
            print("No data to visualize")
            return

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))

        # 1. Requests over time
        ax1 = plt.subplot(3, 3, 1)
        timestamps = [e.timestamp for e in self.entries]
        if timestamps:
            ax1.hist([t.hour + t.minute/60 for t in timestamps], bins=24, color='skyblue', edgecolor='black')
            ax1.set_xlabel('Hour of Day')
            ax1.set_ylabel('Number of Requests')
            ax1.set_title('Request Distribution by Hour')
            ax1.grid(True, alpha=0.3)

        # 2. Status code distribution
        ax2 = plt.subplot(3, 3, 2)
        status_codes = Counter(e.status_code for e in self.entries)
        if status_codes:
            codes = list(status_codes.keys())
            counts = list(status_codes.values())
            colors = ['green' if c < 400 else 'orange' if c < 500 else 'red' for c in codes]
            ax2.bar(range(len(codes)), counts, color=colors, edgecolor='black')
            ax2.set_xticks(range(len(codes)))
            ax2.set_xticklabels(codes, rotation=45)
            ax2.set_xlabel('Status Code')
            ax2.set_ylabel('Count')
            ax2.set_title('Status Code Distribution')
            ax2.grid(True, alpha=0.3, axis='y')

        # 3. Response time distribution
        ax3 = plt.subplot(3, 3, 3)
        response_times = [e.response_time for e in self.entries if e.response_time > 0]
        if response_times:
            ax3.hist(response_times, bins=50, color='lightcoral', edgecolor='black')
            ax3.set_xlabel('Response Time (s)')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Response Time Distribution')
            ax3.grid(True, alpha=0.3)

        # 4. Top endpoints
        ax4 = plt.subplot(3, 3, 4)
        endpoint_hits = Counter(e.endpoint for e in self.entries).most_common(10)
        if endpoint_hits:
            endpoints = [e[0][:30] for e in endpoint_hits]  # Truncate long URLs
            counts = [e[1] for e in endpoint_hits]
            ax4.barh(range(len(endpoints)), counts, color='mediumpurple', edgecolor='black')
            ax4.set_yticks(range(len(endpoints)))
            ax4.set_yticklabels(endpoints, fontsize=8)
            ax4.set_xlabel('Requests')
            ax4.set_title('Top 10 Endpoints')
            ax4.grid(True, alpha=0.3, axis='x')

        # 5. HTTP Methods
        ax5 = plt.subplot(3, 3, 5)
        methods = Counter(e.method for e in self.entries)
        if methods:
            ax5.pie(methods.values(), labels=methods.keys(), autopct='%1.1f%%',
                   startangle=90, colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
            ax5.set_title('HTTP Methods Distribution')

        # 6. Error patterns
        ax6 = plt.subplot(3, 3, 6)
        if self.error_patterns:
            patterns = list(self.error_patterns.keys())[:10]
            counts = [self.error_patterns[p] for p in patterns]
            ax6.barh(range(len(patterns)), counts, color='tomato', edgecolor='black')
            ax6.set_yticks(range(len(patterns)))
            ax6.set_yticklabels(patterns, fontsize=8)
            ax6.set_xlabel('Occurrences')
            ax6.set_title('Error Patterns')
            ax6.grid(True, alpha=0.3, axis='x')

        # 7. Response time over time
        ax7 = plt.subplot(3, 3, 7)
        time_rt = [(e.timestamp, e.response_time) for e in self.entries if e.response_time > 0]
        if time_rt:
            time_rt.sort()
            times, rts = zip(*time_rt)
            ax7.plot(range(len(times)), rts, linewidth=0.5, alpha=0.7, color='navy')
            ax7.set_xlabel('Request Number')
            ax7.set_ylabel('Response Time (s)')
            ax7.set_title('Response Time Over Requests')
            ax7.grid(True, alpha=0.3)

        # 8. IP addresses (top requesters)
        ax8 = plt.subplot(3, 3, 8)
        ip_counts = Counter(e.ip for e in self.entries).most_common(10)
        if ip_counts:
            ips = [ip[:15] for ip, _ in ip_counts]  # Truncate IPs if needed
            counts = [count for _, count in ip_counts]
            ax8.barh(range(len(ips)), counts, color='teal', edgecolor='black')
            ax8.set_yticks(range(len(ips)))
            ax8.set_yticklabels(ips, fontsize=8)
            ax8.set_xlabel('Requests')
            ax8.set_title('Top 10 IP Addresses')
            ax8.grid(True, alpha=0.3, axis='x')

        # 9. Error rate over time
        ax9 = plt.subplot(3, 3, 9)
        hourly_errors = defaultdict(lambda: {'total': 0, 'errors': 0})
        for entry in self.entries:
            hour = entry.timestamp.hour
            hourly_errors[hour]['total'] += 1
            if entry.status_code >= 400:
                hourly_errors[hour]['errors'] += 1

        if hourly_errors:
            hours = sorted(hourly_errors.keys())
            error_rates = [(hourly_errors[h]['errors'] / hourly_errors[h]['total'] * 100)
                          for h in hours]
            ax9.plot(hours, error_rates, marker='o', color='crimson', linewidth=2)
            ax9.set_xlabel('Hour of Day')
            ax9.set_ylabel('Error Rate (%)')
            ax9.set_title('Error Rate by Hour')
            ax9.grid(True, alpha=0.3)
            ax9.set_xticks(range(0, 24, 3))

        plt.tight_layout()

        output_file = output_path / 'log_analysis_report.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to: {output_file}")

        plt.close()


def create_sample_log_file(filename: str = 'sample_server.log'):
    """Create a sample log file for testing"""
    import random

    print(f"Creating sample log file: {filename}")

    sample_logs = []
    base_time = datetime(2024, 1, 1, 10, 0, 0)

    endpoints = ['/api/users', '/api/products', '/api/orders', '/api/login',
                '/api/search', '/api/checkout', '/static/css/main.css', '/']
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    ips = [f'192.168.1.{i}' for i in range(1, 50)]

    for i in range(1000):
        timestamp = base_time.replace(
            hour=(base_time.hour + i // 100) % 24,
            minute=(base_time.minute + i) % 60,
            second=i % 60
        )

        ip = random.choice(ips)
        method = random.choices(methods, weights=[70, 20, 7, 3])[0]
        endpoint = random.choice(endpoints)

        # Mostly successful requests
        if random.random() < 0.85:
            status = 200
            response_time = random.uniform(0.01, 0.5)
            level = 'INFO'
            message = 'Request processed successfully'
        elif random.random() < 0.90:
            status = random.choice([404, 400, 401, 403])
            response_time = random.uniform(0.01, 0.3)
            level = 'WARNING'
            message = 'Client error occurred'
        else:
            status = random.choice([500, 502, 503])
            response_time = random.uniform(0.5, 3.0)
            level = 'ERROR'
            messages = [
                'Database connection failed',
                'Request timeout exceeded',
                'Internal server error',
                'Memory allocation failed'
            ]
            message = random.choice(messages)

        # Add some anomalies
        if random.random() < 0.02:
            response_time = random.uniform(2.0, 5.0)

        log_line = (
            f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} {level} {ip} "
            f"{method} {endpoint} {status} {response_time:.3f} {message}"
        )

        sample_logs.append(log_line)

    with open(filename, 'w') as f:
        f.write('\n'.join(sample_logs))

    print(f"Created {len(sample_logs)} sample log entries\n")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Server Log Analyzer')
    parser.add_argument('log_file', nargs='?', help='Path to log file')
    parser.add_argument('--create-sample', action='store_true',
                       help='Create a sample log file for testing')
    parser.add_argument('--output-dir', default='.',
                       help='Directory to save visualizations (default: current directory)')
    parser.add_argument('--threshold', type=float, default=1.0,
                       help='Response time threshold for anomaly detection (default: 1.0s)')

    args = parser.parse_args()

    if args.create_sample:
        create_sample_log_file('sample_server.log')
        if not args.log_file:
            args.log_file = 'sample_server.log'

    if not args.log_file:
        print("Error: Please provide a log file or use --create-sample")
        parser.print_help()
        sys.exit(1)

    # Run analysis
    analyzer = LogAnalyzer()
    analyzer.load_logs(args.log_file)
    analyzer.identify_error_patterns()
    analyzer.detect_anomalies(response_time_threshold=args.threshold)

    stats = analyzer.generate_statistics()
    analyzer.print_report(stats)
    analyzer.create_visualizations(output_dir=args.output_dir)

    print("✅ Analysis complete!")


if __name__ == '__main__':
    main()
