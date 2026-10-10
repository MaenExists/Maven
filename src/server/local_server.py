"""
Local Tactical Content & REST API Server
Serves the CesiumJS 3D tactical globe web application, streams live OSINT telemetry,
and proxies live surveillance feeds with CORS headers.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import mimetypes
import os
import threading
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional

from src.analysis.anomaly import AnomalyEngine
from src.analysis.change_detection import ChangeDetectionEngine
from src.analysis.geofence import GeofenceManager
from src.analysis.measurements import MeasurementEngine
from src.collectors.cameras import CameraCollector
from src.collectors.conflicts import ConflictCollector
from src.collectors.earthquakes import EarthquakeCollector
from src.collectors.flights import FlightCollector
from src.collectors.maritime import MaritimeCollector
from src.collectors.weather import WeatherCollector
from src.collectors.wildfires import WildfireCollector
from src.config import CONFIG

logger = logging.getLogger(__name__)


class TacticalAPIHandler(SimpleHTTPRequestHandler):
    """Handles REST API queries and serves tactical web frontend assets."""

    server_instance: "TacticalServer"

    def __init__(self, *args, **kwargs):
        # Base web directory
        web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
        super().__init__(*args, directory=web_dir, **kwargs)

    def end_headers(self) -> None:
        """Inject CORS headers to allow WebGL and QWebEngine access."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.end_headers()

    def do_GET(self) -> None:
        """Process API endpoints or forward to static asset handler."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith("/api/"):
            self._handle_api_get(path, query)
        else:
            # Fallback to index.html for root path
            if path == "/" or path == "":
                self.path = "/index.html"
            super().do_GET()

    def do_POST(self) -> None:
        """Process JSON API post actions."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        self._handle_api_post(path, payload)

    def _send_json(self, data: Any, status: int = 200) -> None:
        """Utility to serialize and send JSON response."""
        encoded = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _handle_api_get(self, path: str, query: Dict[str, Any]) -> None:
        srv = self.server_instance

        if path == "/api/status":
            self._send_json({
                "status": "OPERATIONAL",
                "system": "MAVEN GEOSPATIAL INTELLIGENCE",
                "threat_level": "ELEVATED",
                "timestamp": int(os.times()[4]),
            })

        elif path == "/api/flights":
            self._send_json({
                "count": len(srv.flights),
                "data": srv.flights,
                "geojson": srv._to_geojson(srv.flights),
            })

        elif path == "/api/vessels":
            self._send_json({
                "count": len(srv.vessels),
                "data": srv.vessels,
                "geojson": srv._to_geojson(srv.vessels),
            })

        elif path == "/api/wildfires":
            self._send_json({
                "count": len(srv.wildfires),
                "data": srv.wildfires,
                "geojson": srv._to_geojson(srv.wildfires),
            })

        elif path == "/api/earthquakes":
            self._send_json({
                "count": len(srv.earthquakes),
                "data": srv.earthquakes,
                "geojson": srv._to_geojson(srv.earthquakes),
            })

        elif path == "/api/cameras":
            self._send_json({
                "count": len(srv.cameras),
                "data": srv.cameras,
                "geojson": srv._to_geojson(srv.cameras),
            })

        elif path == "/api/conflicts":
            self._send_json({
                "count": len(srv.conflicts),
                "data": srv.conflicts,
                "geojson": srv._to_geojson(srv.conflicts),
            })

        elif path == "/api/weather":
            self._send_json({
                "count": len(srv.weather_grid),
                "data": srv.weather_grid,
            })

        elif path == "/api/weather/point":
            lat = float(query.get("lat", [0.0])[0])
            lon = float(query.get("lon", [0.0])[0])
            report = srv.weather_collector.fetch_weather_for_point(lat, lon)
            self._send_json(report)

        elif path == "/api/geofences":
            self._send_json(srv.geofence_mgr.list_zones())

        elif path == "/api/anomalies":
            self._send_json({
                "count": len(srv.anomalies),
                "data": srv.anomalies,
            })

        elif path == "/api/change-detection/presets":
            self._send_json(srv.change_engine.list_presets())

        elif path == "/api/measure/distance":
            lat1 = float(query.get("lat1", [0.0])[0])
            lon1 = float(query.get("lon1", [0.0])[0])
            lat2 = float(query.get("lat2", [0.0])[0])
            lon2 = float(query.get("lon2", [0.0])[0])
            dist = MeasurementEngine.haversine_distance(lat1, lon1, lat2, lon2)
            bearing = MeasurementEngine.calculate_bearing(lat1, lon1, lat2, lon2)
            dist["bearing_deg"] = bearing
            self._send_json(dist)

        elif path == "/api/search":
            q = query.get("q", [""])[0].strip()
            if not q:
                self._send_json({"query": "", "results": []})
                return
            results = srv.search_places(q)
            self._send_json({"query": q, "results": results})

        elif path == "/api/intel/dossier":
            lat = float(query.get("lat", [0.0])[0])
            lon = float(query.get("lon", [0.0])[0])
            name = query.get("name", [""])[0].strip()
            dossier = srv.get_place_dossier(lat, lon, name)
            self._send_json(dossier)

        elif path == "/api/cameras/nearest":
            lat = float(query.get("lat", [0.0])[0])
            lon = float(query.get("lon", [0.0])[0])
            limit = int(query.get("limit", [6])[0])
            max_km = float(query.get("max_km", [150.0])[0])
            cams = srv.camera_collector.get_nearest_cameras(lat, lon, max_km=max_km, limit=limit)
            self._send_json({"count": len(cams), "cameras": cams})

        elif path == "/api/proxy/image":
            # Proxy external camera images to avoid CORS restriction in WebGL / Canvas
            target_url = query.get("url", [""])[0]
            if not target_url:
                self.send_error(400, "Missing image url parameter")
                return
            try:
                req = urllib.request.Request(target_url, headers={"User-Agent": CONFIG.HTTP_USER_AGENT})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = resp.read()
                    content_type = resp.headers.get("Content-Type", "image/jpeg")

                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_error(502, f"Proxy failed: {e}")

        else:
            self.send_error(404, "Endpoint not found")

    def _handle_api_post(self, path: str, payload: Dict[str, Any]) -> None:
        srv = self.server_instance

        if path == "/api/geofences":
            zone_id = payload.get("id", f"zone-{int(os.times()[4])}")
            name = payload.get("name", "Custom Restricted Area")
            polygon = payload.get("polygon", [])
            alert_types = payload.get("alert_types", ["flight", "vessel"])
            desc = payload.get("description", "")
            color = payload.get("color", "#ff0055")
            zone = srv.geofence_mgr.add_zone(zone_id, name, polygon, alert_types, desc, color)
            self._send_json(zone, status=201)

        elif path == "/api/change-detection/execute":
            preset_id = payload.get("preset_id", "")
            thresh = float(payload.get("threshold", 0.25))
            result = srv.change_engine.execute_diff(preset_id, thresh)
            self._send_json(result)

        elif path == "/api/measure/area":
            coords = payload.get("coordinates", [])
            area_result = MeasurementEngine.polygon_area(coords)
            self._send_json(area_result)

        else:
            self.send_error(404, "Endpoint not found")


class TacticalServer:
    """Manages HTTP daemon and background OSINT collectors."""

    def __init__(self, host: str = CONFIG.HOST, port: int = CONFIG.PORT) -> None:
        self.host = host
        self.port = port
        self.httpd: Optional[ThreadingHTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.poll_thread: Optional[threading.Thread] = None
        self.running: bool = False

        # Collectors
        self.flight_collector = FlightCollector()
        self.maritime_collector = MaritimeCollector()
        self.wildfire_collector = WildfireCollector()
        self.earthquake_collector = EarthquakeCollector()
        self.camera_collector = CameraCollector()
        self.conflict_collector = ConflictCollector()
        self.weather_collector = WeatherCollector()

        # Engines
        self.geofence_mgr = GeofenceManager()
        self.change_engine = ChangeDetectionEngine()
        self.anomaly_engine = AnomalyEngine()

        # Telemetry Cache
        self.flights = []
        self.vessels = []
        self.wildfires = []
        self.earthquakes = []
        self.cameras = []
        self.conflicts = []
        self.weather_grid = []
        self.anomalies = []

        # Search and Intelligence Dossier Cache
        self.search_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.dossier_cache: Dict[str, Dict[str, Any]] = {}

    STRATEGIC_PRESETS = [
        {"name": "Tokyo", "display_name": "Tokyo, Japan", "lat": 35.6762, "lon": 139.6503, "type": "capital", "country": "Japan"},
        {"name": "London", "display_name": "London, Greater London, United Kingdom", "lat": 51.5074, "lon": -0.1278, "type": "capital", "country": "United Kingdom"},
        {"name": "New York", "display_name": "New York City, New York, United States", "lat": 40.7128, "lon": -74.0060, "type": "megacity", "country": "United States"},
        {"name": "Singapore", "display_name": "Singapore (Port & Strait of Malacca Hub)", "lat": 1.290270, "lon": 103.851959, "type": "strategic_hub", "country": "Singapore"},
        {"name": "Suez Canal", "display_name": "Suez Canal (Great Bitter Lake / Ismailia), Egypt", "lat": 30.7050, "lon": 32.3442, "type": "chokepoint", "country": "Egypt"},
        {"name": "Strait of Hormuz", "display_name": "Strait of Hormuz (Bandar Abbas / Musandam)", "lat": 26.5667, "lon": 56.2500, "type": "chokepoint", "country": "Oman / Iran"},
        {"name": "Strait of Malacca", "display_name": "Strait of Malacca (One Fathom Bank)", "lat": 2.5000, "lon": 101.5000, "type": "chokepoint", "country": "Malaysia / Indonesia"},
        {"name": "Strait of Gibraltar", "display_name": "Strait of Gibraltar (Pillars of Hercules)", "lat": 35.9600, "lon": -5.5000, "type": "chokepoint", "country": "Spain / Morocco"},
        {"name": "Panama Canal", "display_name": "Panama Canal (Miraflores & Cocoli Locks)", "lat": 9.0800, "lon": -79.6800, "type": "chokepoint", "country": "Panama"},
        {"name": "Washington D.C.", "display_name": "Washington, District of Columbia, United States", "lat": 38.8951, "lon": -77.0364, "type": "capital", "country": "United States"},
        {"name": "Paris", "display_name": "Paris, Île-de-France, France", "lat": 48.8566, "lon": 2.3522, "type": "capital", "country": "France"},
        {"name": "Berlin", "display_name": "Berlin, Germany", "lat": 52.5200, "lon": 13.4050, "type": "capital", "country": "Germany"},
        {"name": "Taipei", "display_name": "Taipei, Taiwan", "lat": 25.0330, "lon": 121.5654, "type": "city", "country": "Taiwan"},
        {"name": "Seoul", "display_name": "Seoul, South Korea", "lat": 37.5665, "lon": 126.9780, "type": "capital", "country": "South Korea"},
        {"name": "Kyiv", "display_name": "Kyiv, Ukraine", "lat": 50.4501, "lon": 30.5234, "type": "capital", "country": "Ukraine"},
        {"name": "Dubai", "display_name": "Dubai, United Arab Emirates", "lat": 25.2048, "lon": 55.2708, "type": "city", "country": "United Arab Emirates"},
        {"name": "Beijing", "display_name": "Beijing, China", "lat": 39.9042, "lon": 116.4074, "type": "capital", "country": "China"},
        {"name": "Sydney", "display_name": "Sydney, New South Wales, Australia", "lat": -33.8688, "lon": 151.2093, "type": "city", "country": "Australia"},
        {"name": "San Francisco", "display_name": "San Francisco, California, United States", "lat": 37.7749, "lon": -122.4194, "type": "city", "country": "United States"},
        {"name": "Cairo", "display_name": "Cairo, Egypt", "lat": 30.0444, "lon": 31.2357, "type": "capital", "country": "Egypt"},
        {"name": "Moscow", "display_name": "Moscow, Russian Federation", "lat": 55.7558, "lon": 37.6173, "type": "capital", "country": "Russia"},
        {"name": "Rome", "display_name": "Rome, Lazio, Italy", "lat": 41.9028, "lon": 12.4964, "type": "capital", "country": "Italy"},
        {"name": "New Delhi", "display_name": "New Delhi, Delhi, India", "lat": 28.6139, "lon": 77.2090, "type": "capital", "country": "India"},
        {"name": "Bab-el-Mandeb", "display_name": "Bab-el-Mandeb Strait, Red Sea Entry", "lat": 12.5833, "lon": 43.3333, "type": "chokepoint", "country": "Djibouti / Yemen"},
        {"name": "Bosphorus Strait", "display_name": "Bosphorus Strait, Istanbul, Turkey", "lat": 41.1172, "lon": 29.0719, "type": "chokepoint", "country": "Turkey"},
    ]

    def start(self) -> None:
        """Start the server daemon and collector loops."""
        if self.running:
            return

        TacticalAPIHandler.server_instance = self
        ThreadingHTTPServer.allow_reuse_address = True
        self.httpd = ThreadingHTTPServer((self.host, self.port), TacticalAPIHandler)
        self.running = True

        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        logger.info("Tactical server listening at http://%s:%d", self.host, self.port)

        # Pre-seed initial telemetry so server responds in < 2ms immediately
        self.flights = self.flight_collector._generate_tactical_fleet()
        self.vessels = self.maritime_collector.cached_vessels
        self.wildfires = self.wildfire_collector._generate_fallback_wildfires()
        self.earthquakes = self.earthquake_collector._generate_fallback_earthquakes()
        self.cameras = list(self.camera_collector.GLOBAL_LANDMARK_CAMS)
        self.conflicts = self.conflict_collector.fetch_live_incidents()
        self.weather_grid = [
            {"name": h["name"], "latitude": h["lat"], "longitude": h["lon"], "temperature_c": 20.0, "wind_speed_kmh": 15.0, "wind_direction_deg": 180.0}
            for h in self.weather_collector.HUBS
        ]

        # Start live background polling thread
        self.poll_thread = threading.Thread(target=self._background_poll_loop, daemon=True)
        self.poll_thread.start()

    def stop(self) -> None:
        """Stop server daemon."""
        self.running = False
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        logger.info("Tactical server stopped")

    def refresh_all_telemetry(self) -> None:
        """Poll all active data sources and evaluate threat heuristics."""
        try:
            self.flights = self.flight_collector.fetch_live_flights()
            self.vessels = self.maritime_collector.fetch_live_vessels()
            self.wildfires = self.wildfire_collector.fetch_live_wildfires()
            self.earthquakes = self.earthquake_collector.fetch_live_earthquakes()
            self.cameras = self.camera_collector.fetch_live_cameras()
            self.conflicts = self.conflict_collector.fetch_live_incidents()
            self.weather_grid = self.weather_collector.fetch_global_weather_grid()

            # Evaluate geofence breaches
            all_entities = self.flights + self.vessels
            self.geofence_mgr.evaluate_entities(all_entities)

            # Evaluate anomalies
            self.anomalies = self.anomaly_engine.evaluate_telemetry(
                self.flights, self.vessels, self.wildfires, self.earthquakes
            )
        except Exception as exc:
            logger.error("Error refreshing telemetry: %s", exc)

    def _to_geojson(self, items: list) -> dict:
        """Fast in-memory GeoJSON conversion."""
        features = []
        for item in items:
            lon = item.get("longitude", 0.0)
            lat = item.get("latitude", 0.0)
            alt = item.get("altitude", 0.0)
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon, lat, alt]},
                "properties": item,
            })
        return {"type": "FeatureCollection", "features": features}

    def _background_poll_loop(self) -> None:
        """Periodic background refresh loop."""
        import time
        while self.running:
            time.sleep(15)
            self.refresh_all_telemetry()

    def search_places(self, query_str: str) -> List[Dict[str, Any]]:
        """Search places via strategic preset index and OSM Nominatim geocoder."""
        q_norm = query_str.lower().strip()
        if not q_norm:
            return []

        if q_norm in self.search_cache:
            return self.search_cache[q_norm]

        matches: List[Dict[str, Any]] = []

        # 1. Match against strategic presets first (instant, guaranteed zero latency)
        for p in self.STRATEGIC_PRESETS:
            if q_norm in p["name"].lower() or q_norm in p["display_name"].lower():
                matches.append({
                    "name": p["name"],
                    "display_name": p["display_name"],
                    "lat": p["lat"],
                    "lon": p["lon"],
                    "type": p.get("type", "place"),
                    "category": p.get("country", "STRATEGIC SECTOR"),
                })

        # 2. Query OSM Nominatim if query is at least 2 chars and not already matched
        if len(query_str) >= 2 and len(matches) < 4:
            try:
                encoded = urllib.parse.quote(query_str)
                url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&addressdetails=1&limit=6"
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": CONFIG.HTTP_USER_AGENT},
                )
                with urllib.request.urlopen(req, timeout=2.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))

                for item in data:
                    lat = float(item["lat"])
                    lon = float(item["lon"])
                    display_name = item.get("display_name", "")
                    name = item.get("name") or display_name.split(",")[0].strip()
                    cat = item.get("class", "place")
                    ptype = item.get("type", "location")

                    if not any(abs(m["lat"] - lat) < 0.01 and abs(m["lon"] - lon) < 0.01 for m in matches):
                        matches.append({
                            "name": name,
                            "display_name": display_name,
                            "lat": lat,
                            "lon": lon,
                            "type": ptype,
                            "category": cat.upper(),
                        })
            except Exception as exc:
                logger.warning("Nominatim geocoding lookup failed: %s", exc)

        results = matches[:8]
        self.search_cache[q_norm] = results
        return results

    def get_place_dossier(self, lat: float, lon: float, name: str = "") -> Dict[str, Any]:
        """Compile a Palantir-grade intelligence dossier for a target planetary location."""
        cache_key = f"{round(lat, 3)}:{round(lon, 3)}:{name.lower()}"
        if cache_key in self.dossier_cache:
            return self.dossier_cache[cache_key]

        # 1. Wikipedia Summary
        wiki_title = name.split(",")[0].strip() if name else f"Sector {lat:.2f}, {lon:.2f}"
        wiki_data = {
            "description": "Geographical target sector",
            "extract": f"Planetary coordinates lat {lat:.4f}, lon {lon:.4f}. Tactical reconnaissance active.",
            "thumbnail": ""
        }

        if wiki_title:
            try:
                encoded_title = urllib.parse.quote(wiki_title)
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"
                req = urllib.request.Request(url, headers={"User-Agent": CONFIG.HTTP_USER_AGENT})
                with urllib.request.urlopen(req, timeout=2.5) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    wiki_data["description"] = resp_data.get("description", "Sector location")
                    wiki_data["extract"] = resp_data.get("extract", wiki_data["extract"])
                    thumb = resp_data.get("thumbnail", {}).get("source", "")
                    if thumb:
                        wiki_data["thumbnail"] = thumb
            except Exception as exc:
                logger.debug("Wikipedia dossier fetch failed for '%s': %s", wiki_title, exc)

        # 2. Pinpoint Atmospheric Weather
        weather = self.weather_collector.fetch_weather_for_point(lat, lon)

        # 3. Nearest Street / Traffic / Landmark Surveillance Cameras
        nearest_cams = self.camera_collector.get_nearest_cameras(lat, lon, max_km=150.0, limit=6)
        if not nearest_cams:
            nearest_cams = self.camera_collector.get_nearest_cameras(lat, lon, max_km=25000.0, limit=1)

        # 4. Tactical Airspace & Maritime Presence
        flights_in_sector = 0
        for f in self.flights:
            flat = f.get("latitude")
            flon = f.get("longitude")
            if flat is not None and flon is not None:
                d = MeasurementEngine.haversine_distance(lat, lon, flat, flon)["distance_km"]
                if d <= 300.0:
                    flights_in_sector += 1

        vessels_in_sector = 0
        for v in self.vessels:
            vlat = v.get("latitude")
            vlon = v.get("longitude")
            if vlat is not None and vlon is not None:
                d = MeasurementEngine.haversine_distance(lat, lon, vlat, vlon)["distance_km"]
                if d <= 250.0:
                    vessels_in_sector += 1

        # Nearest seismic anomaly within 600 km
        nearest_quake = None
        min_quake_dist = 600.0
        for q in self.earthquakes:
            qlat = q.get("latitude")
            qlon = q.get("longitude")
            if qlat is not None and qlon is not None:
                d = MeasurementEngine.haversine_distance(lat, lon, qlat, qlon)["distance_km"]
                if d < min_quake_dist:
                    min_quake_dist = d
                    nearest_quake = {
                        "magnitude": q.get("magnitude", 0),
                        "place": q.get("place", "Seismic Event"),
                        "distance_km": round(d, 1)
                    }

        # Active fires within 300 km
        fires_count = 0
        for w in self.wildfires:
            wlat = w.get("latitude")
            wlon = w.get("longitude")
            if wlat is not None and wlon is not None:
                d = MeasurementEngine.haversine_distance(lat, lon, wlat, wlon)["distance_km"]
                if d <= 300.0:
                    fires_count += 1

        dossier = {
            "name": name or wiki_title,
            "latitude": lat,
            "longitude": lon,
            "description": wiki_data["description"],
            "summary": wiki_data["extract"],
            "thumbnail_url": wiki_data["thumbnail"],
            "weather": weather,
            "cameras": nearest_cams,
            "tactical_context": {
                "flights_in_sector": flights_in_sector,
                "vessels_in_sector": vessels_in_sector,
                "nearby_fires": fires_count,
                "seismic_hazard": nearest_quake,
            }
        }

        self.dossier_cache[cache_key] = dossier
        return dossier
