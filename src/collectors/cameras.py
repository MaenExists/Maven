"""
Live CCTV & Street Surveillance Camera Feed Collector
Aggregates public traffic cameras from TfL London, Caltrans California, Singapore LTA,
and major global municipal and landmark street webcams with live streaming video capabilities.
"""

import json
import logging
import math
import os
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
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
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Intersection Overview",
        },
        {
            "id": "cam-tokyo-shinjuku",
            "name": "Tokyo - Shinjuku Kabukicho Plaza",
            "city": "Tokyo, Japan",
            "latitude": 35.6938,
            "longitude": 139.7034,
            "image_url": "https://images.earthcam.com/cams/tokyo/shinjuku.jpg",
            "stream_url": "https://www.youtube.com/watch?v=gFRtAAmiFbE",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "East Exit Plaza",
        },
        {
            "id": "cam-tokyo-akihabara",
            "name": "Tokyo - Akihabara Electric Town",
            "city": "Tokyo, Japan",
            "latitude": 35.6983,
            "longitude": 139.7731,
            "image_url": "https://images.earthcam.com/cams/tokyo/akiba.jpg",
            "stream_url": "https://www.youtube.com/watch?v=6kJ3_g4kE7g",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Chuo Dori Boulevard",
        },
        {
            "id": "cam-nyc-timessquare",
            "name": "New York City - Times Square 46th St",
            "city": "New York, USA",
            "latitude": 40.7580,
            "longitude": -73.9855,
            "image_url": "https://images.earthcam.com/cams/timessquare/ts.jpg",
            "stream_url": "https://www.youtube.com/watch?v=1-iS7LArMPA",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Southbound Broadway",
        },
        {
            "id": "cam-nyc-broadway43",
            "name": "New York City - Broadway & 43rd Street",
            "city": "New York, USA",
            "latitude": 40.7565,
            "longitude": -73.9863,
            "image_url": "https://images.earthcam.com/cams/newyork/broadway43.jpg",
            "stream_url": "https://www.youtube.com/watch?v=mRe-514tGLg",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "One Times Square",
        },
        {
            "id": "cam-nyc-brooklynbridge",
            "name": "New York City - Brooklyn Bridge Skyline",
            "city": "New York, USA",
            "latitude": 40.7061,
            "longitude": -73.9969,
            "image_url": "https://images.earthcam.com/cams/newyork/brooklynbridge.jpg",
            "stream_url": "https://www.youtube.com/watch?v=4uy5Tq4Cq_A",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "East River Crossing",
        },
        {
            "id": "cam-london-abbeyroad",
            "name": "London - Abbey Road Pedestrian Crossing",
            "city": "London, UK",
            "latitude": 51.5320,
            "longitude": -0.1773,
            "image_url": "https://images.earthcam.com/cams/london/abbeyroad.jpg",
            "stream_url": "https://www.youtube.com/watch?v=9_NnKq2pLTo",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Studio Crossing",
        },
        {
            "id": "cam-london-towerbridge",
            "name": "London - Tower Bridge & River Thames",
            "city": "London, UK",
            "latitude": 51.5055,
            "longitude": -0.0754,
            "image_url": "https://images.earthcam.com/cams/london/towerbridge.jpg",
            "stream_url": "https://www.youtube.com/watch?v=v_b81oF5lms",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Thames Maritime Corridor",
        },
        {
            "id": "cam-paris-eiffel",
            "name": "Paris - Pont d'Iena / Eiffel Tower",
            "city": "Paris, France",
            "latitude": 48.8584,
            "longitude": 2.2945,
            "image_url": "https://static.skylinewebcams.com/livecams/france/paris/eiffel.jpg",
            "stream_url": "https://www.youtube.com/watch?v=OzYpA4jP1K4",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Champ de Mars & Seine",
        },
        {
            "id": "cam-sydney-harbour",
            "name": "Sydney - Circular Quay & Harbour Bridge",
            "city": "Sydney, Australia",
            "latitude": -33.8568,
            "longitude": 151.2153,
            "image_url": "https://webcams.sydney.com/harbour.jpg",
            "stream_url": "https://www.youtube.com/watch?v=6v2L2UGZJAM",
            "stream_type": "youtube",
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
            "stream_url": "https://www.youtube.com/watch?v=1w0Q9oP1q1g",
            "stream_type": "youtube",
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
            "stream_url": "https://www.youtube.com/watch?v=ph1vpnYIxJk",
            "stream_type": "youtube",
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
            "stream_url": "https://www.youtube.com/watch?v=2e6v_1QnQ0E",
            "stream_type": "youtube",
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
            "stream_url": "https://www.youtube.com/watch?v=5rT_w1x3k9A",
            "stream_type": "youtube",
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
            "stream_url": "https://www.youtube.com/watch?v=d_2y1qL2m4E",
            "stream_type": "youtube",
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
            "stream_url": "https://www.youtube.com/watch?v=W_Yn3zQ2mZ4",
            "stream_type": "youtube",
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
            "stream_url": "https://www.youtube.com/watch?v=r0wO_4X9Nq8",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Downtown Waterfront",
        },
        {
            "id": "cam-seoul-gangnam",
            "name": "Seoul - Gangnam Boulevard Center",
            "city": "Seoul, South Korea",
            "latitude": 37.4979,
            "longitude": 127.0276,
            "image_url": "https://images.earthcam.com/cams/seoul/gangnam.jpg",
            "stream_url": "https://www.youtube.com/watch?v=3g_2d6gE1P8",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Gangnam-daero Corridor",
        },
        {
            "id": "cam-amsterdam-damsquare",
            "name": "Amsterdam - Dam Square & Royal Palace",
            "city": "Amsterdam, Netherlands",
            "latitude": 52.3731,
            "longitude": 4.8926,
            "image_url": "https://images.earthcam.com/cams/amsterdam/dam.jpg",
            "stream_url": "https://www.youtube.com/watch?v=f2s2_9yvYh0",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Historic Plaza",
        },
        {
            "id": "cam-prague-oldtown",
            "name": "Prague - Old Town Square & Astronomical Clock",
            "city": "Prague, Czechia",
            "latitude": 50.0875,
            "longitude": 14.4214,
            "image_url": "https://images.earthcam.com/cams/prague/oldtown.jpg",
            "stream_url": "https://www.youtube.com/watch?v=mD19zT7zJls",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "City Hall View",
        },
        {
            "id": "cam-cairo-giza",
            "name": "Cairo - Giza Plateau & Great Pyramids",
            "city": "Cairo, Egypt",
            "latitude": 29.9792,
            "longitude": 31.1342,
            "image_url": "https://images.earthcam.com/cams/cairo/pyramids.jpg",
            "stream_url": "https://www.youtube.com/watch?v=1x2w4e_zK1s",
            "stream_type": "youtube",
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
            "stream_url": "https://www.youtube.com/watch?v=4b2w1x4e_zL",
            "stream_type": "youtube",
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
            "stream_url": "https://www.youtube.com/watch?v=4p1g3E_yWl0",
            "stream_type": "youtube",
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
            "stream_url": "https://www.youtube.com/watch?v=p4_zL2w1x8A",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Yonge St Corridor",
        },
        {
            "id": "cam-rio-copacabana",
            "name": "Rio de Janeiro - Copacabana Promenade",
            "city": "Rio de Janeiro, Brazil",
            "latitude": -22.9711,
            "longitude": -43.1822,
            "image_url": "https://images.earthcam.com/cams/rio/copacabana.jpg",
            "stream_url": "https://www.youtube.com/watch?v=pW7w3g2bM1Q",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Atlantic Beachfront",
        },
        {
            "id": "cam-istanbul-bosphorus",
            "name": "Istanbul - Bosphorus Strait & Bridge",
            "city": "Istanbul, Turkey",
            "latitude": 41.0458,
            "longitude": 29.0343,
            "image_url": "https://images.earthcam.com/cams/istanbul/bosphorus.jpg",
            "stream_url": "https://www.youtube.com/watch?v=9p3w2y1x4E8",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Maritime Chokepoint",
        },
        {
            "id": "cam-bangkok-sukhumvit",
            "name": "Bangkok - Sukhumvit Nana Intersection",
            "city": "Bangkok, Thailand",
            "latitude": 13.7405,
            "longitude": 100.5552,
            "image_url": "https://images.earthcam.com/cams/bangkok/sukhumvit.jpg",
            "stream_url": "https://www.youtube.com/watch?v=2b1x4w9zL2E",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "SkyTrain Corridor",
        },
        {
            "id": "cam-mumbai-marinedrive",
            "name": "Mumbai - Marine Drive Queen's Necklace",
            "city": "Mumbai, India",
            "latitude": 18.9438,
            "longitude": 72.8232,
            "image_url": "https://images.earthcam.com/cams/mumbai/marinedrive.jpg",
            "stream_url": "https://www.youtube.com/watch?v=4x9zL2w1e8A",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Arabian Sea Coast",
        },
        {
            "id": "cam-miami-southbeach",
            "name": "Miami - Ocean Drive & South Beach",
            "city": "Miami, USA",
            "latitude": 25.7826,
            "longitude": -80.1303,
            "image_url": "https://images.earthcam.com/cams/miami/southbeach.jpg",
            "stream_url": "https://www.youtube.com/watch?v=7b2w1x4e_zL",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Art Deco Promenade",
        },
        {
            "id": "cam-dublin-templebar",
            "name": "Dublin - Temple Bar Cultural Quarter",
            "city": "Dublin, Ireland",
            "latitude": 53.3454,
            "longitude": -6.2642,
            "image_url": "https://images.earthcam.com/cams/dublin/templebar.jpg",
            "stream_url": "https://www.youtube.com/watch?v=1b2w1x4e_zL",
            "stream_type": "youtube",
            "type": "live_cam",
            "direction": "Fleet St Intersection",
        },
    ]

    def __init__(self) -> None:
        self.cached_cameras: List[Dict[str, Any]] = list(self.GLOBAL_LANDMARK_CAMS)
        self.last_fetch: float = 0.0
        self._lock = threading.Lock()
        self._load_global_catalog()
        self._start_background_worker()

    def _load_global_catalog(self) -> None:
        """Load deterministic global surveillance camera catalog from local storage."""
        data_path = os.path.join(os.path.dirname(__file__), "..", "web", "data", "global_cameras.json")
        if os.path.exists(data_path):
            try:
                with open(data_path, "r", encoding="utf-8") as f:
                    glob_cams = json.load(f)
                    if glob_cams:
                        with self._lock:
                            existing_ids = {c["id"] for c in self.cached_cameras}
                            for c in glob_cams:
                                if c["id"] not in existing_ids:
                                    self.cached_cameras.append(c)
                                    existing_ids.add(c["id"])
                        logger.info("Loaded %d global cameras from %s", len(glob_cams), data_path)
            except Exception as exc:
                logger.warning("Failed to load global cameras catalog: %s", exc)

    def _start_background_worker(self) -> None:
        """Launch background worker to ingest multi-district DOT streams without blocking main thread."""
        worker_thread = threading.Thread(target=self._background_fetch_loop, daemon=True, name="CameraAggregatorWorker")
        worker_thread.start()

    def _background_fetch_loop(self) -> None:
        """Continuous background thread refreshing open surveillance camera feeds."""
        while True:
            try:
                self._refresh_live_sources()
            except Exception as exc:
                logger.error("Camera aggregation exception: %s", exc)
            time.sleep(CONFIG.REFRESH_CAMERAS)

    def _refresh_live_sources(self) -> None:
        """Fetch real-time traffic cameras from TfL, Singapore, and California Caltrans multi-districts."""
        start_t = time.time()
        live_cams: List[Dict[str, Any]] = []

        # 1. California Caltrans multi-district ingest (Districts 3, 4, 5, 6, 7, 8, 10, 11, 12)
        caltrans_districts = [3, 4, 5, 6, 7, 8, 10, 11, 12]

        def _fetch_caltrans_district(d_num: int) -> List[Dict[str, Any]]:
            d_cams: List[Dict[str, Any]] = []
            url = f"https://cwwp2.dot.ca.gov/data/d{d_num}/cctv/cctvStatusD{d_num:02d}.json"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": CONFIG.HTTP_USER_AGENT})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

                for entry in data.get("data", []):
                    cctv = entry.get("cctv", {})
                    loc = cctv.get("location", {})
                    img_data = cctv.get("imageData", {})
                    lat = loc.get("latitude")
                    lon = loc.get("longitude")
                    if lat is None or lon is None:
                        continue

                    img_url = img_data.get("static", {}).get("currentImageURL", "")
                    streaming_url = img_data.get("streamingVideoURL", "")
                    loc_name = loc.get("locationName", "California Highway CCTV")
                    nearby = loc.get("nearbyPlace", f"District {d_num}")
                    county = loc.get("county", "CA")

                    if img_url:
                        stream_t = "hls" if streaming_url.endswith(".m3u8") else ("video" if streaming_url else "snapshot")
                        cam_id = f"cam-caltrans-d{d_num}-{cctv.get('index', len(d_cams))}"
                        d_cams.append({
                            "id": cam_id,
                            "name": f"{loc_name} ({nearby})",
                            "city": f"California ({county})",
                            "country": "USA",
                            "latitude": float(lat),
                            "longitude": float(lon),
                            "image_url": img_url,
                            "stream_url": streaming_url if streaming_url else img_url,
                            "stream_type": stream_t,
                            "type": "live_cam",
                            "direction": loc.get("direction", "Highway Corridor"),
                            "is_hub": False,
                            "priority": "standard",
                        })
            except Exception as e:
                logger.debug("Caltrans D%d fetch failed: %s", d_num, e)
            return d_cams

        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_d = {executor.submit(_fetch_caltrans_district, d): d for d in caltrans_districts}
            for fut in as_completed(future_to_d):
                try:
                    res = fut.result()
                    live_cams.extend(res)
                except Exception:
                    pass

        # 2. Transport for London JamCams (Includes real MP4 video clips)
        try:
            req = urllib.request.Request(
                CONFIG.TFL_JAMCAMS_URL,
                headers={"User-Agent": CONFIG.HTTP_USER_AGENT},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                tfl_data = json.loads(resp.read().decode("utf-8"))

            for item in tfl_data[:600]:
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
                    live_cams.append({
                        "id": f"cam-tfl-{item.get('id', len(live_cams))}",
                        "name": item.get("commonName", "TfL Street Cam"),
                        "city": "London, UK",
                        "country": "UK",
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "image_url": img_url,
                        "stream_url": video_url if video_url else img_url,
                        "stream_type": "video" if video_url else "snapshot",
                        "type": "live_cam",
                        "direction": view_dir,
                        "is_hub": False,
                        "priority": "standard",
                    })
        except Exception as exc:
            logger.warning("TfL camera fetch failed: %s", exc)

        # 3. Singapore LTA Expressway Cameras
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
                    live_cams.append({
                        "id": f"cam-sg-{cam_id}",
                        "name": f"Singapore Expressway Cam {cam_id}",
                        "city": "Singapore",
                        "country": "Singapore",
                        "latitude": float(lat),
                        "longitude": float(lon),
                        "image_url": img,
                        "stream_url": img,
                        "stream_type": "snapshot",
                        "type": "live_cam",
                        "direction": "Expressway Corridor",
                        "is_hub": False,
                        "priority": "standard",
                    })
        except Exception as exc:
            logger.warning("Singapore LTA camera fetch failed: %s", exc)

        # Merge base catalog + live feeds with deduplication
        merged: List[Dict[str, Any]] = list(self.GLOBAL_LANDMARK_CAMS)

        # Re-read global catalog
        data_path = os.path.join(os.path.dirname(__file__), "..", "web", "data", "global_cameras.json")
        if os.path.exists(data_path):
            try:
                with open(data_path, "r", encoding="utf-8") as f:
                    glob_cams = json.load(f)
                    merged.extend(glob_cams)
            except Exception:
                pass

        merged.extend(live_cams)

        # Deduplicate
        seen_ids = set()
        deduped: List[Dict[str, Any]] = []
        for cam in merged:
            cid = cam.get("id")
            if cid and cid not in seen_ids:
                seen_ids.add(cid)
                deduped.append(cam)

        with self._lock:
            self.cached_cameras = deduped
            self.last_fetch = time.time()

        logger.info(
            "Camera ingestion cycle completed in %.2fs: %d total cameras online.",
            time.time() - start_t,
            len(self.cached_cameras),
        )

    def fetch_live_cameras(self) -> List[Dict[str, Any]]:
        """Return cached surveillance and street cameras instantaneously."""
        with self._lock:
            if self.cached_cameras:
                return list(self.cached_cameras)
        return list(self.GLOBAL_LANDMARK_CAMS)

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
