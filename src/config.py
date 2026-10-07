"""
Maven Platform Configuration
Defines endpoints, cache timeouts, default settings, and system constants.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Config:
    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8765
    DEBUG: bool = False

    # OSINT Endpoints
    OPENSKY_URL: str = "https://opensky-network.org/api/states/all"
    USGS_EARTHQUAKES_URL: str = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    NASA_FIRMS_URL: str = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_24h.csv"
    TFL_JAMCAMS_URL: str = "https://api.tfl.gov.uk/Place/Type/JamCam"
    CALTRANS_D04_URL: str = "https://cwwp2.dot.ca.gov/data/d4/cctv/cctvStatusD04.json"
    OPEN_METEO_URL: str = "https://api.open-meteo.com/v1/forecast"
    
    # NASA GIBS Tile Endpoint for Sentinel-2 / MODIS Satellite Imagery
    NASA_GIBS_WMTS_URL: str = "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{Time}/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg"

    # Refresh Intervals (seconds)
    REFRESH_FLIGHTS: int = 15
    REFRESH_VESSELS: int = 20
    REFRESH_WILDFIRES: int = 300
    REFRESH_EARTHQUAKES: int = 60
    REFRESH_CAMERAS: int = 120
    REFRESH_WEATHER: int = 180

    # Cache Limits
    MAX_FLIGHT_ENTITIES: int = 1200
    MAX_VESSEL_ENTITIES: int = 800
    MAX_FIRE_ENTITIES: int = 1000
    MAX_QUAKE_ENTITIES: int = 500
    MAX_CAMERA_ENTITIES: int = 1500

    # User Agent
    HTTP_USER_AGENT: str = "Maven-Geospatial-Intelligence/1.0"


CONFIG = Config()
