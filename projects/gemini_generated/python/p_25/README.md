# Weather Data Aggregator

This is a command-line tool that fetches current weather data for a given location from two separate, key-less public APIs and presents a comparative summary.

## Features

- **No API Keys Required**: The script uses the Open-Meteo and Weather.gov APIs, which do not require any authentication, making it instantly runnable.
- **Global and US Coverage**: 
    - **Open-Meteo**: Provides weather data for locations worldwide.
    - **Weather.gov**: Provides detailed weather data primarily for locations within the United States.
- **Data Aggregation**: Fetches temperature and wind speed from both sources.
- **Summary Report**: Displays the data from both APIs in a clean, side-by-side table and calculates an aggregated average temperature.

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

3.  **Run the script:**
    You can specify a location using the `--location` or `-l` flag. If no location is provided, it defaults to "New York".

    **For a US location (uses both APIs):**
    ```bash
    python weather_aggregator.py --location "Chicago"
    ```

    **For a non-US location (will likely only get data from Open-Meteo):**
    ```bash
    python weather_aggregator.py -l "London"
    ```

## Expected Output

Running the script will produce a report in your console similar to this:

```
Geocoding location: 'Chicago'...
Found: Chicago, Illinois, US
Fetching data from Open-Meteo...
Fetching data from Weather.gov...

--- Weather Summary for Chicago ---
Timestamp: 2023-10-27 18:00:00

| Metric          | Open-Meteo      | Weather.gov     |
|-----------------|-----------------|-----------------|
| Temperature     | 15.5°C          | 15.0°C          |
| Wind Speed      | 12.0 km/h       | 12.87 km/h      |

Aggregated Average Temperature: 15.25°C

--- End of Report ---
```
