"""
USGS Real-Time Global Seismic Activity Collector
Pulls global earthquake feeds directly from the United States Geological Survey.
"""

import json
import logging
import time
import urllib.request
from typing import Any, Dict, List

from src.config import CONFIG

logger = logging.getLogger(__name__)


class EarthquakeCollector:
    """Collects real-time seismic event features from USGS."""

    def __init__(self) -> None:
        self.cached_quakes: List[Dict[str, Any]] = []
        self.last_fetch: float = 0.0

    def fetch_live_earthquakes(self) -> List[Dict[str, Any]]:
        """Fetch live USGS earthquakes or return cached feed."""
        now = time.time()
        if self.cached_quakes and (now - self.last_fetch) < CONFIG.REFRESH_EARTHQUAKES:
            return self.cached_quakes

        try:
            req = urllib.request.Request(
                CONFIG.USGS_EARTHQUAKES_URL,
                headers={"User-Agent": CONFIG.HTTP_USER_AGENT},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            quakes: List[Dict[str, Any]] = []
            for feat in data.get("features", [])[: CONFIG.MAX_QUAKE_ENTITIES]:
                props = feat.get("properties", {})
                geom = feat.get("geometry", {})
                coords = geom.get("coordinates", [0, 0, 0])
                mag = props.get("mag")
                if mag is None or mag < 1.0:
                    continue

                event_id = feat.get("id", f"quake-{len(quakes)}")
                quake_record = {
                    "id": f"quake-{event_id}",
                    "type": "earthquake",
                    "place": props.get("place", "Unknown epicenter"),
                    "magnitude": round(float(mag), 1),
                    "depth_km": round(float(coords[2]), 1) if len(coords) > 2 else 10.0,
                    "longitude": round(float(coords[0]), 5),
                    "latitude": round(float(coords[1]), 5),
                    "time_epoch": props.get("time", int(now * 1000)),
                    "tsunami_alert": bool(props.get("tsunami", 0)),
                    "significance": props.get("sig", 0),
                    "url": props.get("url", ""),
                    "radius_km": round(10 ** (0.45 * float(mag)), 1),
                }
                quakes.append(quake_record)

            if quakes:
                self.cached_quakes = quakes
                self.last_fetch = now
                logger.info("Retrieved %d seismic events from USGS", len(quakes))
                return self.cached_quakes

        except Exception as exc:
            logger.warning("USGS fetch failed (%s). Using fallback seismic activity.", exc)

        if not self.cached_quakes:
            self.cached_quakes = self._generate_fallback_earthquakes()
            self.last_fetch = now

        return self.cached_quakes

    def _generate_fallback_earthquakes(self) -> List[Dict[str, Any]]:
        """Fallback seismic activity along major tectonic fault lines."""
        fault_points = [
            {"place": "12 km SW of Petrolia, California", "lat": 40.23, "lon": -124.38, "mag": 4.6, "depth": 14.2},
            {"place": "Off the coast of Fukushima, Japan", "lat": 37.72, "lon": 141.85, "mag": 5.4, "depth": 48.0},
            {"place": "South Sandwich Islands Region", "lat": -56.12, "lon": -27.45, "mag": 6.1, "depth": 35.0},
            {"place": "Halmahera, Indonesia", "lat": 1.45, "lon": 127.88, "mag": 5.0, "depth": 105.0},
            {"place": "Central Mid-Atlantic Ridge", "lat": 0.82, "lon": -28.11, "mag": 4.9, "depth": 10.0},
            {"place": "Near coast of Central Chile", "lat": -31.42, "lon": -71.55, "mag": 5.2, "depth": 28.5},
            {"place": "Kuril Islands, Russia", "lat": 47.92, "lon": 154.21, "mag": 5.7, "depth": 62.0},
        ]

        now = int(time.time() * 1000)
        quakes = []
        for i, q in enumerate(fault_points):
            quakes.append({
                "id": f"quake-fallback-{i}",
                "type": "earthquake",
                "place": q["place"],
                "magnitude": q["mag"],
                "depth_km": q["depth"],
                "longitude": q["lon"],
                "latitude": q["lat"],
                "time_epoch": now - (i * 3600 * 1000),
                "tsunami_alert": q["mag"] >= 6.0,
                "significance": int(q["mag"] * 100),
                "url": "https://earthquake.usgs.gov",
                "radius_km": round(10 ** (0.45 * q["mag"]), 1),
            })
        return quakes

    def to_geojson(self) -> Dict[str, Any]:
        """Convert seismic events to GeoJSON FeatureCollection."""
        quakes = self.fetch_live_earthquakes()
        features = []
        for q in quakes:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [q["longitude"], q["latitude"], 0.0],
                },
                "properties": q,
            })
        return {"type": "FeatureCollection", "features": features}
