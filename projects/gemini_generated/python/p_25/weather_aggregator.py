import requests
import argparse
from datetime import datetime

# --- API Configuration ---
# No API keys needed for these services
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_API = "https://api.open-meteo.com/v1/forecast"
WEATHER_GOV_API = "https://api.weather.gov/points/{lat},{lon}"

# --- Helper Functions ---

def get_lat_lon(location_name):
    """Converts a location name to latitude and longitude using Open-Meteo's geocoding."""
    print(f"Geocoding location: '{location_name}'...")
    params = {"name": location_name, "count": 1}
    try:
        response = requests.get(GEOCODING_API, params=params)
        response.raise_for_status()
        results = response.json().get('results')
        if not results:
            print(f"Error: Could not find coordinates for '{location_name}'.")
            return None, None
        loc = results[0]
        print(f"Found: {loc['name']}, {loc.get('admin1', '')}, {loc['country_code']}")
        return loc['latitude'], loc['longitude']
    except requests.exceptions.RequestException as e:
        print(f"Error during geocoding request: {e}")
        return None, None

def fetch_open_meteo(lat, lon):
    """Fetches current weather from Open-Meteo."""
    print("Fetching data from Open-Meteo...")
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True
    }
    try:
        response = requests.get(OPEN_METEO_API, params=params)
        response.raise_for_status()
        data = response.json()['current_weather']
        return {
            "temperature_c": data['temperature'],
            "wind_speed_kmh": data['windspeed']
        }
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch data from Open-Meteo: {e}")
        return None

def fetch_weather_gov(lat, lon):
    """Fetches current weather from Weather.gov (primarily for US locations)."""
    print("Fetching data from Weather.gov...")
    headers = {"User-Agent": "MyWeatherAggregator/1.0 (contact@example.com)"}
    try:
        # Step 1: Get the grid endpoint for the given coordinates
        response_points = requests.get(WEATHER_GOV_API.format(lat=lat, lon=lon), headers=headers)
        response_points.raise_for_status()
        forecast_url = response_points.json()['properties']['forecast']

        # Step 2: Get the actual forecast from the grid endpoint
        response_forecast = requests.get(forecast_url, headers=headers)
        response_forecast.raise_for_status()
        current_period = response_forecast.json()['properties']['periods'][0]
        
        temp_f = current_period['temperature']
        temp_c = (temp_f - 32) * 5.0/9.0

        # Extract wind speed value
        wind_speed_str = current_period['windSpeed']
        wind_speed_mph = int(wind_speed_str.split()[0])
        wind_speed_kmh = wind_speed_mph * 1.60934

        return {
            "temperature_c": round(temp_c, 2),
            "wind_speed_kmh": round(wind_speed_kmh, 2)
        }
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        print(f"Could not fetch data from Weather.gov: {e}. (Note: This API works best for US locations)")
        return None

def generate_summary_report(location, data_om, data_wgov):
    """Prints a summary report comparing the data from both APIs."""
    print(f"\n--- Weather Summary for {location.title()} ---")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"| Metric          | Open-Meteo      | Weather.gov     |")
    print(f"|-----------------|-----------------|-----------------|")
    
    temp_om_str = f"{data_om['temperature_c']}°C" if data_om else "N/A"
    temp_wgov_str = f"{data_wgov['temperature_c']}°C" if data_wgov else "N/A"
    print(f"| Temperature     | {temp_om_str:<15} | {temp_wgov_str:<15} |")

    wind_om_str = f"{data_om['wind_speed_kmh']} km/h" if data_om else "N/A"
    wind_wgov_str = f"{data_wgov['wind_speed_kmh']} km/h" if data_wgov else "N/A"
    print(f"| Wind Speed      | {wind_om_str:<15} | {wind_wgov_str:<15} |")

    # --- Aggregated Data ---
    temps = [d['temperature_c'] for d in [data_om, data_wgov] if d]
    if temps:
        avg_temp = sum(temps) / len(temps)
        print(f"\nAggregated Average Temperature: {avg_temp:.2f}°C")
    
    print("\n--- End of Report ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate weather data from multiple APIs.")
    parser.add_argument("-l", "--location", default="New York", help="The location to fetch weather for (e.g., \"London\").")
    args = parser.parse_args()

    latitude, longitude = get_lat_lon(args.location)

    if latitude and longitude:
        open_meteo_data = fetch_open_meteo(latitude, longitude)
        weather_gov_data = fetch_weather_gov(latitude, longitude)
        
        generate_summary_report(args.location, open_meteo_data, weather_gov_data)
