"""
Autonomous Anomaly & Threat Detection Engine
Evaluates entity streams against tactical operational rules and emits pulsing map flags.
"""

import logging
import time
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class AnomalyEngine:
    """Rules engine identifying operational anomalies across air, sea, and land vectors."""

    def __init__(self) -> None:
        self.active_anomalies: List[Dict[str, Any]] = []

    def evaluate_telemetry(
        self,
        flights: List[Dict[str, Any]],
        vessels: List[Dict[str, Any]],
        wildfires: List[Dict[str, Any]],
        earthquakes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Run all threat detection heuristics and return active flags."""
        anomalies: List[Dict[str, Any]] = []
        now = time.time()

        # 1. Aviation Rules: Emergency squawk codes & anomalous flight parameters
        for flt in flights:
            squawk = flt.get("squawk", "")
            if squawk in ["7700", "7600", "7500"]:
                category = "Aviation Emergency" if squawk == "7700" else "Comm Loss / Hijack Alert"
                anomalies.append({
                    "id": f"anom-flight-{flt['id']}",
                    "target_id": flt["id"],
                    "target_type": "flight",
                    "title": f"SQUAWK {squawk}: {flt.get('callsign', 'UNKNOWN')}",
                    "category": category,
                    "severity": "CRITICAL",
                    "longitude": flt["longitude"],
                    "latitude": flt["latitude"],
                    "altitude": flt.get("altitude", 10000.0),
                    "description": f"Transponder squawking emergency code {squawk}. Origin {flt.get('country', 'N/A')}.",
                    "pulse_color": "#ff0055",
                    "radius_meters": 45000,
                    "timestamp": int(now),
                })

        # 2. Maritime Rules: High-risk choke-point speed anomalies / dark ships
        for v in vessels:
            speed = v.get("speed_knots", 0.0)
            choke = v.get("chokepoint", "")
            # If large tanker stopped in narrow channel (blockage threat)
            if "Strait" in choke and speed < 0.8 and v.get("vessel_type") in ["Oil Tanker", "LNG Tanker"]:
                anomalies.append({
                    "id": f"anom-vessel-{v['id']}",
                    "target_id": v["id"],
                    "target_type": "vessel",
                    "title": f"Chokepoint Stoppage: {v.get('name', 'Vessel')}",
                    "category": "Maritime Navigation Hazard",
                    "severity": "HIGH",
                    "longitude": v["longitude"],
                    "latitude": v["latitude"],
                    "altitude": 0.0,
                    "description": f"Tanker stationary ({speed} kts) inside {choke}. Navigation obstruction risk.",
                    "pulse_color": "#f59e0b",
                    "radius_meters": 25000,
                    "timestamp": int(now),
                })

        # 3. Wildfire Rules: Severe thermal surges
        for fire in wildfires:
            frp = fire.get("frp_mw", 0.0)
            if frp >= 200.0:
                anomalies.append({
                    "id": f"anom-fire-{fire['id']}",
                    "target_id": fire["id"],
                    "target_type": "wildfire",
                    "title": f"Severe Fire Radiative Power ({frp:.0f} MW)",
                    "category": "Thermal Outbreak",
                    "severity": "HIGH",
                    "longitude": fire["longitude"],
                    "latitude": fire["latitude"],
                    "altitude": 0.0,
                    "description": f"Extreme thermal intensity detected by satellite sensor {fire.get('satellite', '')}.",
                    "pulse_color": "#ff3b30",
                    "radius_meters": 30000,
                    "timestamp": int(now),
                })

        # 4. Seismic Rules: Major earthquakes with tsunami potential
        for q in earthquakes:
            mag = q.get("magnitude", 0.0)
            if mag >= 5.5:
                anomalies.append({
                    "id": f"anom-quake-{q['id']}",
                    "target_id": q["id"],
                    "target_type": "earthquake",
                    "title": f"Major Seismic Event M{mag:.1f}",
                    "category": "Seismic Threat",
                    "severity": "CRITICAL" if mag >= 6.0 else "HIGH",
                    "longitude": q["longitude"],
                    "latitude": q["latitude"],
                    "altitude": 0.0,
                    "description": f"{q.get('place', 'Epicenter')}. Depth: {q.get('depth_km', 10)} km. Tsunami Alert: {q.get('tsunami_alert', False)}.",
                    "pulse_color": "#ff007f",
                    "radius_meters": int(q.get("radius_km", 20) * 1000),
                    "timestamp": int(now),
                })

        self.active_anomalies = anomalies
        return self.active_anomalies

    def get_active_anomalies(self) -> List[Dict[str, Any]]:
        """Return the current set of detected operational anomalies."""
        return self.active_anomalies
