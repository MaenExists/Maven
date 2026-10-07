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
