/**
 * Tactical Entity Layers & Billboard Collections
 * Manages aircraft, maritime vessels, fires, seismic shocks, surveillance cameras, and threats.
 * Optimized with Canvas Glyph Texture Caching & In-Place Entity Updates for 60 FPS performance.
 */

class TacticalLayersManager {
    constructor(viewer) {
        this.viewer = viewer;

        // Custom Data Sources
        this.flightSource = new Cesium.CustomDataSource('flights');
        this.vesselSource = new Cesium.CustomDataSource('vessels');
        this.fireSource = new Cesium.CustomDataSource('wildfires');
        this.quakeSource = new Cesium.CustomDataSource('earthquakes');
        this.cameraSource = new Cesium.CustomDataSource('cameras');
        this.conflictSource = new Cesium.CustomDataSource('conflicts');
        this.anomalySource = new Cesium.CustomDataSource('anomalies');

        // Texture Cache to prevent GC pauses
        this.iconCache = new Map();

        // Layer visibility flags
        this.visibility = {
            flights: true,
            vessels: true,
            wildfires: true,
            earthquakes: true,
            cameras: true,
            conflicts: true,
            anomalies: true
        };

        this._initDataSources();
        this._initClustering();
        this._initSelectionHandler();
    }

    _initDataSources() {
        this.viewer.dataSources.add(this.flightSource);
        this.viewer.dataSources.add(this.vesselSource);
        this.viewer.dataSources.add(this.fireSource);
        this.viewer.dataSources.add(this.quakeSource);
        this.viewer.dataSources.add(this.cameraSource);
        this.viewer.dataSources.add(this.conflictSource);
        this.viewer.dataSources.add(this.anomalySource);
    }

    _initClustering() {
        const clusterSources = [this.flightSource, this.cameraSource, this.vesselSource];
        clusterSources.forEach(source => {
            source.clustering.enabled = true;
            source.clustering.pixelRange = 40;
            source.clustering.minimumClusterSize = 5;

            source.clustering.clusterEvent.addEventListener((clusteredEntities, cluster) => {
                cluster.label.show = true;
                cluster.label.text = clusteredEntities.length.toString();
                cluster.label.font = '11px "JetBrains Mono", monospace';
                cluster.label.fillColor = Cesium.Color.fromCssColorString('#00f0ff');
                cluster.label.outlineColor = Cesium.Color.BLACK;
                cluster.label.outlineWidth = 2;
                cluster.label.style = Cesium.LabelStyle.FILL_AND_OUTLINE;
                cluster.label.verticalOrigin = Cesium.VerticalOrigin.CENTER;

                cluster.billboard.show = true;
                cluster.billboard.image = this._getClusterIcon(clusteredEntities.length);
                cluster.billboard.width = 28;
                cluster.billboard.height = 28;
            });
        });
    }

    _getClusterIcon(count) {
        const key = 'cluster';
        if (this.iconCache.has(key)) return this.iconCache.get(key);

        const canvas = document.createElement('canvas');
        canvas.width = 56;
        canvas.height = 56;
        const ctx = canvas.getContext('2d');

        ctx.beginPath();
        ctx.arc(28, 28, 24, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(6, 12, 24, 0.85)';
        ctx.fill();
        ctx.lineWidth = 2.5;
        ctx.strokeStyle = '#00f0ff';
        ctx.stroke();

        this.iconCache.set(key, canvas);
        return canvas;
    }

    _getFlightIcon(heading = 0, color = '#00f0ff') {
        const roundedHeading = Math.round(heading / 10) * 10 % 360;
        const key = `flight_${color}_${roundedHeading}`;
        if (this.iconCache.has(key)) return this.iconCache.get(key);

        const canvas = document.createElement('canvas');
        canvas.width = 32;
        canvas.height = 32;
        const ctx = canvas.getContext('2d');

        ctx.translate(16, 16);
        ctx.rotate((roundedHeading * Math.PI) / 180);

        ctx.beginPath();
        ctx.moveTo(0, -12);
        ctx.lineTo(10, 8);
        ctx.lineTo(3, 5);
        ctx.lineTo(3, 11);
        ctx.lineTo(0, 8);
        ctx.lineTo(-3, 11);
        ctx.lineTo(-3, 5);
        ctx.lineTo(-10, 8);
        ctx.closePath();

        ctx.fillStyle = color;
        ctx.fill();
        ctx.lineWidth = 1.2;
        ctx.strokeStyle = '#050a14';
        ctx.stroke();

        this.iconCache.set(key, canvas);
        return canvas;
    }

    _getVesselIcon(heading = 0) {
        const roundedHeading = Math.round(heading / 15) * 15 % 360;
        const key = `vessel_${roundedHeading}`;
        if (this.iconCache.has(key)) return this.iconCache.get(key);

        const canvas = document.createElement('canvas');
        canvas.width = 28;
        canvas.height = 28;
        const ctx = canvas.getContext('2d');

        ctx.translate(14, 14);
        ctx.rotate((roundedHeading * Math.PI) / 180);

        ctx.beginPath();
        ctx.moveTo(0, -10);
        ctx.lineTo(6, 2);
        ctx.lineTo(6, 10);
        ctx.lineTo(-6, 10);
        ctx.lineTo(-6, 2);
        ctx.closePath();

        ctx.fillStyle = '#10b981';
        ctx.fill();
        ctx.lineWidth = 1.2;
        ctx.strokeStyle = '#022c22';
        ctx.stroke();

        this.iconCache.set(key, canvas);
        return canvas;
    }

    _getCameraIcon() {
        const key = 'cam_icon';
        if (this.iconCache.has(key)) return this.iconCache.get(key);

        const canvas = document.createElement('canvas');
        canvas.width = 26;
        canvas.height = 26;
        const ctx = canvas.getContext('2d');

        ctx.fillStyle = 'rgba(6, 12, 24, 0.9)';
        ctx.fillRect(4, 7, 13, 11);
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = '#38bdf8';
        ctx.strokeRect(4, 7, 13, 11);

        ctx.beginPath();
        ctx.moveTo(17, 10);
        ctx.lineTo(22, 6);
        ctx.lineTo(22, 19);
        ctx.lineTo(17, 15);
        ctx.closePath();
        ctx.fillStyle = '#38bdf8';
        ctx.fill();

        this.iconCache.set(key, canvas);
        return canvas;
    }

    _getHazardIcon() {
        const key = 'hazard_icon';
        if (this.iconCache.has(key)) return this.iconCache.get(key);

        const canvas = document.createElement('canvas');
        canvas.width = 28;
        canvas.height = 28;
        const ctx = canvas.getContext('2d');

        ctx.beginPath();
        ctx.moveTo(14, 2);
        ctx.lineTo(26, 14);
        ctx.lineTo(14, 26);
        ctx.lineTo(2, 14);
        ctx.closePath();

        ctx.fillStyle = 'rgba(255, 0, 85, 0.9)';
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 14px "JetBrains Mono", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('!', 14, 14);

        this.iconCache.set(key, canvas);
        return canvas;
    }

    // In-place updates to avoid garbage collection hitches
    updateFlights(flights) {
        if (!this.visibility.flights) return;
        const activeIds = new Set();

        flights.forEach(f => {
            activeIds.add(f.id);
            const pos = Cesium.Cartesian3.fromDegrees(f.longitude, f.latitude, f.altitude || 10000);
            const existing = this.flightSource.entities.getById(f.id);

            if (existing) {
                existing.position = pos;
                existing.properties = f;
            } else {
                const color = f.squawk === '7700' ? '#ff0055' : (f.altitude > 10000 ? '#00f0ff' : '#f59e0b');
                this.flightSource.entities.add({
                    id: f.id,
                    position: pos,
                    billboard: {
                        image: this._getFlightIcon(f.heading, color),
                        scale: 0.85,
                        verticalOrigin: Cesium.VerticalOrigin.CENTER,
                        heightReference: Cesium.HeightReference.NONE
                    },
                    properties: f
                });
            }
        });
    }

    updateVessels(vessels) {
        if (!this.visibility.vessels) return;

        vessels.forEach(v => {
            const pos = Cesium.Cartesian3.fromDegrees(v.longitude, v.latitude, 5);
            const existing = this.vesselSource.entities.getById(v.id);

            if (existing) {
                existing.position = pos;
                existing.properties = v;
            } else {
                this.vesselSource.entities.add({
                    id: v.id,
                    position: pos,
                    billboard: {
                        image: this._getVesselIcon(v.heading),
                        scale: 0.8,
                        verticalOrigin: Cesium.VerticalOrigin.CENTER,
                        heightReference: Cesium.HeightReference.NONE
                    },
                    properties: v
                });
            }
        });
    }

    updateWildfires(fires) {
        if (!this.visibility.wildfires) return;
        if (this.fireSource.entities.values.length > 0) return; // Keep static active fires

        fires.forEach(fire => {
            const size = Math.min(18, Math.max(6, fire.frp_mw / 18));
            this.fireSource.entities.add({
                id: fire.id,
                position: Cesium.Cartesian3.fromDegrees(fire.longitude, fire.latitude, 10),
                point: {
                    pixelSize: size,
                    color: Cesium.Color.fromCssColorString('#ff4500').withAlpha(0.85),
                    outlineColor: Cesium.Color.fromCssColorString('#ffd700'),
                    outlineWidth: 1.5,
                    heightReference: Cesium.HeightReference.NONE
                },
                properties: fire
            });
        });
    }

    updateEarthquakes(quakes) {
        if (!this.visibility.earthquakes) return;
        if (this.quakeSource.entities.values.length > 0) return;

        quakes.forEach(q => {
            const radiusMeters = (q.radius_km || 25) * 1000;
            this.quakeSource.entities.add({
                id: q.id,
                position: Cesium.Cartesian3.fromDegrees(q.longitude, q.latitude, 15),
                ellipse: {
                    semiMinorAxis: radiusMeters,
                    semiMajorAxis: radiusMeters,
                    material: Cesium.Color.fromCssColorString('#f59e0b').withAlpha(0.2),
                    outline: true,
                    outlineColor: Cesium.Color.fromCssColorString('#f59e0b'),
                    outlineWidth: 1.5,
                    heightReference: Cesium.HeightReference.NONE
                },
                point: {
                    pixelSize: 8,
                    color: Cesium.Color.fromCssColorString('#f59e0b'),
                    outlineColor: Cesium.Color.WHITE,
                    outlineWidth: 1.5,
                    heightReference: Cesium.HeightReference.NONE
                },
                properties: q
            });
        });
    }

    updateCameras(cams) {
        if (!this.visibility.cameras || !cams || !cams.length) return;
        if (this.cameraSource.entities.values.length >= cams.length && cams.length > 0) return;

        this.cameraSource.entities.suspendEvents();
        const existingIds = new Set(this.cameraSource.entities.values.map(e => e.id));

        const landmarkCondition = new Cesium.DistanceDisplayCondition(0, 36000000.0);
        const corridorCondition = new Cesium.DistanceDisplayCondition(0, 9500000.0);
        const municipalCondition = new Cesium.DistanceDisplayCondition(0, 3800000.0);

        const icon = this._getCameraIcon();

        for (let i = 0; i < cams.length; i++) {
            const cam = cams[i];
            if (existingIds.has(cam.id)) continue;
            existingIds.add(cam.id);

            // Level of Detail (LOD):
            // - Hubs / high priority / famous landmarks visible globally from orbit
            // - Metropolitan corridors visible below 9.5M meters
            // - Dense municipal & highway CCTV visible below 3.8M meters
            let distCond = municipalCondition;
            if (cam.is_hub || cam.priority === 'high' || i < 120 || cam.id.startsWith('cam-tokyo-') || cam.id.startsWith('cam-nyc-') || cam.id.startsWith('cam-london-')) {
                distCond = landmarkCondition;
            } else if (cam.stream_type === 'youtube' || cam.direction === 'Plaza Overview' || cam.direction === 'Waterfront Vista') {
                distCond = corridorCondition;
            }

            this.cameraSource.entities.add({
                id: cam.id,
                position: Cesium.Cartesian3.fromDegrees(cam.longitude, cam.latitude, 25),
                billboard: {
                    image: icon,
                    scale: 0.85,
                    verticalOrigin: Cesium.VerticalOrigin.CENTER,
                    heightReference: Cesium.HeightReference.NONE,
                    distanceDisplayCondition: distCond
                },
                properties: cam
            });
        }

        this.cameraSource.entities.resumeEvents();
    }

    updateConflicts(conflicts) {
        if (!this.visibility.conflicts) return;
        if (this.conflictSource.entities.values.length > 0) return;

        conflicts.forEach(inc => {
            this.conflictSource.entities.add({
                id: inc.id,
                position: Cesium.Cartesian3.fromDegrees(inc.longitude, inc.latitude, 0),
                billboard: {
                    image: this._getHazardIcon(),
                    scale: 0.85,
                    verticalOrigin: Cesium.VerticalOrigin.CENTER,
                    heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
                },
                properties: inc
            });
        });
    }

    updateAnomalies(anomalies) {
        if (!this.visibility.anomalies) return;
        this.anomalySource.entities.removeAll();

        anomalies.forEach(anom => {
            const rad = anom.radius_meters || 35000;
            this.anomalySource.entities.add({
                id: anom.id,
                position: Cesium.Cartesian3.fromDegrees(anom.longitude, anom.latitude, 0),
                ellipse: {
                    semiMinorAxis: rad,
                    semiMajorAxis: rad,
                    material: Cesium.Color.fromCssColorString(anom.pulse_color || '#ff0055').withAlpha(0.25),
                    outline: true,
                    outlineColor: Cesium.Color.fromCssColorString(anom.pulse_color || '#ff0055'),
                    outlineWidth: 2,
                    heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
                },
                properties: anom
            });
        });
    }

    toggleLayer(layerId, isVisible) {
        this.visibility[layerId] = isVisible;
        const sourceMap = {
            flights: this.flightSource,
            vessels: this.vesselSource,
            wildfires: this.fireSource,
            earthquakes: this.quakeSource,
            cameras: this.cameraSource,
            conflicts: this.conflictSource,
            anomalies: this.anomalySource
        };
        if (sourceMap[layerId]) {
            sourceMap[layerId].show = isVisible;
        }
    }

    _initSelectionHandler() {
        const handler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas);
        const tooltip = document.getElementById('tacticalTooltip');

        // Track drag state so we NEVER stall GPU with raycasting during camera orbit / pan
        let isMouseDown = false;
        let lastPickTime = 0;
        let pickPending = false;

        handler.setInputAction(() => {
            isMouseDown = true;
            if (tooltip) {
                tooltip.style.opacity = '0';
                tooltip.style.display = 'none';
            }
        }, Cesium.ScreenSpaceEventType.LEFT_DOWN);

        handler.setInputAction(() => { isMouseDown = false; }, Cesium.ScreenSpaceEventType.LEFT_UP);
        handler.setInputAction(() => { isMouseDown = true; if (tooltip) tooltip.style.display = 'none'; }, Cesium.ScreenSpaceEventType.MIDDLE_DOWN);
        handler.setInputAction(() => { isMouseDown = false; }, Cesium.ScreenSpaceEventType.MIDDLE_UP);
        handler.setInputAction(() => { isMouseDown = true; if (tooltip) tooltip.style.display = 'none'; }, Cesium.ScreenSpaceEventType.RIGHT_DOWN);
        handler.setInputAction(() => { isMouseDown = false; }, Cesium.ScreenSpaceEventType.RIGHT_UP);

        // Ultra-high performance throttled Hover Tooltips on all signs, markers, and country territories
        handler.setInputAction((movement) => {
            if (isMouseDown) return;

            const now = performance.now();
            if (now - lastPickTime < 45 || pickPending) return;
            pickPending = true;

            requestAnimationFrame(() => {
                pickPending = false;
                lastPickTime = performance.now();
                if (isMouseDown) return;

                const picked = this.viewer.scene.pick(movement.endPosition);
                if (Cesium.defined(picked) && picked.id) {
                    this.viewer.scene.canvas.style.cursor = 'pointer';
                    const entity = picked.id;

                    // Check if hovering over country boundary polygon
                    if (entity.customCountryData) {
                        if (window.mavenApp && window.mavenApp.countries) {
                            window.mavenApp.countries.highlightCountryOnHover(entity);
                        }
                        if (tooltip) {
                            const c = entity.customCountryData;
                            const popStr = c.population ? (c.population > 1e6 ? `${(c.population / 1e6).toFixed(1)}M` : `${c.population.toLocaleString()}`) : 'N/A';
                            tooltip.innerHTML = `
                                <div class="tooltip-header">🌍 SOVEREIGN TERRITORY</div>
                                <div class="tooltip-title">${c.name}</div>
                                <div class="tooltip-meta">CONTINENT: ${c.continent} | POP: ${popStr}</div>
                                <div class="tooltip-hint">▶ CLICK TO INSPECT COUNTRY DOSSIER</div>
                            `;
                            tooltip.style.left = `${Math.min(window.innerWidth - 330, movement.endPosition.x + 16)}px`;
                            tooltip.style.top = `${Math.min(window.innerHeight - 100, movement.endPosition.y + 16)}px`;
                            tooltip.style.display = 'block';
                            tooltip.style.opacity = '1';
                        }
                        return;
                    }

                    // Hovering over tactical entities (flight, vessel, camera, earthquake, fire, conflict, weather)
                    let props = {};
                    if (entity.properties) {
                        if (typeof entity.properties.getValue === 'function') {
                            props = entity.properties.getValue(Cesium.JulianDate.now()) || {};
                        } else if (entity.properties.propertyNames) {
                            entity.properties.propertyNames.forEach(name => {
                                props[name] = entity.properties[name].getValue();
                            });
                        }
                    }

                    const entType = props.type || 'entity';
                    if (tooltip && (props.name || props.callsign || props.title || props.id)) {
                        let header = 'TACTICAL TARGET';
                        let title = props.callsign || props.name || props.title || props.id;
                        let meta = '';
                        let hint = '▶ CLICK TO INSPECT';

                        if (entType === 'flight') {
                            header = '✈️ AIRCRAFT [AIR RECON]';
                            title = `${props.callsign || 'FLIGHT'} (${props.origin_country || 'INTERNATIONAL'})`;
                            meta = `ALT: ${Math.round(props.altitude || 0)}m | SPD: ${Math.round(props.velocity_knots || 0)} kts | HDG: ${Math.round(props.heading || 0)}°`;
                            hint = props.squawk === '7700' ? '⚠️ EMERGENCY SQUAWK 7700' : '▶ CLICK FOR TARGET TELEMETRY';
                        } else if (entType === 'vessel') {
                            header = '🚢 MARITIME AIS VESSEL';
                            title = `${props.name || 'VESSEL'} [${(props.vessel_type || 'CARGO').toUpperCase()}]`;
                            meta = `SPEED: ${props.speed_knots || 0} kts | DEST: ${props.destination || 'TRANSIT'}`;
                            hint = '▶ CLICK FOR MARITIME TELEMETRY';
                        } else if (entType === 'live_cam') {
                            header = '📹 LIVE SURVEILLANCE CCTV';
                            title = props.name || 'CCTV UNIT';
                            meta = `${props.city || 'METROPOLITAN SECTOR'} // ${props.direction || 'Corridor'}`;
                            hint = '▶ CLICK TO ENTER LIVE STREET VIEW';
                        } else if (entType === 'earthquake') {
                            header = '⚠️ SEISMIC HAZARD [USGS]';
                            title = `M${props.magnitude} - ${props.place || 'Seismic Event'}`;
                            meta = `DEPTH: ${props.depth_km || 10} KM | TIME: ACTIVE`;
                        } else if (entType === 'wildfire') {
                            header = '🔥 THERMAL FRONT [FIRMS]';
                            title = `ACTIVE WILDFIRE CLUSTER`;
                            meta = `RADIATIVE POWER: ${props.frp_mw || 25} MW`;
                        } else if (entType === 'conflict') {
                            header = '⚔️ SECURITY / HAZARD ZONE';
                            title = props.title || 'SECURITY INCIDENT';
                            meta = `SEVERITY: ${props.severity || 'ELEVATED'}`;
                        } else if (entType === 'weather') {
                            header = '🌦️ ATMOSPHERIC TELEMETRY';
                            title = props.title || props.name;
                            meta = props.details || `${props.temperature_c}°C`;
                        }

                        tooltip.innerHTML = `
                            <div class="tooltip-header">${header}</div>
                            <div class="tooltip-title">${title}</div>
                            <div class="tooltip-meta">${meta}</div>
                            <div class="tooltip-hint">${hint}</div>
                        `;
                        tooltip.style.left = `${Math.min(window.innerWidth - 330, movement.endPosition.x + 16)}px`;
                        tooltip.style.top = `${Math.min(window.innerHeight - 100, movement.endPosition.y + 16)}px`;
                        tooltip.style.display = 'block';
                        tooltip.style.opacity = '1';
                    }
                } else {
                    this.viewer.scene.canvas.style.cursor = 'default';
                    if (window.mavenApp && window.mavenApp.countries) {
                        window.mavenApp.countries.clearHover();
                    }
                    if (tooltip) {
                        tooltip.style.opacity = '0';
                        tooltip.style.display = 'none';
                    }
                }
            });
        }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

        // Click handler with direct Street View and Country Dossier triggers
        handler.setInputAction((click) => {
            const picked = this.viewer.scene.pick(click.position);
            if (Cesium.defined(picked) && picked.id) {
                window.tacticalSound.playTargetLock();
                const entity = picked.id;

                // 1. Country Selection
                if (entity.customCountryData) {
                    if (window.mavenApp && window.mavenApp.countries) {
                        const countryData = window.mavenApp.countries.selectCountry(entity);
                        if (window.mavenBridge) {
                            window.mavenBridge.notifyEntitySelected('country', countryData.name, JSON.stringify(countryData));
                        }
                    }
                    return;
                }

                // 2. Tactical Entities (Camera, Flight, Vessel, Hazard)
                let props = {};
                if (entity.properties) {
                    if (typeof entity.properties.getValue === 'function') {
                        props = entity.properties.getValue(Cesium.JulianDate.now()) || {};
                    } else if (entity.properties.propertyNames) {
                        entity.properties.propertyNames.forEach(name => {
                            props[name] = entity.properties[name].getValue();
                        });
                    }
                }

                const entType = props.type || 'entity';
                const entId = props.id || entity.id;

                // If live camera clicked: swoop camera directly down to ground level and open feed
                if (entType === 'live_cam') {
                    if (props.longitude && props.latitude) {
                        this.viewer.camera.flyTo({
                            destination: Cesium.Cartesian3.fromDegrees(props.longitude, props.latitude, 450),
                            orientation: {
                                heading: Cesium.Math.toRadians(0),
                                pitch: Cesium.Math.toRadians(-22),
                                roll: 0.0
                            },
                            duration: 2.0
                        });
                    }
                }

                if (window.mavenBridge) {
                    window.mavenBridge.notifyEntitySelected(entType, entId, JSON.stringify(props));
                }
            } else {
                // Clicked on planetary terrain: reverse-geodetic lookup and Street View swoop
                const ray = this.viewer.camera.getPickRay(click.position);
                const cartesian = this.viewer.scene.globe.pick(ray, this.viewer.scene);
                if (Cesium.defined(cartesian)) {
                    const carto = Cesium.Cartographic.fromCartesian(cartesian);
                    const lon = Cesium.Math.toDegrees(carto.longitude);
                    const lat = Cesium.Math.toDegrees(carto.latitude);

                    // If Street View mode is active, smoothly swoop to ground level and query sector dossier
                    if (window.mavenApp && window.mavenApp.streetViewMode) {
                        this.viewer.camera.flyTo({
                            destination: Cesium.Cartesian3.fromDegrees(lon, lat, 400),
                            orientation: {
                                heading: this.viewer.camera.heading,
                                pitch: Cesium.Math.toRadians(-20),
                                roll: 0.0
                            },
                            duration: 2.0
                        });

                        if (window.mavenBridge) {
                            window.mavenBridge.notifyEntitySelected('ground_point', `geo_${lat.toFixed(3)}_${lon.toFixed(3)}`, JSON.stringify({
                                type: 'ground_point',
                                latitude: lat,
                                longitude: lon,
                                name: `Sector Coordinates: ${lat.toFixed(3)}°, ${lon.toFixed(3)}°`
                            }));
                        }
                    }
                }
            }
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    }
}

window.TacticalLayersManager = TacticalLayersManager;
