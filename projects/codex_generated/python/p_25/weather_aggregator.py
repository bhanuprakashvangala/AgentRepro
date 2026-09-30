#!/usr/bin/env python3
"""Aggregate weather data from multiple APIs and generate comparison report."""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
NOAA_POINTS_URL = "https://api.weather.gov/points/{lat},{lon}"
DEFAULT_USER_AGENT = "WeatherAggregator/1.0 (+contact@example.com)"


@dataclass
class WeatherSnapshot:
    source: str
    current_temperature_c: Optional[float]
    current_condition: Optional[str]
    current_wind_kph: Optional[float]
    daily_high_c: Optional[float]
    daily_low_c: Optional[float]
    precipitation_mm: Optional[float]
    observation_time: Optional[str]


@dataclass
class AggregatedReport:
    latitude: float
    longitude: float
    requested_at: str
    snapshots: List[WeatherSnapshot]
    blended_current_temperature_c: Optional[float]
    blended_daily_high_c: Optional[float]
    blended_daily_low_c: Optional[float]
    notes: List[str]


class WeatherAggregatorError(RuntimeError):
    """Custom exception for weather aggregation failures."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate weather forecasts from multiple APIs")
    parser.add_argument("--latitude", type=float, required=True, help="Latitude in decimal degrees")
    parser.add_argument("--longitude", type=float, required=True, help="Longitude in decimal degrees")
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="Custom User-Agent header (include contact email per NOAA policy)",
    )
    parser.add_argument("--text-output", help="Path to write human-readable summary")
    parser.add_argument("--json-output", help="Path to write JSON report")
    return parser.parse_args()


def fetch_open_meteo(lat: float, lon: float) -> WeatherSnapshot:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone": "auto",
    }
    response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    current = data.get("current_weather", {})
    daily = data.get("daily", {})

    timestamp = current.get("time")
    if timestamp:
        try:
            timestamp = datetime.fromisoformat(timestamp).isoformat()
        except ValueError:
            pass

    snapshot = WeatherSnapshot(
        source="open-meteo",
        current_temperature_c=_to_float(current.get("temperature")),
        current_condition=None,
        current_wind_kph=_ms_to_kph(current.get("windspeed")),
        daily_high_c=_first_item(daily.get("temperature_2m_max")),
        daily_low_c=_first_item(daily.get("temperature_2m_min")),
        precipitation_mm=_first_item(daily.get("precipitation_sum")),
        observation_time=timestamp,
    )
    return snapshot


def fetch_noaa(lat: float, lon: float, user_agent: str) -> WeatherSnapshot:
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/geo+json",
    }
    metadata_resp = requests.get(
        NOAA_POINTS_URL.format(lat=lat, lon=lon), headers=headers, timeout=10
    )
    metadata_resp.raise_for_status()
    metadata = metadata_resp.json()

    properties = metadata.get("properties", {})
    hourly_url = properties.get("forecastHourly")
    daily_url = properties.get("forecast")

    current_temp = None
    current_condition = None
    observation_time = None

    if hourly_url:
        hourly_resp = requests.get(hourly_url, headers=headers, timeout=10)
        hourly_resp.raise_for_status()
        hourly_data = hourly_resp.json()
        periods = hourly_data.get("properties", {}).get("periods", [])
        if periods:
            period = periods[0]
            current_temp = _fahrenheit_to_celsius(period.get("temperature"))
            current_condition = period.get("shortForecast")
            observation_time = period.get("startTime")

    daily_high = None
    daily_low = None
    precipitation_mm = None

    if daily_url:
        daily_resp = requests.get(daily_url, headers=headers, timeout=10)
        daily_resp.raise_for_status()
        daily_data = daily_resp.json()
        daily_periods = daily_data.get("properties", {}).get("periods", [])
        if daily_periods:
            today_periods = daily_periods[:2]
            highs = [
                _fahrenheit_to_celsius(p.get("temperature"))
                for p in today_periods
                if p.get("isDaytime") and p.get("temperatureUnit") == "F"
            ]
            lows = [
                _fahrenheit_to_celsius(p.get("temperature"))
                for p in today_periods
                if not p.get("isDaytime") and p.get("temperatureUnit") == "F"
            ]
            if highs:
                daily_high = max(highs)
            if lows:
                daily_low = min(lows)

    snapshot = WeatherSnapshot(
        source="noaa",
        current_temperature_c=current_temp,
        current_condition=current_condition,
        current_wind_kph=None,
        daily_high_c=daily_high,
        daily_low_c=daily_low,
        precipitation_mm=precipitation_mm,
        observation_time=observation_time,
    )
    return snapshot


def aggregate_snapshots(lat: float, lon: float, snapshots: List[WeatherSnapshot]) -> AggregatedReport:
    temps = [snap.current_temperature_c for snap in snapshots if snap.current_temperature_c is not None]
    highs = [snap.daily_high_c for snap in snapshots if snap.daily_high_c is not None]
    lows = [snap.daily_low_c for snap in snapshots if snap.daily_low_c is not None]

    blended_temp = _mean(temps)
    blended_high = _mean(highs)
    blended_low = _mean(lows)

    notes: List[str] = []
    if len(temps) >= 2:
        diff = abs(temps[0] - temps[1])
        notes.append(f"Current temperature difference between sources: {diff:.1f}°C")
    if blended_high and blended_low:
        notes.append(
            f"Blended high/low estimate: {blended_high:.1f}°C / {blended_low:.1f}°C"
        )

    report = AggregatedReport(
        latitude=lat,
        longitude=lon,
        requested_at=datetime.utcnow().isoformat() + "Z",
        snapshots=snapshots,
        blended_current_temperature_c=blended_temp,
        blended_daily_high_c=blended_high,
        blended_daily_low_c=blended_low,
        notes=notes,
    )
    return report


def generate_text_summary(report: AggregatedReport) -> str:
    lines = []
    lines.append("Weather Forecast Summary")
    lines.append("=======================")
    lines.append(f"Location: {report.latitude:.4f}, {report.longitude:.4f}")
    lines.append(f"Generated at: {report.requested_at}")
    lines.append("")

    for snapshot in report.snapshots:
        lines.append(f"Source: {snapshot.source}")
        lines.append(
            f"  Current temperature: {format_temperature(snapshot.current_temperature_c)}"
        )
        if snapshot.current_condition:
            lines.append(f"  Conditions: {snapshot.current_condition}")
        if snapshot.current_wind_kph is not None:
            lines.append(f"  Wind: {snapshot.current_wind_kph:.1f} km/h")
        lines.append(
            f"  Daily high/low: {format_temperature(snapshot.daily_high_c)} / {format_temperature(snapshot.daily_low_c)}"
        )
        if snapshot.precipitation_mm is not None:
            lines.append(f"  Precipitation: {snapshot.precipitation_mm:.1f} mm")
        if snapshot.observation_time:
            lines.append(f"  Observation time: {snapshot.observation_time}")
        lines.append("")

    if report.blended_current_temperature_c is not None:
        lines.append(
            f"Blended current temperature: {report.blended_current_temperature_c:.1f}°C"
        )
    if report.blended_daily_high_c is not None and report.blended_daily_low_c is not None:
        lines.append(
            f"Blended high/low: {report.blended_daily_high_c:.1f}°C / {report.blended_daily_low_c:.1f}°C"
        )

    if report.notes:
        lines.append("")
        lines.append("Notes:")
        for note in report.notes:
            lines.append(f"  - {note}")

    return "\n".join(lines)


def format_temperature(temp: Optional[float]) -> str:
    if temp is None or math.isnan(temp):
        return "n/a"
    return f"{temp:.1f}°C"


def _first_item(values: Optional[List[float]]) -> Optional[float]:
    if not values:
        return None
    return _to_float(values[0])


def _to_float(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _ms_to_kph(value) -> Optional[float]:
    val = _to_float(value)
    if val is None:
        return None
    return val * 3.6


def _fahrenheit_to_celsius(value) -> Optional[float]:
    val = _to_float(value)
    if val is None:
        return None
    return (val - 32) * 5.0 / 9.0


def _mean(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def write_outputs(report: AggregatedReport, text_path: Optional[str], json_path: Optional[str]) -> None:
    if text_path:
        Path(text_path).write_text(generate_text_summary(report), encoding="utf-8")
        print(f"Text summary written to {text_path}")
    if json_path:
        payload = asdict(report)
        Path(json_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"JSON report written to {json_path}")


def main() -> None:
    args = parse_args()

    try:
        open_meteo_snapshot = fetch_open_meteo(args.latitude, args.longitude)
    except requests.RequestException as exc:
        raise WeatherAggregatorError(f"Open-Meteo request failed: {exc}") from exc

    try:
        noaa_snapshot = fetch_noaa(args.latitude, args.longitude, args.user_agent)
    except requests.RequestException as exc:
        raise WeatherAggregatorError(f"NOAA request failed: {exc}") from exc

    snapshots = [open_meteo_snapshot, noaa_snapshot]
    report = aggregate_snapshots(args.latitude, args.longitude, snapshots)

    print(generate_text_summary(report))

    write_outputs(report, args.text_output, args.json_output)


if __name__ == "__main__":
    try:
        main()
    except WeatherAggregatorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
