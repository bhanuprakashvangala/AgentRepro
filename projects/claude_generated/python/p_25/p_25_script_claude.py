"""
Weather Data Aggregator
Fetches weather data from multiple APIs, aggregates results, and generates reports.
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import statistics


class WeatherAggregator:
    """Aggregates weather data from multiple weather APIs."""

    def __init__(self):
        """Initialize the weather aggregator."""
        self.results = []
        self.apis_used = []

    def fetch_openmeteo_data(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Fetch weather data from Open-Meteo API (free, no API key required).

        Args:
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Dictionary containing weather data or None if request fails
        """
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": "auto",
                "forecast_days": 7
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            result = {
                "source": "Open-Meteo",
                "current": {
                    "temperature": data["current"]["temperature_2m"],
                    "humidity": data["current"]["relative_humidity_2m"],
                    "wind_speed": data["current"]["wind_speed_10m"],
                    "conditions": self._interpret_weather_code(data["current"]["weather_code"])
                },
                "forecast": []
            }

            # Parse daily forecast
            for i in range(len(data["daily"]["time"])):
                result["forecast"].append({
                    "date": data["daily"]["time"][i],
                    "temp_max": data["daily"]["temperature_2m_max"][i],
                    "temp_min": data["daily"]["temperature_2m_min"][i],
                    "precipitation": data["daily"]["precipitation_sum"][i]
                })

            self.apis_used.append("Open-Meteo")
            return result

        except requests.exceptions.RequestException as e:
            print(f"Error fetching Open-Meteo data: {e}")
            return None

    def fetch_wttr_data(self, location: str) -> Optional[Dict]:
        """
        Fetch weather data from wttr.in (free, no API key required).

        Args:
            location: City name

        Returns:
            Dictionary containing weather data or None if request fails
        """
        try:
            url = f"https://wttr.in/{location}"
            params = {"format": "j1"}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            current = data["current_condition"][0]
            result = {
                "source": "wttr.in",
                "current": {
                    "temperature": float(current["temp_F"]),
                    "humidity": float(current["humidity"]),
                    "wind_speed": float(current["windspeedMiles"]),
                    "conditions": current["weatherDesc"][0]["value"]
                },
                "forecast": []
            }

            # Parse daily forecast
            for day in data["weather"]:
                result["forecast"].append({
                    "date": day["date"],
                    "temp_max": float(day["maxtempF"]),
                    "temp_min": float(day["mintempF"]),
                    "precipitation": float(day["totalprecipMM"]) / 25.4  # Convert mm to inches
                })

            self.apis_used.append("wttr.in")
            return result

        except requests.exceptions.RequestException as e:
            print(f"Error fetching wttr.in data: {e}")
            return None

    def _interpret_weather_code(self, code: int) -> str:
        """Convert Open-Meteo weather code to description."""
        codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog", 51: "Light drizzle",
            53: "Moderate drizzle", 55: "Dense drizzle", 61: "Slight rain",
            63: "Moderate rain", 65: "Heavy rain", 71: "Slight snow",
            73: "Moderate snow", 75: "Heavy snow", 95: "Thunderstorm"
        }
        return codes.get(code, f"Unknown ({code})")

    def aggregate_data(self, location: str, latitude: float, longitude: float) -> List[Dict]:
        """
        Fetch and aggregate weather data from multiple APIs.

        Args:
            location: City name
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            List of weather data dictionaries from different sources
        """
        print(f"\n{'='*60}")
        print(f"Fetching weather data for: {location}")
        print(f"Coordinates: {latitude}, {longitude}")
        print(f"{'='*60}\n")

        self.results = []
        self.apis_used = []

        # Fetch from Open-Meteo (always free, no key required)
        print("Fetching from Open-Meteo API...")
        openmeteo_data = self.fetch_openmeteo_data(latitude, longitude)
        if openmeteo_data:
            self.results.append(openmeteo_data)
            print("✓ Open-Meteo data retrieved successfully")

        # Fetch from wttr.in (free, no key required)
        print("\nFetching from wttr.in API...")
        wttr_data = self.fetch_wttr_data(location)
        if wttr_data:
            self.results.append(wttr_data)
            print("✓ wttr.in data retrieved successfully")

        print(f"\n{'='*60}")
        print(f"Successfully retrieved data from {len(self.results)} source(s)")
        print(f"{'='*60}\n")

        return self.results

    def compare_data(self) -> Dict:
        """
        Compare and aggregate weather data from different sources.

        Returns:
            Dictionary containing comparison statistics
        """
        if not self.results:
            return {"error": "No data to compare"}

        # Aggregate current conditions
        temperatures = [r["current"]["temperature"] for r in self.results]
        humidities = [r["current"]["humidity"] for r in self.results]
        wind_speeds = [r["current"]["wind_speed"] for r in self.results]

        comparison = {
            "sources_count": len(self.results),
            "sources": [r["source"] for r in self.results],
            "current_conditions": {
                "temperature": {
                    "average": round(statistics.mean(temperatures), 1),
                    "min": round(min(temperatures), 1),
                    "max": round(max(temperatures), 1),
                    "by_source": {r["source"]: r["current"]["temperature"] for r in self.results}
                },
                "humidity": {
                    "average": round(statistics.mean(humidities), 1),
                    "min": round(min(humidities), 1),
                    "max": round(max(humidities), 1),
                    "by_source": {r["source"]: r["current"]["humidity"] for r in self.results}
                },
                "wind_speed": {
                    "average": round(statistics.mean(wind_speeds), 1),
                    "min": round(min(wind_speeds), 1),
                    "max": round(max(wind_speeds), 1),
                    "by_source": {r["source"]: r["current"]["wind_speed"] for r in self.results}
                },
                "conditions": {r["source"]: r["current"]["conditions"] for r in self.results}
            }
        }

        # Aggregate forecast data
        forecast_comparison = []
        max_forecast_days = min(len(r["forecast"]) for r in self.results)

        for day_idx in range(max_forecast_days):
            temps_max = [r["forecast"][day_idx]["temp_max"] for r in self.results]
            temps_min = [r["forecast"][day_idx]["temp_min"] for r in self.results]
            precip = [r["forecast"][day_idx]["precipitation"] for r in self.results]

            forecast_comparison.append({
                "date": self.results[0]["forecast"][day_idx]["date"],
                "temp_max": {
                    "average": round(statistics.mean(temps_max), 1),
                    "range": [round(min(temps_max), 1), round(max(temps_max), 1)]
                },
                "temp_min": {
                    "average": round(statistics.mean(temps_min), 1),
                    "range": [round(min(temps_min), 1), round(max(temps_min), 1)]
                },
                "precipitation": {
                    "average": round(statistics.mean(precip), 2),
                    "max": round(max(precip), 2)
                }
            })

        comparison["forecast"] = forecast_comparison

        return comparison

    def generate_report(self, comparison: Dict, location: str) -> str:
        """Generate a human-readable weather forecast summary report."""
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append(f"WEATHER FORECAST SUMMARY REPORT - {location.upper()}")
        report_lines.append("=" * 70)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Data Sources: {', '.join(comparison['sources'])}")
        report_lines.append("=" * 70)

        # Current Conditions
        report_lines.append("\nCURRENT CONDITIONS")
        report_lines.append("-" * 70)

        curr = comparison["current_conditions"]
        report_lines.append(f"Temperature: {curr['temperature']['average']}°F")
        report_lines.append(f"  Range across sources: {curr['temperature']['min']}°F - {curr['temperature']['max']}°F")

        report_lines.append(f"\nHumidity: {curr['humidity']['average']}%")
        report_lines.append(f"  Range across sources: {curr['humidity']['min']}% - {curr['humidity']['max']}%")

        report_lines.append(f"\nWind Speed: {curr['wind_speed']['average']} mph")

        report_lines.append(f"\nConditions by source:")
        for source, condition in curr["conditions"].items():
            report_lines.append(f"  {source}: {condition}")

        # Forecast
        report_lines.append("\n" + "=" * 70)
        report_lines.append("7-DAY FORECAST SUMMARY")
        report_lines.append("=" * 70)

        for day in comparison["forecast"]:
            report_lines.append(f"\n{day['date']}")
            report_lines.append("-" * 70)
            report_lines.append(f"  High: {day['temp_max']['average']}°F (range: {day['temp_max']['range'][0]}°F - {day['temp_max']['range'][1]}°F)")
            report_lines.append(f"  Low:  {day['temp_min']['average']}°F (range: {day['temp_min']['range'][0]}°F - {day['temp_min']['range'][1]}°F)")
            report_lines.append(f"  Precipitation: {day['precipitation']['average']} inches")

        report_lines.append("\n" + "=" * 70)

        return "\n".join(report_lines)

    def save_report(self, report: str, filename: str = "weather_report.txt"):
        """Save text report to file."""
        with open(filename, 'w') as f:
            f.write(report)
        print(f"Report saved to {filename}")


def main():
    """Main execution function with example usage."""
    # Example: New York City
    location = "New York"
    latitude = 40.7128
    longitude = -74.0060

    # Initialize aggregator
    aggregator = WeatherAggregator()

    # Fetch and aggregate data
    results = aggregator.aggregate_data(location, latitude, longitude)

    if not results:
        print("Error: Could not fetch data from any weather API")
        return

    # Compare data from different sources
    comparison = aggregator.compare_data()

    # Generate human-readable report
    report = aggregator.generate_report(comparison, location)

    # Display and save report
    print(report)
    aggregator.save_report(report)


if __name__ == "__main__":
    main()
