import psutil
import time
import argparse
from datetime import datetime

# --- Configuration ---
DEFAULT_LOG_FILE = "system_monitor.log"
# Cooldown in seconds before re-issuing an alert for the same resource
ALERT_COOLDOWN = 300 # 5 minutes

def log_usage(log_file, cpu_percent, mem_percent, disk_percent):
    """Appends a timestamped resource usage log entry to the specified file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp}, CPU: {cpu_percent:.1f}%, MEM: {mem_percent:.1f}%, DISK: {disk_percent:.1f}%
"
    try:
        with open(log_file, 'a') as f:
            f.write(log_entry)
    except IOError as e:
        print(f"[ERROR] Could not write to log file {log_file}: {e}")

def check_and_alert(cpu, mem, disk, thresholds, last_alert_times):
    """Checks resource usage against thresholds and prints alerts."""
    now = time.time()
    
    # Check CPU
    if cpu > thresholds['cpu'] and (now - last_alert_times['cpu'] > ALERT_COOLDOWN):
        print(f"\n[ALERT] CPU usage is critical: {cpu:.1f}% (Threshold: {thresholds['cpu']}%) ")
        last_alert_times['cpu'] = now

    # Check Memory
    if mem > thresholds['mem'] and (now - last_alert_times['mem'] > ALERT_COOLDOWN):
        print(f"\n[ALERT] Memory usage is critical: {mem:.1f}% (Threshold: {thresholds['mem']}%) ")
        last_alert_times['mem'] = now

    # Check Disk
    if disk > thresholds['disk'] and (now - last_alert_times['disk'] > ALERT_COOLDOWN):
        print(f"\n[ALERT] Disk usage is critical: {disk:.1f}% (Threshold: {thresholds['disk']}%) ")
        last_alert_times['disk'] = now

def start_monitoring(interval, log_file, thresholds):
    """Main loop to monitor system resources."""
    print("--- Starting System Resource Monitor ---")
    print(f"Checking every {interval} seconds. Press Ctrl+C to stop.")
    print(f"Alert Thresholds -> CPU: {thresholds['cpu']}%, Memory: {thresholds['mem']}%, Disk: {thresholds['disk']}%
")

    # Initialize cooldown timestamps to 0 to allow immediate first alert
    last_alert_times = {'cpu': 0, 'mem': 0, 'disk': 0}

    while True:
        # Get current resource usage
        # interval=1 for cpu_percent gets a non-blocking reading over 1 second
        cpu_usage = psutil.cpu_percent(interval=1)
        mem_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        # Log the current usage
        log_usage(log_file, cpu_usage, mem_usage, disk_usage)

        # Print live status to console
        status_line = f"CPU: {cpu_usage:5.1f}% | MEM: {mem_usage:5.1f}% | DISK: {disk_usage:5.1f}%"
        print(f"\r{status_line}", end="", flush=True)

        # Check for alerts
        check_and_alert(cpu_usage, mem_usage, disk_usage, thresholds, last_alert_times)

        # Wait for the next interval
        time.sleep(interval - 1) # Subtract the 1 second used by cpu_percent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor system resources (CPU, Memory, Disk) with alerts.")
    parser.add_argument("-i", "--interval", type=int, default=5, help="Interval in seconds between checks (default: 5).")
    parser.add_argument("--cpu-threshold", type=float, default=80.0, help="CPU usage percentage to trigger an alert (default: 80).")
    parser.add_argument("--mem-threshold", type=float, default=80.0, help="Memory usage percentage to trigger an alert (default: 80).")
    parser.add_argument("--disk-threshold", type=float, default=90.0, help="Disk usage percentage to trigger an alert (default: 90).")
    parser.add_argument("--log-file", default=DEFAULT_LOG_FILE, help=f"File to log resource usage (default: {DEFAULT_LOG_FILE}).")
    args = parser.parse_args()

    if args.interval < 2:
        print("[ERROR] Interval must be 2 seconds or greater.")
        exit(1)

    alert_thresholds = {
        'cpu': args.cpu_threshold,
        'mem': args.mem_threshold,
        'disk': args.disk_threshold
    }

    try:
        start_monitoring(args.interval, args.log_file, alert_thresholds)
    except KeyboardInterrupt:
        print("\n\n--- Monitor stopped by user. ---")
    except Exception as e:
        print(f"\n[FATAL ERROR] An unexpected error occurred: {e}")
