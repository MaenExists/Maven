"""
Geodesic Measurements Engine
Computes great-circle distances, azimuth/bearing, and spherical polygon surface area.
"""

import math
from typing import Any, Dict, List, Tuple


class MeasurementEngine:
    """Geodetic math operations on WGS84 / spherical Earth."""

    EARTH_RADIUS_KM: float = 6371.0088

    @classmethod
    def haversine_distance(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> Dict[str, float]:
        """Compute great-circle distance between two coordinates."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        dist_km = cls.EARTH_RADIUS_KM * c
        dist_nm = dist_km * 0.539957
        dist_miles = dist_km * 0.621371

        return {
            "distance_km": round(dist_km, 2),
            "distance_nm": round(dist_nm, 2),
            "distance_miles": round(dist_miles, 2),
        }

    @classmethod
    def calculate_bearing(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate forward azimuth / bearing from point 1 to point 2 (0 to 360 degrees)."""
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_lambda = math.radians(lon2 - lon1)

        y = math.sin(delta_lambda) * math.cos(phi2)
        x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
        theta = math.atan2(y, x)
        bearing = (math.degrees(theta) + 360.0) % 360.0
        return round(bearing, 1)

    @classmethod
    def polygon_area(cls, coordinates: List[List[float]]) -> Dict[str, float]:
        """
        Compute surface area of spherical polygon (coordinates: [[lon, lat], ...])
        using Girard's spherical excess theorem.
        """
        if len(coordinates) < 3:
            return {"area_km2": 0.0, "area_nm2": 0.0, "hectares": 0.0}

        total = 0.0
        n = len(coordinates)

        for i in range(n):
            j = (i + 1) % n
            k = (i + 2) % n
            p1 = coordinates[i]
            p2 = coordinates[j]
            p3 = coordinates[k]

            lon1, lat1 = math.radians(p1[0]), math.radians(p1[1])
            lon2, lat2 = math.radians(p2[0]), math.radians(p2[1])
            lon3, lat3 = math.radians(p3[0]), math.radians(p3[1])

            total += (lon3 - lon1) * math.sin(lat2)

        area_km2 = abs(total * (cls.EARTH_RADIUS_KM ** 2) / 2.0)
        area_nm2 = area_km2 * 0.291553
        hectares = area_km2 * 100.0

        return {
            "area_km2": round(area_km2, 2),
            "area_nm2": round(area_nm2, 2),
            "hectares": round(hectares, 1),
        }
