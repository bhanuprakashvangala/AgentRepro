# System Resource Monitor

This is a command-line tool that continuously monitors system resources (CPU, memory, and disk usage), logs the data to a file, and provides real-time alerts if usage exceeds specified thresholds.

## Features

- **Cross-Platform**: Uses the `psutil` library to run on Windows, macOS, and Linux.
- **Live Monitoring**: Provides a continuously updating, single-line display of current CPU, memory, and disk usage.
- **Historical Logging**: Appends timestamped resource usage to a log file (`system_monitor.log` by default) for later analysis.
- **Threshold Alerts**: Prints a clear alert message to the console if any resource exceeds its configured threshold.
- **Alert Cooldown**: To prevent spam, alerts for a specific resource have a 5-minute cooldown period.
- **Configurable**: The monitoring interval and alert thresholds can be easily changed via command-line arguments.

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

3.  **Run the Monitor:**
    To stop the monitor at any time, press `Ctrl+C`.

    **To run with default settings:**
    (Checks every 5 seconds. Alerts at CPU > 80%, Memory > 80%, Disk > 90%)
    ```bash
    python system_monitor.py
    ```

    **To run with custom settings:**
    You can customize the interval and thresholds.
    ```bash
    python system_monitor.py --interval 10 --cpu-threshold 75 --mem-threshold 85 --disk-threshold 95
    ```

## Output

### Console Output

You will see a live-updating status line:
```
CPU:   5.2% | MEM:  45.8% | DISK:  60.2%
```

If a threshold is breached, an alert will be printed:
```
[ALERT] CPU usage is critical: 85.3% (Threshold: 80%)
```

### Log File (`system_monitor.log`)

A log file will be created in the same directory, with entries added at each interval:
```
2023-10-27 19:00:00, CPU: 5.2%, MEM: 45.8%, DISK: 60.2%
2023-10-27 19:00:05, CPU: 10.1%, MEM: 45.9%, DISK: 60.2%
...
```
