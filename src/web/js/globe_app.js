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
        this.sunLightingEnabled = false; // Default disabled for high brightness/vividness
        this.buildingsEnabled = true;
        this.currentBasemap = 'satellite'; // 'satellite' | 'dark' | 'osm'
        this.activeImageryLayer = null;

        this.init();
    }

    async init() {
        // Initialize Cesium Viewer with high-performance parameters
        this.viewer = new Cesium.Viewer('cesiumContainer', {
            baseLayer: false, // Modern Cesium syntax (v1.107+)
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
            orderIndependentTranslucency: false, // Huge FPS boost on WebGL
            contextOptions: {
                webgl: {
                    alpha: false,
                    antialias: false,
                    preserveDrawingBuffer: false, // Hardware compositor direct blit
                    powerPreference: "high-performance",
                    desynchronized: true
                }
            }
        });

        // 1:1 Direct hardware blit (avoids super-sampling GPU fill-rate penalty)
        this.viewer.resolutionScale = 1.0;
        this.viewer.targetFrameRate = 60;

        const scene = this.viewer.scene;
        const globe = scene.globe;

        // Disable heavy atmospheric raymarching passes for massive framerate boost
        if (scene.skyAtmosphere) scene.skyAtmosphere.show = false;
        if (globe.showGroundAtmosphere !== undefined) globe.showGroundAtmosphere = false;
        if (scene.fog) scene.fog.enabled = false;
        if (scene.sun) scene.sun.show = false;
        if (scene.moon) scene.moon.show = false;

        // Visual and rendering tuning for ultra-high framerates
        globe.baseColor = Cesium.Color.fromCssColorString('#0a1120');
        globe.enableLighting = this.sunLightingEnabled;
        globe.maximumScreenSpaceError = 3.0; // High-efficiency tile streaming
        globe.depthTestAgainstTerrain = false; // Disable heavy terrain collision tests
        globe.tileCacheSize = 100;
        globe.preloadAncestors = false;
        globe.preloadSiblings = false;
        scene.highDynamicRange = false;
        scene.backgroundColor = Cesium.Color.fromCssColorString('#030712');

        // Apply primary high-detail Earth imagery
        await this.setBasemap('satellite');

        // Configure camera inertia for catch, drag, and flick momentum
        const controller = scene.screenSpaceCameraController;
        controller.inertiaSpin = 0.88;
        controller.inertiaTranslate = 0.88;
        controller.inertiaZoom = 0.82;
        controller.bounceAnimationTime = 0.15;
        controller.minimumZoomDistance = 30.0;
        controller.maximumZoomDistance = 40000000.0;

        // Load 3D Buildings if Cesium Ion token is configured
        if (Cesium.Ion.defaultAccessToken && Cesium.Ion.defaultAccessToken.length > 20) {
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
                console.log('OSM 3D Buildings fallback:', e.message);
            }
        }

        // Initialize operational modules
        this.layers = new TacticalLayersManager(this.viewer);
        this.geofenceDrawer = new GeofenceDrawer(this.viewer);
        this.measureTool = new MeasurementTool(this.viewer);
        this.changeViewer = new SatelliteChangeViewer(this.viewer);
        this.weatherLayer = new WeatherSimulationLayer(this.viewer);
        this.countries = new CountriesLayerManager(this.viewer);
        this.sensorOptics = new TacticalSensorOptics(this.viewer);
        this.detectionMesh = new TacticalDetectionMesh(this.viewer);
        this.streetViewMode = false;
        this.cockpitActive = false;
        this.cockpitTarget = null;
        this.cockpitListener = null;

        // Bind global tactical keyboard shortcuts
        this._bindGlobalHotkeys();

        // Bind camera telemetry readout
        this._bindTelemetryReadout();

        // Initial orbital vantage point
        this.viewer.camera.setView({
            destination: Cesium.Cartesian3.fromDegrees(30.0, 20.0, 18000000.0),
            orientation: {
                heading: Cesium.Math.toRadians(0),
                pitch: Cesium.Math.toRadians(-90),
                roll: 0.0
            }
        });

        // Start background telemetry polling
        this.startDataPolling();
        this.loadInitialGeofences();

        // Setup QWebChannel bridge
        this._initQtWebChannel();
    }

    async setBasemap(type) {
        this.currentBasemap = type;
        const imageryLayers = this.viewer.imageryLayers;

        try {
            let provider;
            if (type === 'satellite') {
                // High-Resolution Photorealistic Satellite Imagery (Esri World Imagery)
                provider = await Cesium.ArcGisMapServerImageryProvider.fromUrl(
                    'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer',
                    { enablePickFeatures: false }
                );
            } else if (type === 'dark') {
                // Tactical Dark Matter (CartoDB Dark All)
                provider = new Cesium.UrlTemplateImageryProvider({
                    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
                    subdomains: ['a', 'b', 'c', 'd'],
                    maximumLevel: 19,
                    credit: 'CartoDB Dark Matter'
                });
            } else {
                // OpenStreetMap Standard
                provider = new Cesium.OpenStreetMapImageryProvider({
                    url: 'https://tile.openstreetmap.org/'
                });
            }

            // Remove existing base imagery layer
            if (this.activeImageryLayer) {
                imageryLayers.remove(this.activeImageryLayer);
            }

            this.activeImageryLayer = imageryLayers.addImageryProvider(provider, 0);
            console.log(`Basemap successfully switched to: ${type}`);
            window.tacticalSound.playClick();
        } catch (err) {
            console.warn(`Failed to load ${type} basemap, loading OpenStreetMap fallback:`, err);
            try {
                const fallbackProvider = new Cesium.OpenStreetMapImageryProvider({
                    url: 'https://tile.openstreetmap.org/'
                });
                if (this.activeImageryLayer) {
                    imageryLayers.remove(this.activeImageryLayer);
                }
                this.activeImageryLayer = imageryLayers.addImageryProvider(fallbackProvider, 0);
            } catch (fallbackErr) {
                console.error('All imagery providers failed:', fallbackErr);
            }
        }
    }

    cycleBasemap() {
        const sequence = ['satellite', 'dark', 'osm'];
        const nextIdx = (sequence.indexOf(this.currentBasemap) + 1) % sequence.length;
        this.setBasemap(sequence[nextIdx]);
        return sequence[nextIdx];
    }

    _bindTelemetryReadout() {
        const coordsElem = document.getElementById('hudCoords');
        const altElem = document.getElementById('hudAlt');
        const headingElem = document.getElementById('hudHeading');

        let ticking = false;
        const updateReadout = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    const cam = this.viewer.camera;
                    const carto = cam.positionCartographic;
                    const lon = Cesium.Math.toDegrees(carto.longitude).toFixed(4);
                    const lat = Cesium.Math.toDegrees(carto.latitude).toFixed(4);
                    const heightKm = (carto.height / 1000).toFixed(0);
                    const heading = Cesium.Math.toDegrees(cam.heading).toFixed(0);

                    if (coordsElem) coordsElem.textContent = `${lat}° N, ${lon}° E`;
                    if (altElem) altElem.textContent = `${heightKm} KM`;
                    if (headingElem) headingElem.textContent = `${heading}°`;
                    ticking = false;
                });
                ticking = true;
            }
        };

        this.viewer.camera.changed.addEventListener(updateReadout);
        this.viewer.camera.moveEnd.addEventListener(updateReadout);
    }

    _initQtWebChannel() {
        if (typeof QWebChannel !== 'undefined' && typeof qt !== 'undefined' && qt.webChannelTransport) {
            new QWebChannel(qt.webChannelTransport, (channel) => {
                window.mavenBridge = channel.objects.mavenBridge;
                console.log('Qt WebChannel connected to Python bridge');

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
        // 1. High-frequency dynamic telemetry (flights, vessels, satellites, anomalies)
        const fetchDynamic = async () => {
            try {
                const [flightsRes, vesselsRes, anomRes, satsRes] = await Promise.all([
                    fetch('/api/flights').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/vessels').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/anomalies').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/satellites').then(r => r.json()).catch(() => ({ data: [] })),
                ]);

                if (flightsRes.data) this.layers.updateFlights(flightsRes.data);
                if (vesselsRes.data) this.layers.updateVessels(vesselsRes.data);
                if (anomRes.data) this.layers.updateAnomalies(anomRes.data);
                if (satsRes.data) this.layers.updateSatellites(satsRes.data);

                this._updateCounters({
                    flights: flightsRes.count || 0,
                    vessels: vesselsRes.count || 0,
                    anomalies: anomRes.count || 0,
                    satellites: satsRes.count || 0
                });
            } catch (e) {
                console.warn('Dynamic telemetry polling error:', e);
            }
        };

        // 2. Low-frequency static / environmental updates (cameras, earthquakes, fires, conflicts, weather)
        const fetchStatic = async () => {
            try {
                const [camsRes, quakesRes, firesRes, confRes, weatherRes] = await Promise.all([
                    fetch('/api/cameras?limit=300').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/earthquakes').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/wildfires').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/conflicts').then(r => r.json()).catch(() => ({ data: [] })),
                    fetch('/api/weather').then(r => r.json()).catch(() => ({ data: [] })),
                ]);

                if (camsRes.data) this.layers.updateCameras(camsRes.data);
                if (quakesRes.data) this.layers.updateEarthquakes(quakesRes.data);
                if (firesRes.data) this.layers.updateWildfires(firesRes.data);
                if (confRes.data) this.layers.updateConflicts(confRes.data);
                if (weatherRes.data) this.weatherLayer.updateWeatherGrid(weatherRes.data);

                this._updateCounters({
                    cameras: camsRes.count || 0,
                    quakes: quakesRes.count || 0,
                    fires: firesRes.count || 0
                });
            } catch (e) {
                console.warn('Static layer polling error:', e);
            }
        };

        await fetchDynamic();
        await fetchStatic();

        // Dynamic telemetry every 10s; Static environmental layers every 60s
        setInterval(fetchDynamic, 10000);
        setInterval(fetchStatic, 60000);
    }

    _bindGlobalHotkeys() {
        window.addEventListener('keydown', (e) => {
            if (['input', 'textarea'].includes(document.activeElement.tagName.toLowerCase())) return;

            // Hotkeys 1-5 for Tactical Sensor Optics
            if (e.key === '1') this.sensorOptics.setMode('VISUAL');
            else if (e.key === '2') this.sensorOptics.setMode('NVG');
            else if (e.key === '3') this.sensorOptics.setMode('FLIR');
            else if (e.key === '4') this.sensorOptics.setMode('CRT');
            else if (e.key === '5') this.sensorOptics.setMode('NOIR');
            // 'c' or 'C' for Cockpit Chase-Cam
            else if (e.key === 'c' || e.key === 'C') this.toggleCockpitMode();
            // 'Escape' to disengage Cockpit
            else if (e.key === 'Escape') this.exitCockpitMode();
        });
    }

    enterCockpitMode(entityId) {
        let target = null;
        if (entityId && this.layers.flightSource) {
            target = this.layers.flightSource.entities.getById(entityId);
        }
        if (!target && this.layers.flightSource) {
            const flights = this.layers.flightSource.entities.values;
            if (flights.length > 0) target = flights[0];
        }
        if (!target) return;

        this.cockpitTarget = target;
        this.cockpitActive = true;
        if (window.tacticalSound) window.tacticalSound.playTargetLock();

        if (this.cockpitListener) {
            this.cockpitListener();
            this.cockpitListener = null;
        }

        // Attach preUpdate camera follower
        this.cockpitListener = this.viewer.scene.preUpdate.addEventListener((scene, time) => {
            if (!this.cockpitTarget || !this.cockpitActive) return;
            const pos = this.cockpitTarget.position.getValue(time);
            if (!pos) return;

            const props = this.cockpitTarget.properties || {};
            const headingDeg = props.heading ? (props.heading.getValue() || 0) : 0;
            const headingRad = Cesium.Math.toRadians(headingDeg);

            const carto = Cesium.Cartographic.fromCartesian(pos);
            const cameraDistance = 240.0;
            const offsetLat = (cameraDistance * Math.cos(headingRad + Math.PI)) / 111320.0;
            const offsetLon = (cameraDistance * Math.sin(headingRad + Math.PI)) / (111320.0 * Math.cos(carto.latitude));

            const camPos = Cesium.Cartesian3.fromRadians(
                carto.longitude + offsetLon,
                carto.latitude + offsetLat,
                carto.height + 36.0
            );

            this.viewer.camera.setView({
                destination: camPos,
                orientation: {
                    heading: headingRad,
                    pitch: Cesium.Math.toRadians(-6.5),
                    roll: 0.0
                }
            });

            if (window.mavenBridge) {
                const altFt = Math.round(carto.height * 3.28084);
                const spdKnots = props.velocity_mps ? Math.round(props.velocity_mps.getValue() * 1.94384) : 460;
                window.mavenBridge.notifyCockpitTelemetry(JSON.stringify({
                    active: true,
                    id: this.cockpitTarget.id,
                    callsign: props.callsign ? props.callsign.getValue() : 'TARGET',
                    altitude_ft: altFt,
                    speed_knots: spdKnots,
                    heading_deg: Math.round(headingDeg)
                }));
            }
        });
    }

    exitCockpitMode() {
        if (!this.cockpitActive) return;
        this.cockpitActive = false;
        if (this.cockpitListener) {
            this.cockpitListener();
            this.cockpitListener = null;
        }
        this.cockpitTarget = null;

        if (window.mavenBridge) {
            window.mavenBridge.notifyCockpitTelemetry(JSON.stringify({ active: false }));
        }

        this.viewer.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(30.0, 20.0, 14000000.0),
            duration: 1.6
        });
    }

    toggleCockpitMode(entityId) {
        if (this.cockpitActive) {
            this.exitCockpitMode();
            return false;
        } else {
            this.enterCockpitMode(entityId);
            return true;
        }
    }

    async swoopToNearestCCTV(lat, lon) {
        try {
            const resp = await fetch(`/api/intel/dossier?lat=${lat}&lon=${lon}&name=Sector`);
            const dossier = await resp.json();
            if (dossier.cameras && dossier.cameras.length > 0) {
                const cam = dossier.cameras[0];
                if (window.tacticalSound) window.tacticalSound.playTargetLock();
                this.viewer.camera.flyTo({
                    destination: Cesium.Cartesian3.fromDegrees(cam.longitude, cam.latitude, 450),
                    orientation: {
                        heading: Cesium.Math.toRadians(0),
                        pitch: Cesium.Math.toRadians(-22),
                        roll: 0.0
                    },
                    duration: 2.0
                });
                if (window.mavenBridge) {
                    window.mavenBridge.notifyEntitySelected('live_cam', cam.id, JSON.stringify(cam));
                }
            }
        } catch (e) {
            console.warn('Swoop to nearest CCTV failed:', e);
        }
    }

    _updateCounters(counts) {
        const updateElem = (id, val) => {
            if (val === undefined) return;
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };
        updateElem('countFlights', counts.flights);
        updateElem('countVessels', counts.vessels);
        updateElem('countFires', counts.fires);
        updateElem('countQuakes', counts.quakes);
        updateElem('countCams', counts.cameras);
        updateElem('countAnomalies', counts.anomalies);
        updateElem('countSatellites', counts.satellites);
    }

    async loadInitialGeofences() {
        try {
            const resp = await fetch('/api/geofences');
            const zones = await resp.json();
            this.geofenceDrawer.loadInitialZones(zones);
        } catch (e) {}
    }

    flyTo(lon, lat, height = 150000.0, pitchDeg = -90.0, headingDeg = 0.0) {
        if (window.tacticalSound) window.tacticalSound.playClick();
        this.viewer.camera.flyTo({
            destination: Cesium.Cartesian3.fromDegrees(lon, lat, height),
            orientation: {
                heading: Cesium.Math.toRadians(headingDeg),
                pitch: Cesium.Math.toRadians(pitchDeg),
                roll: 0.0
            },
            duration: 2.2
        });
    }

    resetNorth() {
        if (window.tacticalSound) window.tacticalSound.playClick();
        const carto = this.viewer.camera.positionCartographic;
        this.viewer.camera.flyTo({
            destination: Cesium.Cartesian3.fromRadians(carto.longitude, carto.latitude, carto.height),
            orientation: {
                heading: Cesium.Math.toRadians(0),
                pitch: Cesium.Math.toRadians(-90),
                roll: 0.0
            },
            duration: 1.2
        });
    }

    toggleTilt() {
        if (window.tacticalSound) window.tacticalSound.playClick();
        const carto = this.viewer.camera.positionCartographic;
        const currentPitch = Cesium.Math.toDegrees(this.viewer.camera.pitch);
        const targetPitch = currentPitch < -60 ? -30 : -90;
        this.viewer.camera.flyTo({
            destination: Cesium.Cartesian3.fromRadians(carto.longitude, carto.latitude, Math.min(carto.height, 800000)),
            orientation: {
                heading: this.viewer.camera.heading,
                pitch: Cesium.Math.toRadians(targetPitch),
                roll: 0.0
            },
            duration: 1.5
        });
        return targetPitch === -30;
    }

    zoomIn() {
        if (window.tacticalSound) window.tacticalSound.playClick();
        const height = this.viewer.camera.positionCartographic.height;
        this.viewer.camera.zoomIn(Math.max(500, height * 0.45));
    }

    zoomOut() {
        if (window.tacticalSound) window.tacticalSound.playClick();
        const height = this.viewer.camera.positionCartographic.height;
        this.viewer.camera.zoomOut(Math.min(20000000, height * 0.7));
    }

    toggleStreetViewMode() {
        this.streetViewMode = !this.streetViewMode;
        if (window.tacticalSound) window.tacticalSound.playClick();
        return this.streetViewMode;
    }

    toggleBorders(show) {
        if (window.tacticalSound) window.tacticalSound.playClick();
        if (this.countries) {
            return this.countries.toggleBorders(show);
        }
        return false;
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
