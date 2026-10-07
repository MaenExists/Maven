"""
Live CCTV & Street Surveillance Camera Feed Collector
Aggregates public traffic cameras from TfL London, Caltrans California, and international feeds.
"""

import json
import logging
import time
import urllib.request
from typing import Any, Dict, List

from src.config import CONFIG

logger = logging.getLogger(__name__)


class CameraCollector:
    """Collects real-time public surveillance and street traffic camera streams."""

    GLOBAL_LANDMARK_CAMS = [
        {
            "id": "cam-tokyo-shibuya",
            "name": "Tokyo - Shibuya Scramble Crossing",
            "city": "Tokyo, Japan",
            "latitude": 35.6595,
            "longitude": 139.7005,
            "image_url": "https://images.earthcam.com/cams/shibuya/tokyo.jpg",
            "stream_url": "https://www.youtube.com/watch?v=HpdO5Kq3o7Y",
            "type": "live_cam",
            "direction": "Intersection Overview",
        },
        {
            "id": "cam-nyc-timessquare",
            "name": "New York City - Times Square 46th St",
            "city": "New York, USA",
            "latitude": 40.7580,
            "longitude": -73.9855,
            "image_url": "https://images.earthcam.com/cams/timessquare/ts.jpg",
            "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA",
            "type": "live_cam",
            "direction": "Southbound Broadway",
        },
        {
            "id": "cam-paris-eiffel",
            "name": "Paris - Pont d'Iena / Eiffel Tower",
            "city": "Paris, France",
            "latitude": 48.8584,
            "longitude": 2.2945,
            "image_url": "https://static.skylinewebcams.com/livecams/france/paris/eiffel.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "Champ de Mars",
        },
        {
            "id": "cam-sydney-harbour",
            "name": "Sydney - Circular Quay & Harbour Bridge",
            "city": "Sydney, Australia",
            "latitude": -33.8568,
            "longitude": 151.2153,
            "image_url": "https://webcams.sydney.com/harbour.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "North Port Entrance",
        },
    ]

    def __init__(self) -> None:
        self.cached_cameras: List[Dict[str, Any]] = []
        self.last_fetch: float = 0.0

    def fetch_live_cameras(self) -> List[Dict[str, Any]]:
        """Fetch cameras from TfL, Caltrans, and global landmarks."""
        now = time.time()
        if self.cached_cameras and (now - self.last_fetch) < CONFIG.REFRESH_CAMERAS:
            return self.cached_cameras

        cams: List[Dict[str, Any]] = list(self.GLOBAL_LANDMARK_CAMS)

        # 1. Transport for London JamCams
        try:
            req = urllib.request.Request(
                CONFIG.TFL_JAMCAMS_URL,
                headers={"User-Agent": CONFIG.HTTP_USER_AGENT},
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                tfl_data = json.loads(resp.read().decode("utf-8"))

            for item in tfl_data[:500]:
                lat = item.get("lat")
                lon = item.get("lon")
                if lat is None or lon is None:
                    continue

                img_url = ""
                video_url = ""
                view_dir = "Traffic Cam"

                for prop in item.get("additionalProperties", []):
                    key = prop.get("key")
                    val = prop.get("value")
                    if key == "imageUrl":
                        img_url = val
                    elif key == "videoUrl":
                        video_url = val
                    elif key == "view":
                        view_dir = val

                if img_url:
                    cams.append({
                        "id": f"cam-tfl-{item.get('id', len(cams))}",
                        "name": item.get("commonName", "TfL Street Cam"),
                        "city": "London, UK",
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "image_url": img_url,
                        "stream_url": video_url,
                        "type": "live_cam",
                        "direction": view_dir,
                    })
            logger.info("Retrieved %d TfL JamCams", len(cams) - len(self.GLOBAL_LANDMARK_CAMS))
        except Exception as exc:
            logger.warning("TfL camera fetch failed: %s", exc)

        # 2. Caltrans California Highway CCTV
        try:
            req = urllib.request.Request(
                CONFIG.CALTRANS_D04_URL,
                headers={"User-Agent": CONFIG.HTTP_USER_AGENT},
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                caltrans_data = json.loads(resp.read().decode("utf-8"))

            for entry in caltrans_data.get("data", [])[:400]:
                cctv = entry.get("cctv", {})
                loc = cctv.get("location", {})
                img_data = cctv.get("imageData", {})
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                if lat is None or lon is None:
                    continue

                img_url = img_data.get("static", {}).get("currentImageURL", "")
                streaming_url = img_data.get("streamingVideoURL", "")
                loc_name = loc.get("locationName", "Highway Cam")
                nearby = loc.get("nearbyPlace", "California")

                if img_url:
                    cams.append({
                        "id": f"cam-caltrans-{cctv.get('index', len(cams))}",
                        "name": f"{loc_name} ({nearby})",
                        "city": f"California ({loc.get('county', 'CA')})",
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "image_url": img_url,
                        "stream_url": streaming_url,
                        "type": "live_cam",
                        "direction": loc.get("direction", "Highway Overview"),
                    })
            logger.info("Total cameras aggregated: %d", len(cams))
        except Exception as exc:
            logger.warning("Caltrans camera fetch failed: %s", exc)

        self.cached_cameras = cams
        self.last_fetch = now
        return self.cached_cameras

    def to_geojson(self) -> Dict[str, Any]:
        """Convert cameras to GeoJSON FeatureCollection."""
        cams = self.fetch_live_cameras()
        features = []
        for c in cams:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [c["longitude"], c["latitude"], 0.0],
                },
                "properties": c,
            })
        return {"type": "FeatureCollection", "features": features}
