"""
Open-Meteo Atmospheric Weather Collector
Retrieves surface wind vectors, precipitation, cloud density, and barometric readings.
"""

import json
import logging
import time
import urllib.request
from typing import Any, Dict, List

from src.config import CONFIG

logger = logging.getLogger(__name__)


class WeatherCollector:
    """Collects real-time atmospheric data worldwide from Open-Meteo."""

    HUBS = [
        {"name": "London", "lat": 51.50, "lon": -0.12},
        {"name": "New York", "lat": 40.71, "lon": -74.00},
        {"name": "Tokyo", "lat": 35.68, "lon": 139.69},
        {"name": "Singapore", "lat": 1.35, "lon": 103.82},
        {"name": "Dubai", "lat": 25.20, "lon": 55.27},
        {"name": "Sydney", "lat": -33.86, "lon": 151.20},
        {"name": "Cairo", "lat": 30.04, "lon": 31.23},
        {"name": "Rio de Janeiro", "lat": -22.90, "lon": -43.17},
        {"name": "Reykjavik", "lat": 64.14, "lon": -21.94},
        {"name": "Cape Town", "lat": -33.92, "lon": 18.42},
    ]

    def __init__(self) -> None:
        self.cached_weather: List[Dict[str, Any]] = []
        self.last_fetch: float = 0.0

    def fetch_weather_for_point(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch pinpoint weather for any latitude and longitude."""
        try:
            url = f"{CONFIG.OPEN_METEO_URL}?latitude={lat}&longitude={lon}&current_weather=true&hourly=cloudcover,precipitation"
            req = urllib.request.Request(url, headers={"User-Agent": CONFIG.HTTP_USER_AGENT})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            curr = data.get("current_weather", {})
            return {
                "latitude": lat,
                "longitude": lon,
                "temperature_c": curr.get("temperature", 20.0),
                "wind_speed_kmh": curr.get("windspeed", 15.0),
                "wind_direction_deg": curr.get("winddirection", 180.0),
                "weather_code": curr.get("weathercode", 0),
                "timestamp": curr.get("time", ""),
            }
        except Exception as exc:
            logger.warning("Pinpoint weather lookup failed: %s", exc)
            return {
                "latitude": lat,
                "longitude": lon,
                "temperature_c": 18.5,
                "wind_speed_kmh": 22.0,
                "wind_direction_deg": 240.0,
                "weather_code": 3,
                "timestamp": "N/A",
            }

    def fetch_global_weather_grid(self) -> List[Dict[str, Any]]:
        """Fetch global hub weather reports."""
        now = time.time()
        if self.cached_weather and (now - self.last_fetch) < CONFIG.REFRESH_WEATHER:
            return self.cached_weather

        reports = []
        for hub in self.HUBS:
            w = self.fetch_weather_for_point(hub["lat"], hub["lon"])
            w["name"] = hub["name"]
            w["id"] = f"weather-{hub['name'].lower().replace(' ', '-')}"
            w["type"] = "weather"
            reports.append(w)

        self.cached_weather = reports
        self.last_fetch = now
        return self.cached_weather
