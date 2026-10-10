"""
Live CCTV & Street Surveillance Camera Feed Collector
Aggregates public traffic cameras from TfL London, Caltrans California, Singapore LTA,
and major global municipal and landmark street webcams.
"""

import json
import logging
import math
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
        {
            "id": "cam-rome-colosseum",
            "name": "Rome - Piazza del Colosseo",
            "city": "Rome, Italy",
            "latitude": 41.8902,
            "longitude": 12.4922,
            "image_url": "https://static.skylinewebcams.com/livecams/italia/roma/colosseo.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "South Arcade View",
        },
        {
            "id": "cam-venice-rialto",
            "name": "Venice - Grand Canal & Rialto Bridge",
            "city": "Venice, Italy",
            "latitude": 45.4380,
            "longitude": 12.3359,
            "image_url": "https://static.skylinewebcams.com/livecams/italia/veneto/venezia-rialto.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "Canal Grande North",
        },
        {
            "id": "cam-dubai-marina",
            "name": "Dubai - Marina Boulevard & Sheikh Zayed Rd",
            "city": "Dubai, UAE",
            "latitude": 25.0805,
            "longitude": 55.1403,
            "image_url": "https://images.earthcam.com/cams/dubai/marina.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "Boulevard Transit",
        },
        {
            "id": "cam-berlin-brandenburg",
            "name": "Berlin - Pariser Platz / Brandenburger Tor",
            "city": "Berlin, Germany",
            "latitude": 52.5163,
            "longitude": 13.3777,
            "image_url": "https://images.earthcam.com/cams/berlin/gate.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "Unter den Linden",
        },
        {
            "id": "cam-sf-goldengate",
            "name": "San Francisco - Golden Gate Vista Point",
            "city": "San Francisco, USA",
            "latitude": 37.8280,
            "longitude": -122.4800,
            "image_url": "https://images.earthcam.com/cams/sanfrancisco/goldengate.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "North Anchorage View",
        },
        {
            "id": "cam-hongkong-harbour",
            "name": "Hong Kong - Victoria Harbour & Tsim Sha Tsui",
            "city": "Hong Kong",
            "latitude": 22.2936,
            "longitude": 114.1733,
            "image_url": "https://images.earthcam.com/cams/hongkong/victoria.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "Harbour Skyline",
        },
        {
            "id": "cam-singapore-mbs",
            "name": "Singapore - Marina Bay Sands Promenade",
            "city": "Singapore",
            "latitude": 1.2838,
            "longitude": 103.8591,
            "image_url": "https://images.earthcam.com/cams/singapore/marinabay.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "Downtown Waterfront",
        },
        {
            "id": "cam-cairo-giza",
            "name": "Cairo - Giza Plateau & Great Pyramids",
            "city": "Cairo, Egypt",
            "latitude": 29.9792,
            "longitude": 31.1342,
            "image_url": "https://images.earthcam.com/cams/cairo/pyramids.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "Plateau Horizon",
        },
        {
            "id": "cam-capetown-waterfront",
            "name": "Cape Town - V&A Waterfront & Table Mountain",
            "city": "Cape Town, South Africa",
            "latitude": -33.9045,
            "longitude": 18.4208,
            "image_url": "https://images.earthcam.com/cams/capetown/waterfront.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "Harbour Basin",
        },
        {
            "id": "cam-lasvegas-strip",
            "name": "Las Vegas - Bellagio Fountains & Strip",
            "city": "Las Vegas, USA",
            "latitude": 36.1126,
            "longitude": -115.1767,
            "image_url": "https://images.earthcam.com/cams/lasvegas/strip.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "Las Vegas Blvd",
        },
        {
            "id": "cam-toronto-dundas",
            "name": "Toronto - Yonge-Dundas Square",
            "city": "Toronto, Canada",
            "latitude": 43.6561,
            "longitude": -79.3802,
            "image_url": "https://images.earthcam.com/cams/toronto/dundas.jpg",
            "stream_url": "",
            "type": "live_cam",
            "direction": "Yonge St Corridor",
        },
    ]

    def __init__(self) -> None:
        self.cached_cameras: List[Dict[str, Any]] = list(self.GLOBAL_LANDMARK_CAMS)
        self.last_fetch: float = 0.0

    def fetch_live_cameras(self) -> List[Dict[str, Any]]:
        """Fetch cameras from TfL, Caltrans, Singapore LTA, and global landmarks."""
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
            with urllib.request.urlopen(req, timeout=5) as resp:
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
        except Exception as exc:
            logger.warning("TfL camera fetch failed: %s", exc)

        # 2. Singapore LTA DataMall Expressway Cameras
        try:
            req = urllib.request.Request(
                "https://api.data.gov.sg/v1/transport/traffic-images",
                headers={"User-Agent": CONFIG.HTTP_USER_AGENT},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                sg_data = json.loads(resp.read().decode("utf-8"))
                sg_items = sg_data.get("items", [])
                sg_cameras = sg_items[0].get("cameras", []) if sg_items else []

            for sc in sg_cameras:
                loc = sc.get("location", {})
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                img = sc.get("image", "")
                cam_id = sc.get("camera_id", "")
                if lat and lon and img:
                    cams.append({
                        "id": f"cam-sg-{cam_id}",
                        "name": f"Singapore Expressway Cam {cam_id}",
                        "city": "Singapore",
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "image_url": img,
                        "stream_url": "",
                        "type": "live_cam",
                        "direction": "Expressway Corridor",
                    })
        except Exception as exc:
            logger.warning("Singapore LTA camera fetch failed: %s", exc)

        # 3. Caltrans California Highway CCTV
        try:
            req = urllib.request.Request(
                CONFIG.CALTRANS_D04_URL,
                headers={"User-Agent": CONFIG.HTTP_USER_AGENT},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
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
        except Exception as exc:
            logger.warning("Caltrans camera fetch failed: %s", exc)

        self.cached_cameras = cams
        self.last_fetch = now
        logger.info("Total cameras aggregated: %d", len(self.cached_cameras))
        return self.cached_cameras

    def get_nearest_cameras(self, lat: float, lon: float, max_km: float = 120.0, limit: int = 6) -> List[Dict[str, Any]]:
        """Find the closest street cameras to a given latitude and longitude."""
        all_cams = self.cached_cameras if self.cached_cameras else self.GLOBAL_LANDMARK_CAMS
        results = []

        for cam in all_cams:
            clat = cam.get("latitude")
            clon = cam.get("longitude")
            if clat is None or clon is None:
                continue

            # Haversine distance
            dlat = math.radians(clat - lat)
            dlon = math.radians(clon - lon)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(clat)) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            dist_km = 6371.0 * c

            if dist_km <= max_km:
                cam_copy = dict(cam)
                cam_copy["distance_km"] = round(dist_km, 1)
                results.append(cam_copy)

        results.sort(key=lambda x: x["distance_km"])
        return results[:limit]

    def to_geojson(self) -> Dict[str, Any]:
        """Convert cameras to GeoJSON FeatureCollection."""
        cams = self.cached_cameras if self.cached_cameras else self.GLOBAL_LANDMARK_CAMS
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
