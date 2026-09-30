# Weather Aggregator

Fetches weather data from two public APIs (Open-Meteo and National Weather Service) for a specified latitude/longitude, compares the results, and produces a blended forecast summary.

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python weather_aggregator.py --latitude 40.7128 --longitude -74.0060 \
  --user-agent "WeatherAggregator/1.0 (+you@example.com)" \
  --text-output forecast.txt --json-output forecast.json
```

Arguments:
- `--latitude` / `--longitude`: Coordinates in decimal degrees (required).
- `--user-agent`: Custom User-Agent header sent to weather.gov (include contact info as requested by NOAA). Default is `WeatherAggregator/1.0 (+contact@example.com)`.
- `--text-output`: Optional path to write a human-readable summary.
- `--json-output`: Optional path to write the full JSON payload.

The script prints the summary to stdout and optionally saves text/JSON files. It blends current temperature and daily high/low values from both sources and notes any differences between providers.

> **Note:** The National Weather Service API occasionally throttles requests. Provide a valid contact email in the user agent to comply with their policy.
