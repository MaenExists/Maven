"""
Automated Verification Test Suite for Maven Platform
Tests collectors, spatial algorithms, anomaly engine, and REST server.
"""

import json
import unittest
import urllib.request

from src.analysis.anomaly import AnomalyEngine
from src.analysis.change_detection import ChangeDetectionEngine
from src.analysis.geofence import GeofenceManager, is_point_in_polygon
from src.analysis.measurements import MeasurementEngine
from src.collectors.cameras import CameraCollector
from src.collectors.conflicts import ConflictCollector
from src.collectors.earthquakes import EarthquakeCollector
from src.collectors.flights import FlightCollector
from src.collectors.maritime import MaritimeCollector
from src.collectors.weather import WeatherCollector
from src.collectors.wildfires import WildfireCollector
from src.server.local_server import TacticalServer


class TestSpatialMath(unittest.TestCase):
    def test_point_in_polygon(self):
        # Square polygon: lon [0, 10], lat [0, 10]
        square = [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
        self.assertTrue(is_point_in_polygon(5.0, 5.0, square))
        self.assertFalse(is_point_in_polygon(15.0, 5.0, square))
        self.assertFalse(is_point_in_polygon(-1.0, 5.0, square))

    def test_haversine_distance(self):
        # London (51.5074, -0.1278) to Paris (48.8566, 2.3522) ≈ 344 km
        res = MeasurementEngine.haversine_distance(51.5074, -0.1278, 48.8566, 2.3522)
        self.assertGreater(res["distance_km"], 330)
        self.assertLess(res["distance_km"], 360)

    def test_bearing_calculation(self):
        # North bearing
        bearing = MeasurementEngine.calculate_bearing(0.0, 0.0, 10.0, 0.0)
        self.assertAlmostEqual(bearing, 0.0, delta=1.0)

    def test_polygon_area(self):
        # Approximate 1 degree by 1 degree area at equator ≈ 12,300 km^2
        poly = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]
        area = MeasurementEngine.polygon_area(poly)
        self.assertGreater(area["area_km2"], 10000)


class TestCollectorsAndEngines(unittest.TestCase):
    def test_collectors(self):
        flights = FlightCollector().fetch_live_flights()
        self.assertGreater(len(flights), 0)

        vessels = MaritimeCollector().fetch_live_vessels()
        self.assertGreater(len(vessels), 0)

        fires = WildfireCollector().fetch_live_wildfires()
        self.assertGreater(len(fires), 0)

        quakes = EarthquakeCollector().fetch_live_earthquakes()
        self.assertGreater(len(quakes), 0)

        cams = CameraCollector().fetch_live_cameras()
        self.assertGreater(len(cams), 0)

        conflicts = ConflictCollector().fetch_live_incidents()
        self.assertGreater(len(conflicts), 0)

    def test_anomaly_detection(self):
        engine = AnomalyEngine()
        # Simulated emergency squawk flight
        sim_flights = [{
            "id": "flight-test-01",
            "callsign": "MAYDAY01",
            "squawk": "7700",
            "longitude": 10.0,
            "latitude": 50.0,
            "altitude": 8000.0,
        }]
        anoms = engine.evaluate_telemetry(sim_flights, [], [], [])
        self.assertEqual(len(anoms), 1)
        self.assertEqual(anoms[0]["severity"], "CRITICAL")

    def test_change_detection(self):
        engine = ChangeDetectionEngine()
        res = engine.execute_diff("diff-port-singapore")
        self.assertEqual(res["preset_id"], "diff-port-singapore")
        self.assertGreater(res["detected_area_km2"], 0)


class TestLocalTacticalServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = TacticalServer(host="127.0.0.1", port=9876)
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_server_status_and_flights(self):
        url = "http://127.0.0.1:9876/api/status"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read().decode())
            self.assertEqual(data["status"], "OPERATIONAL")

        flights_url = "http://127.0.0.1:9876/api/flights"
        with urllib.request.urlopen(flights_url, timeout=5) as r:
            f_data = json.loads(r.read().decode())
            self.assertIn("data", f_data)
            self.assertGreater(f_data["count"], 0)

    def test_search_and_dossier_endpoints(self):
        search_url = "http://127.0.0.1:9876/api/search?q=Tokyo"
        with urllib.request.urlopen(search_url, timeout=10) as r:
            s_data = json.loads(r.read().decode())
            self.assertEqual(s_data["query"], "Tokyo")
            self.assertGreater(len(s_data["results"]), 0)
            self.assertIn("lat", s_data["results"][0])

        dossier_url = "http://127.0.0.1:9876/api/intel/dossier?lat=35.6762&lon=139.6503&name=Tokyo"
        with urllib.request.urlopen(dossier_url, timeout=10) as r:
            d_data = json.loads(r.read().decode())
            self.assertEqual(d_data["name"], "Tokyo")
            self.assertIn("summary", d_data)
            self.assertIn("cameras", d_data)
            self.assertIn("tactical_context", d_data)


if __name__ == "__main__":
    unittest.main()
