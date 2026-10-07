"""
Geofencing & Zone Breach Engine
Provides spatial point-in-polygon testing, entry/exit state tracking, and breach alerts.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


def is_point_in_polygon(lon: float, lat: float, polygon_coords: List[List[float]]) -> bool:
    """
    Ray casting point-in-polygon algorithm.
    polygon_coords format: [[lon1, lat1], [lon2, lat2], ...]
    """
    n = len(polygon_coords)
    if n < 3:
        return False

    inside = False
    p1x, p1y = polygon_coords[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon_coords[i % n]
        if lat > min(p1y, p2y):
            if lat <= max(p1y, p2y):
                if lon <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or lon <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


class GeofenceManager:
    """Manages active zones, evaluates telemetry streams, and emits breach alerts."""

    def __init__(self) -> None:
        self.zones: Dict[str, Dict[str, Any]] = {}
        # Track entity state: (zone_id, entity_id) -> timestamp
        self._occupants: Dict[str, Set[str]] = {}
        self.active_alerts: List[Dict[str, Any]] = []

        # Seed with initial tactical demonstration zones
        self._seed_default_zones()

    def _seed_default_zones(self) -> None:
        """Add predefined high-interest operational monitoring zones."""
        self.add_zone(
            zone_id="zone-hormuz-exclusion",
            name="Strait of Hormuz Security Perimeter",
            polygon=[
                [55.80, 26.00],
                [57.00, 26.00],
                [57.00, 27.20],
                [55.80, 27.20],
            ],
            alert_types=["vessel", "flight"],
            description="Monitored maritime corridor for unauthorized naval ingress.",
            color="#ff0055",
        )
        self.add_zone(
            zone_id="zone-london-airspace",
            name="London Metropolitan Airspace Restricted Sector",
            polygon=[
                [-0.50, 51.35],
                [0.20, 51.35],
                [0.20, 51.65],
                [-0.50, 51.65],
            ],
            alert_types=["flight"],
            description="Terminal control area flight surveillance zone.",
            color="#00f0ff",
        )

    def add_zone(
        self,
        zone_id: str,
        name: str,
        polygon: List[List[float]],
        alert_types: Optional[List[str]] = None,
        description: str = "",
        color: str = "#ff0055",
    ) -> Dict[str, Any]:
        """Registers a new geofence zone."""
        zone = {
            "id": zone_id,
            "name": name,
            "polygon": polygon,
            "alert_types": alert_types or ["flight", "vessel", "wildfire"],
            "description": description,
            "color": color,
            "created_at": int(time.time()),
        }
        self.zones[zone_id] = zone
        if zone_id not in self._occupants:
            self._occupants[zone_id] = set()
        logger.info("Registered geofence: %s (%s)", name, zone_id)
        return zone

    def remove_zone(self, zone_id: str) -> bool:
        """Removes a geofence zone."""
        if zone_id in self.zones:
            del self.zones[zone_id]
            self._occupants.pop(zone_id, None)
            return True
        return False

    def list_zones(self) -> List[Dict[str, Any]]:
        """Return list of all configured geofences."""
        return list(self.zones.values())

    def evaluate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check all entities against active geofences.
        Returns newly triggered breach events.
        """
        breaches: List[Dict[str, Any]] = []
        now = time.time()

        for zone_id, zone in self.zones.items():
            poly = zone["polygon"]
            allowed_types = set(zone["alert_types"])
            current_occupants: Set[str] = set()

            for ent in entities:
                ent_type = ent.get("type", "")
                if ent_type not in allowed_types:
                    continue

                lon = ent.get("longitude")
                lat = ent.get("latitude")
                if lon is None or lat is None:
                    continue

                if is_point_in_polygon(lon, lat, poly):
                    ent_id = ent.get("id", f"{ent_type}-{lon}-{lat}")
                    current_occupants.add(ent_id)

                    # Check if this is a newly entered breach
                    if ent_id not in self._occupants[zone_id]:
                        alert = {
                            "id": f"breach-{zone_id}-{ent_id}-{int(now)}",
                            "type": "geofence_breach",
                            "event": "ZONE_ENTRY",
                            "zone_id": zone_id,
                            "zone_name": zone["name"],
                            "entity_id": ent_id,
                            "entity_type": ent_type,
                            "callsign_or_name": ent.get("callsign") or ent.get("name") or ent_id,
                            "longitude": lon,
                            "latitude": lat,
                            "timestamp": int(now),
                            "severity": "HIGH",
                            "description": f"Entity [{ent.get('callsign') or ent.get('name') or ent_id}] breached {zone['name']}",
                        }
                        breaches.append(alert)
                        self.active_alerts.append(alert)
                        logger.warning("Geofence breach detected: %s in %s", ent_id, zone["name"])

            # Update occupants tracking
            self._occupants[zone_id] = current_occupants

        # Limit alert history buffer
        if len(self.active_alerts) > 100:
            self.active_alerts = self.active_alerts[-100:]

        return breaches
