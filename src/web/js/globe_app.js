/**
 * MAVEN 3D Tactical Globe Engine
 * Core CesiumJS initialization, camera momentum, 3D tiles, lighting, and OSINT synchronization.
 */

class MavenGlobeApp {
    constructor() {
        this.viewer = null;
        this.layers = null;
        this.geofenceDrawer = null;
        this.measureTool = null;
        this.changeViewer = null;
        this.weatherLayer = null;
        this.osmBuildings = null;
        this.sunLightingEnabled = true;
        this.buildingsEnabled = true;

        this.init();
    }

    async init() {
        // High contrast dark basemap (CartoDB Dark Matter)
        const darkImageryProvider = new Cesium.UrlTemplateImageryProvider({
            url: 'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
            subdomains: ['a', 'b', 'c', 'd'],
            maximumLevel: 19,
            credit: 'CartoDB Dark Matter / OpenStreetMap'
        });

        // Initialize Cesium Viewer
        this.viewer = new Cesium.Viewer('cesiumContainer', {
            imageryProvider: darkImageryProvider,
            baseLayerPicker: false,
            geocoder: false,
            homeButton: false,
            infoBox: false,
            sceneModePicker: false,
            selectionIndicator: false,
            navigationHelpButton: false,
            animation: false,
            timeline: false,
            fullscreenButton: false,
            vrButton: false,
            shadows: false,
            terrainShadows: Cesium.ShadowMode.DISABLED,
            contextOptions: {
                webgl: {
                    alpha: true,
                    antialias: true,
                    preserveDrawingBuffer: true
                }
            }
        });

        // Atmospheric and lighting configuration
        const scene = this.viewer.scene;
        const globe = scene.globe;

        globe.baseColor = Cesium.Color.fromCssColorString('#06090e');
        globe.enableLighting = this.sunLightingEnabled;
        globe.atmosphereLightIntensity = 8.0;
        globe.nightColor = Cesium.Color.fromCssColorString('#020408');
        scene.skyAtmosphere.show = true;
        scene.skyAtmosphere.brightnessShift = -0.15;
        scene.skyAtmosphere.saturationShift = -0.3;
        scene.backgroundColor = Cesium.Color.fromCssColorString('#030712');

        // Configure camera inertia for catch, drag, and flick momentum
        const controller = scene.screenSpaceCameraController;
        controller.inertiaSpin = 0.88;
        controller.inertiaTranslate = 0.88;
        controller.inertiaZoom = 0.85;
        controller.bounceAnimationTime = 0.2;
        controller.minimumZoomDistance = 50.0;
        controller.maximumZoomDistance = 45000000.0;

        // Load 3D Buildings (Cesium OSM Buildings) if token/network allows, with graceful fallback
        try {
            if (typeof Cesium.createOsmBuildingsAsync === 'function') {
                const buildingsTileset = await Cesium.createOsmBuildingsAsync();
                this.osmBuildings = buildingsTileset;
                this.osmBuildings.style = new Cesium.Cesium3DTileStyle({
                    color: {
                        conditions: [
                            ['true', 'color("#0f172a", 0.95)']
                        ]
                    }
                });
                scene.primitives.add(this.osmBuildings);
                console.log('OSM 3D Buildings streaming active');
            }
        } catch (e) {
            console.log('OSM 3D Buildings fallback to 2D footprint vectors:', e.message);
        }

        // Initialize modules
        this.layers = new TacticalLayersManager(this.viewer);
        this.geofenceDrawer = new GeofenceDrawer(this.viewer);
        this.measureTool = new MeasurementTool(this.viewer);
        this.changeViewer = new SatelliteChangeViewer(this.viewer);
        this.weatherLayer = new WeatherSimulationLayer(this.viewer);

        // Bind camera telemetry readout
        this._bindTelemetryReadout();

        // Initial vantage point (orbital view)
        this.viewer.camera.setView({
            destination: Cesium.Cartesian3.fromDegrees(15.0, 25.0, 22000000.0),
            orientation: {
                heading: Cesium.Math.toRadians(0),
                pitch: Cesium.Math.toRadians(-90),
                roll: 0.0
            }
        });

        // Start data polling loops
        this.startDataPolling();
        this.loadInitialGeofences();

        // Setup QWebChannel if present
        this._initQtWebChannel();
    }

    _bindTelemetryReadout() {
        const coordsElem = document.getElementById('hudCoords');
        const altElem = document.getElementById('hudAlt');
        const headingElem = document.getElementById('hudHeading');

        const updateReadout = () => {
            const cam = this.viewer.camera;
            const carto = cam.positionCartographic;
            const lon = Cesium.Math.toDegrees(carto.longitude).toFixed(4);
            const lat = Cesium.Math.toDegrees(carto.latitude).toFixed(4);
            const heightKm = (carto.height / 1000).toFixed(0);
            const heading = Cesium.Math.toDegrees(cam.heading).toFixed(0);

            if (coordsElem) coordsElem.textContent = `${lat}° N, ${lon}° E`;
            if (altElem) altElem.textContent = `${heightKm} KM`;
            if (headingElem) headingElem.textContent = `${heading}°`;
        };

        this.viewer.camera.changed.addEventListener(updateReadout);
        this.viewer.camera.moveEnd.addEventListener(updateReadout);
    }

    _initQtWebChannel() {
        if (typeof QWebChannel !== 'undefined') {
            new QWebChannel(qt.webChannelTransport, (channel) => {
                window.mavenBridge = channel.objects.mavenBridge;
                console.log('Qt WebChannel connected to Python bridge');

                // Listen for bridge signals
                if (window.mavenBridge.cameraFocusRequested) {
                    window.mavenBridge.cameraFocusRequested.connect((lon, lat, height) => {
                        this.flyTo(lon, lat, height);
                    });
                }
                if (window.mavenBridge.layerToggled) {
                    window.mavenBridge.layerToggled.connect((layerId, state) => {
                        this.layers.toggleLayer(layerId, state);
                    });
                }
                if (window.mavenBridge.changeDetectionTriggered) {
                    window.mavenBridge.changeDetectionTriggered.connect((presetId) => {
                        this.changeViewer.loadPreset(presetId);
                    });
                }
                if (window.mavenBridge.measureModeActivated) {
                    window.mavenBridge.measureModeActivated.connect((mode) => {
                        this.measureTool.setMode(mode);
                    });
                }
            });
        }
    }

    async startDataPolling() {
        const fetchAll = async () => {
            try {
                const [flightsRes, vesselsRes, firesRes, quakesRes, camsRes, confRes, weatherRes, anomRes] = await Promise.all([
                    fetch('/api/flights').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/vessels').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/wildfires').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/earthquakes').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/cameras').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/conflicts').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/weather').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/anomalies').then(r => r.json()).catch(() => ({ data: [] })),
                ]);

                if (flightsRes.data) this.layers.updateFlights(flightsRes.data);
                if (vesselsRes.data) this.layers.updateVessels(vesselsRes.data);
                if (firesRes.data) this.layers.updateWildfires(firesRes.data);
                if (quakesRes.data) this.layers.updateEarthquakes(quakesRes.data);
                if (camsRes.data) this.layers.updateCameras(camsRes.data);
                if (confRes.data) this.layers.updateConflicts(confRes.data);
                if (weatherRes.data) this.weatherLayer.updateWeatherGrid(weatherRes.data);
                if (anomRes.data) this.layers.updateAnomalies(anomRes.data);

                // Update HUD live counters
                this._updateCounters({
                    flights: flightsRes.count || 0,
                    vessels: vesselsRes.count || 0,
                    fires: firesRes.count || 0,
                    quakes: quakesRes.count || 0,
                    cameras: camsRes.count || 0,
                    anomalies: anomRes.count || 0
                });
            } catch (e) {
                console.warn('Telemetry polling error:', e);
            }
        };

        // Initial fetch then cycle every 10 seconds
        await fetchAll();
        setInterval(fetchAll, 10000);
    }

    _updateCounters(counts) {
        const updateElem = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };
        updateElem('countFlights', counts.flights);
        updateElem('countVessels', counts.vessels);
        updateElem('countFires', counts.fires);
        updateElem('countQuakes', counts.quakes);
        updateElem('countCams', counts.cameras);
        updateElem('countAnomalies', counts.anomalies);
    }

    async loadInitialGeofences() {
        try {
            const resp = await fetch('/api/geofences');
            const zones = await resp.json();
            this.geofenceDrawer.loadInitialZones(zones);
        } catch (e) {}
    }

    flyTo(lon, lat, height = 150000.0) {
        window.tacticalSound.playClick();
        this.viewer.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(lon, lat, height),
            duration: 2.0
        });
    }

    toggleSunLighting() {
        this.sunLightingEnabled = !this.sunLightingEnabled;
        this.viewer.scene.globe.enableLighting = this.sunLightingEnabled;
        window.tacticalSound.playClick();
        return this.sunLightingEnabled;
    }

    toggle3DBuildings() {
        this.buildingsEnabled = !this.buildingsEnabled;
        if (this.osmBuildings) {
            this.osmBuildings.show = this.buildingsEnabled;
        }
        window.tacticalSound.playClick();
        return this.buildingsEnabled;
    }

    openCameraModal(camData) {
        window.tacticalSound.playSonarPing();
        const modal = document.getElementById('cameraModal');
        const title = document.getElementById('modalCamTitle');
        const img = document.getElementById('modalCamImg');
        const loc = document.getElementById('modalCamLoc');
        const coords = document.getElementById('modalCamCoords');

        if (modal) {
            if (title) title.textContent = camData.name || 'SURVEILLANCE UNIT';
            if (loc) loc.textContent = camData.city || 'METROPOLITAN SECTOR';
            if (coords) coords.textContent = `${camData.latitude.toFixed(4)}, ${camData.longitude.toFixed(4)}`;
            if (img) {
                // Route through local CORS proxy if needed
                const srcUrl = camData.image_url;
                img.src = srcUrl.startsWith('http') ? `/api/proxy/image?url=${encodeURIComponent(srcUrl)}` : srcUrl;
            }
            modal.style.display = 'flex';
        }
    }

    closeCameraModal() {
        window.tacticalSound.playClick();
        const modal = document.getElementById('cameraModal');
        if (modal) modal.style.display = 'none';
    }
}

// Global bootstrap
window.addEventListener('DOMContentLoaded', () => {
    window.mavenApp = new MavenGlobeApp();
});
