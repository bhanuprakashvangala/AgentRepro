#!/usr/bin/env python3
"""
System Resource Monitor with Threshold-based Alerts
Monitors CPU, memory, and disk usage with configurable thresholds
"""

import psutil
import time
import datetime
import os
from pathlib import Path


class ResourceMonitor:
    """Monitor system resources and trigger alerts when thresholds are exceeded"""

    def __init__(self,
                 cpu_threshold=80.0,
                 memory_threshold=80.0,
                 disk_threshold=80.0,
                 log_file="resource_monitor.log",
                 interval=5):
        """
        Initialize the resource monitor

        Args:
            cpu_threshold: CPU usage percentage threshold for alerts (default: 80%)
            memory_threshold: Memory usage percentage threshold for alerts (default: 80%)
            disk_threshold: Disk usage percentage threshold for alerts (default: 80%)
            log_file: Path to log file (default: "resource_monitor.log")
            interval: Monitoring interval in seconds (default: 5)
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.log_file = log_file
        self.interval = interval

        # Create log file if it doesn't exist
        Path(self.log_file).touch(exist_ok=True)

    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        """Get current memory usage statistics"""
        memory = psutil.virtual_memory()
        return {
            'percent': memory.percent,
            'used_gb': memory.used / (1024**3),
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3)
        }

    def get_disk_usage(self, path='/'):
        """Get current disk usage statistics"""
        disk = psutil.disk_usage(path)
        return {
            'percent': disk.percent,
            'used_gb': disk.used / (1024**3),
            'total_gb': disk.total / (1024**3),
            'free_gb': disk.free / (1024**3)
        }

    def check_thresholds(self, cpu, memory, disk):
        """
        Check if any resource exceeds its threshold

        Returns:
            list: List of alert messages
        """
        alerts = []

        if cpu > self.cpu_threshold:
            alerts.append(f"🔴 CPU ALERT: {cpu:.1f}% (threshold: {self.cpu_threshold}%)")

        if memory['percent'] > self.memory_threshold:
            alerts.append(
                f"🔴 MEMORY ALERT: {memory['percent']:.1f}% "
                f"({memory['used_gb']:.2f}GB/{memory['total_gb']:.2f}GB) "
                f"(threshold: {self.memory_threshold}%)"
            )

        if disk['percent'] > self.disk_threshold:
            alerts.append(
                f"🔴 DISK ALERT: {disk['percent']:.1f}% "
                f"({disk['used_gb']:.2f}GB/{disk['total_gb']:.2f}GB) "
                f"(threshold: {self.disk_threshold}%)"
            )

        return alerts

    def log_metrics(self, timestamp, cpu, memory, disk, alerts):
        """Log metrics and alerts to file"""
        with open(self.log_file, 'a') as f:
            # Write timestamp
            f.write(f"\n{'='*70}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"{'-'*70}\n")

            # Write metrics
            f.write(f"CPU Usage: {cpu:.1f}%\n")
            f.write(f"Memory Usage: {memory['percent']:.1f}% "
                   f"({memory['used_gb']:.2f}GB / {memory['total_gb']:.2f}GB)\n")
            f.write(f"Disk Usage: {disk['percent']:.1f}% "
                   f"({disk['used_gb']:.2f}GB / {disk['total_gb']:.2f}GB)\n")

            # Write alerts if any
            if alerts:
                f.write(f"\n⚠️  ALERTS:\n")
                for alert in alerts:
                    f.write(f"  {alert}\n")

    def display_metrics(self, timestamp, cpu, memory, disk, alerts):
        """Display metrics to console"""
        print(f"\n{'='*70}")
        print(f"📊 System Resource Monitor - {timestamp}")
        print(f"{'='*70}")

        # CPU
        cpu_status = "🔴" if cpu > self.cpu_threshold else "🟢"
        print(f"\n{cpu_status} CPU Usage: {cpu:.1f}%")

        # Memory
        mem_status = "🔴" if memory['percent'] > self.memory_threshold else "🟢"
        print(f"{mem_status} Memory Usage: {memory['percent']:.1f}% "
              f"({memory['used_gb']:.2f}GB / {memory['total_gb']:.2f}GB)")
        print(f"   Available: {memory['available_gb']:.2f}GB")

        # Disk
        disk_status = "🔴" if disk['percent'] > self.disk_threshold else "🟢"
        print(f"{disk_status} Disk Usage: {disk['percent']:.1f}% "
              f"({disk['used_gb']:.2f}GB / {disk['total_gb']:.2f}GB)")
        print(f"   Free: {disk['free_gb']:.2f}GB")

        # Alerts
        if alerts:
            print(f"\n⚠️  ACTIVE ALERTS:")
            for alert in alerts:
                print(f"   {alert}")
        else:
            print(f"\n✅ All systems normal")

        print(f"\nNext check in {self.interval} seconds... (Ctrl+C to stop)")

    def run(self, duration=None):
        """
        Run the monitoring loop

        Args:
            duration: Total duration to run in seconds (None for infinite)
        """
        print(f"\n🚀 Starting System Resource Monitor")
        print(f"{'='*70}")
        print(f"Thresholds: CPU={self.cpu_threshold}%, "
              f"Memory={self.memory_threshold}%, "
              f"Disk={self.disk_threshold}%")
        print(f"Log file: {os.path.abspath(self.log_file)}")
        print(f"Check interval: {self.interval} seconds")
        print(f"{'='*70}")

        start_time = time.time()

        try:
            while True:
                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    print("\n⏰ Duration limit reached. Stopping monitor.")
                    break

                # Get current timestamp
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Collect metrics
                cpu = self.get_cpu_usage()
                memory = self.get_memory_usage()
                disk = self.get_disk_usage()

                # Check thresholds
                alerts = self.check_thresholds(cpu, memory, disk)

                # Log to file
                self.log_metrics(timestamp, cpu, memory, disk, alerts)

                # Display to console
                self.display_metrics(timestamp, cpu, memory, disk, alerts)

                # Wait for next interval
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            print(f"📄 Logs saved to: {os.path.abspath(self.log_file)}")


def main():
    """Main entry point"""
    # Configure monitor with custom thresholds
    monitor = ResourceMonitor(
        cpu_threshold=80.0,      # Alert if CPU > 80%
        memory_threshold=80.0,   # Alert if Memory > 80%
        disk_threshold=80.0,     # Alert if Disk > 80%
        log_file="resource_monitor.log",
        interval=5               # Check every 5 seconds
    )

    # Run the monitor (infinite loop until Ctrl+C)
    monitor.run()

    # Or run for a specific duration (e.g., 60 seconds):
    # monitor.run(duration=60)


if __name__ == "__main__":
    main()
