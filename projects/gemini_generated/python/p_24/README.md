# Network Port Scanner

This project is a Python script that scans a target IP address for open ports and attempts to identify the services running on them.

## ⚠️ CRITICAL: Requirements & Safety

1.  **External Dependency**: This script is a wrapper for the **Nmap** security tool. You **MUST** install Nmap on your system and ensure it is available in your system's PATH for this script to work.
    - **Download Nmap from its official website: [https://nmap.org/download.html](https://nmap.org/download.html)**

2.  **Ethical Use**: Port scanning can be viewed as a hostile act. **DO NOT scan any IP address or network that you do not own or have explicit, written permission to test.** This tool is for educational purposes only. By default, it is configured to safely scan your own machine (`localhost`).

## Features

- **Port & Service Scanning**: Uses Nmap's powerful `-sV` engine to detect open ports, services, and version information.
- **Configurable Targets**: Allows you to specify a target IP and port range via the command line.
- **Reproducible Demo**: The script automatically starts a temporary "dummy" server on port `12345` on your local machine. This guarantees that the scanner will find at least one open port during a default scan, providing a clear and safe demonstration of its functionality.
- **Formatted Reporting**: Generates a clean, readable report of the scan results directly in your console.

## Usage

1.  **Install Nmap**: Download and install Nmap from [https://nmap.org/download.html](https://nmap.org/download.html).

2.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Scanner:**

    **To run a safe scan on your own machine (recommended):**
    ```bash
    python port_scanner.py
    ```
    This will scan `localhost` (127.0.0.1) and will find the dummy server on port 12345, along with any other open ports on your machine in the default range.

    **To scan a different target (use with caution):**
    ```bash
    python port_scanner.py --target <IP_ADDRESS> --ports <PORT_RANGE>
    
    # Example:
    python port_scanner.py --target 192.168.1.1 --ports 1-1000
    ```

## Output

The script will print a detailed report listing the state of the host and for every open port, its state, service name, and version information if detected.
