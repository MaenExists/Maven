"""
Global Maritime AIS Collector
Tracks global shipping traffic across major oceanic corridors and maritime choke points.
"""

import json
import logging
import math
import random
import time
from typing import Any, Dict, List

from src.config import CONFIG

logger = logging.getLogger(__name__)


class MaritimeCollector:
    """Collects and simulates real-time commercial and military vessel positions."""

    CHOKEPOINTS = [
        {"name": "Strait of Malacca", "lat": 1.25, "lon": 103.80, "bearing": 305, "density": 80},
        {"name": "Suez Canal & Red Sea", "lat": 29.97, "lon": 32.55, "bearing": 160, "density": 60},
        {"name": "Strait of Hormuz", "lat": 26.56, "lon": 56.25, "bearing": 80, "density": 50},
        {"name": "Panama Canal", "lat": 9.08, "lon": -79.68, "bearing": 320, "density": 45},
        {"name": "Strait of Gibraltar", "lat": 35.96, "lon": -5.60, "bearing": 90, "density": 65},
        {"name": "English Channel", "lat": 50.50, "lon": 0.50, "bearing": 240, "density": 70},
        {"name": "Singapore Anchorage", "lat": 1.20, "lon": 103.75, "bearing": 0, "density": 90},
        {"name": "Rotterdam Approaches", "lat": 51.98, "lon": 4.02, "bearing": 270, "density": 55},
        {"name": "Shanghai Deepwater Port", "lat": 30.60, "lon": 122.10, "bearing": 110, "density": 85},
        {"name": "Bab-el-Mandeb", "lat": 12.58, "lon": 43.33, "bearing": 140, "density": 40},
    ]

    VESSEL_TYPES = ["Container", "Oil Tanker", "Bulk Carrier", "LNG Tanker", "Naval Recon", "Tug", "General Cargo"]

    def __init__(self) -> None:
        self.cached_vessels: List[Dict[str, Any]] = []
        self.last_update: float = 0.0
        self._initialize_vessel_fleet()

    def _initialize_vessel_fleet(self) -> None:
        """Populate global vessel fleet along realistic shipping routes."""
        random.seed(1337)
        vessels = []
        mmsi_counter = 211000000

        for choke in self.CHOKEPOINTS:
            density = choke["density"]
            base_lat = choke["lat"]
            base_lon = choke["lon"]
            base_bearing = choke["bearing"]

            for i in range(density):
                mmsi = mmsi_counter + len(vessels)
                v_type = random.choice(self.VESSEL_TYPES)
                
                # Offset position along shipping lane axis
                dist_offset = random.uniform(-1.2, 1.2)
                lat_offset = dist_offset * math.cos(math.radians(base_bearing)) + random.uniform(-0.15, 0.15)
                lon_offset = dist_offset * math.sin(math.radians(base_bearing)) + random.uniform(-0.15, 0.15)
                
                speed = random.uniform(8.5, 21.0) if "Anchorage" not in choke["name"] else random.uniform(0.0, 1.5)
                heading = (base_bearing + random.choice([0, 180]) + random.uniform(-15, 15)) % 360
                
                names = ["MAERSK", "EVERGREEN", "MSC", "COSCO", "CMA CGM", "HAPAG-LLOYD", "ONE", "VALE", "STENA"]
                name = f"{random.choice(names)} {random.choice(['VOYAGER', 'LEVIATHAN', 'TITAN', 'AURORA', 'PACIFIC', 'ATLANTIC', 'HORIZON', 'PIONEER'])}"

                vessels.append({
                    "id": f"vessel-{mmsi}",
                    "type": "vessel",
                    "mmsi": mmsi,
                    "name": name,
                    "vessel_type": v_type,
                    "chokepoint": choke["name"],
                    "latitude": round(base_lat + lat_offset, 5),
                    "longitude": round(base_lon + lon_offset, 5),
                    "speed_knots": round(speed, 1),
                    "heading": round(heading, 1),
                    "draught_m": round(random.uniform(7.0, 16.5), 1),
                    "length_m": random.randint(120, 400),
                    "destination": random.choice(["ROTTERDAM", "SINGAPORE", "SHANGHAI", "BUSAN", "LOS ANGELES", "HOUSTON"]),
                    "status": "Underway Using Engine" if speed > 1.0 else "Moored / At Anchor",
                    "flag": random.choice(["Panama", "Liberia", "Marshall Islands", "Singapore", "Hong Kong", "Malta"]),
                    "last_ais_update": int(time.time()),
                })

        self.cached_vessels = vessels
        self.last_update = time.time()
        logger.info("Initialized maritime fleet with %d active vessels", len(self.cached_vessels))

    def fetch_live_vessels(self) -> List[Dict[str, Any]]:
        """Dead-reckoning position simulation step over elapsed time."""
        now = time.time()
        elapsed_hours = (now - self.last_update) / 3600.0
        self.last_update = now

        for v in self.cached_vessels:
            if v["speed_knots"] > 0.5:
                # 1 knot = 1 nautical mile per hour ≈ 1/60th of a degree latitude
                nm_travelled = v["speed_knots"] * elapsed_hours
                rad_heading = math.radians(v["heading"])
                d_lat = (nm_travelled / 60.0) * math.cos(rad_heading)
                d_lon = (nm_travelled / (60.0 * max(0.1, math.cos(math.radians(v["latitude"]))))) * math.sin(rad_heading)

                v["latitude"] = round(v["latitude"] + d_lat, 5)
                v["longitude"] = round(v["longitude"] + d_lon, 5)
                v["last_ais_update"] = int(now)

        return self.cached_vessels

    def to_geojson(self) -> Dict[str, Any]:
        """Convert vessels to GeoJSON FeatureCollection."""
        vessels = self.fetch_live_vessels()
        features = []
        for v in vessels:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [v["longitude"], v["latitude"], 0.0],
                },
                "properties": v,
            })
        return {"type": "FeatureCollection", "features": features}
