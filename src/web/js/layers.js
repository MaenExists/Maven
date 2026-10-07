/**
 * Tactical Entity Layers & Billboard Collections
 * Manages aircraft, maritime vessels, fires, seismic shocks, surveillance cameras, and threats.
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
        // Configure screen space clustering for aircraft and cameras to avoid clutter
        const clusterSources = [this.flightSource, this.cameraSource, this.vesselSource];
        clusterSources.forEach(source => {
            source.clustering.enabled = true;
            source.clustering.pixelRange = 35;
            source.clustering.minimumClusterSize = 4;

            source.clustering.clusterEvent.addEventListener((clusteredEntities, cluster) => {
                cluster.label.show = true;
                cluster.label.text = clusteredEntities.length.toString();
                cluster.label.font = '12px "JetBrains Mono", monospace';
                cluster.label.fillColor = Cesium.Color.fromCssColorString('#00f0ff');
                cluster.label.outlineColor = Cesium.Color.BLACK;
                cluster.label.outlineWidth = 2;
                cluster.label.style = Cesium.LabelStyle.FILL_AND_OUTLINE;
                cluster.label.verticalOrigin = Cesium.VerticalOrigin.CENTER;

                cluster.billboard.show = true;
                cluster.billboard.image = this._createClusterIcon(clusteredEntities.length);
                cluster.billboard.width = 32;
                cluster.billboard.height = 32;
            });
        });
    }

    _createClusterIcon(count) {
        const canvas = document.createElement('canvas');
        canvas.width = 64;
        canvas.height = 64;
        const ctx = canvas.getContext('2d');

        ctx.beginPath();
        ctx.arc(32, 32, 28, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(6, 12, 24, 0.85)';
        ctx.fill();
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#00f0ff';
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(32, 32, 22, 0, Math.PI * 2);
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.strokeStyle = 'rgba(0, 240, 255, 0.6)';
        ctx.stroke();

        return canvas;
    }

    _createFlightIcon(heading = 0, color = '#00f0ff') {
        const canvas = document.createElement('canvas');
        canvas.width = 36;
        canvas.height = 36;
        const ctx = canvas.getContext('2d');

        ctx.translate(18, 18);
        ctx.rotate((heading * Math.PI) / 180);

        // Tactical Jet Glyph
        ctx.beginPath();
        ctx.moveTo(0, -14);
        ctx.lineTo(12, 10);
        ctx.lineTo(4, 7);
        ctx.lineTo(4, 13);
        ctx.lineTo(0, 10);
        ctx.lineTo(-4, 13);
        ctx.lineTo(-4, 7);
        ctx.lineTo(-12, 10);
        ctx.closePath();

        ctx.fillStyle = color;
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = '#050a14';
        ctx.stroke();

        return canvas;
    }

    _createVesselIcon(heading = 0) {
        const canvas = document.createElement('canvas');
        canvas.width = 32;
        canvas.height = 32;
        const ctx = canvas.getContext('2d');

        ctx.translate(16, 16);
        ctx.rotate((heading * Math.PI) / 180);

        ctx.beginPath();
        ctx.moveTo(0, -12);
        ctx.lineTo(7, 2);
        ctx.lineTo(7, 12);
        ctx.lineTo(-7, 12);
        ctx.lineTo(-7, 2);
        ctx.closePath();

        ctx.fillStyle = '#10b981';
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = '#022c22';
        ctx.stroke();

        return canvas;
    }

    _createCameraIcon() {
        const canvas = document.createElement('canvas');
        canvas.width = 28;
        canvas.height = 28;
        const ctx = canvas.getContext('2d');

        ctx.fillStyle = 'rgba(6, 12, 24, 0.9)';
        ctx.fillRect(4, 8, 14, 12);
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = '#38bdf8';
        ctx.strokeRect(4, 8, 14, 12);

        // Lens cone
        ctx.beginPath();
        ctx.moveTo(18, 11);
        ctx.lineTo(24, 7);
        ctx.lineTo(24, 21);
        ctx.lineTo(18, 17);
        ctx.closePath();
        ctx.fillStyle = '#38bdf8';
        ctx.fill();

        return canvas;
    }

    _createHazardIcon() {
        const canvas = document.createElement('canvas');
        canvas.width = 32;
        canvas.height = 32;
        const ctx = canvas.getContext('2d');

        // Diamond warning
        ctx.beginPath();
        ctx.moveTo(16, 2);
        ctx.lineTo(30, 16);
        ctx.lineTo(16, 30);
        ctx.lineTo(2, 16);
        ctx.closePath();

        ctx.fillStyle = 'rgba(255, 0, 85, 0.85)';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 16px "JetBrains Mono", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('!', 16, 16);

        return canvas;
    }

    updateFlights(flights) {
        if (!this.visibility.flights) return;
        this.flightSource.entities.removeAll();

        flights.forEach(f => {
            const color = f.squawk === '7700' ? '#ff0055' : (f.altitude > 10000 ? '#00f0ff' : '#f59e0b');
            this.flightSource.entities.add({
                id: f.id,
                position: Cesium.Cartesian3.fromDegrees(f.longitude, f.latitude, f.altitude || 10000),
                billboard: {
                    image: this._createFlightIcon(f.heading, color),
                    scale: 0.9,
                    verticalOrigin: Cesium.VerticalOrigin.CENTER,
                    heightReference: Cesium.HeightReference.NONE
                },
                properties: f
            });
        });
    }

    updateVessels(vessels) {
        if (!this.visibility.vessels) return;
        this.vesselSource.entities.removeAll();

        vessels.forEach(v => {
            this.vesselSource.entities.add({
                id: v.id,
                position: Cesium.Cartesian3.fromDegrees(v.longitude, v.latitude, 0),
                billboard: {
                    image: this._createVesselIcon(v.heading),
                    scale: 0.85,
                    verticalOrigin: Cesium.VerticalOrigin.CENTER,
                    heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
                },
                properties: v
            });
        });
    }

    updateWildfires(fires) {
        if (!this.visibility.wildfires) return;
        this.fireSource.entities.removeAll();

        fires.forEach(fire => {
            const size = Math.min(24, Math.max(8, fire.frp_mw / 12));
            this.fireSource.entities.add({
                id: fire.id,
                position: Cesium.Cartesian3.fromDegrees(fire.longitude, fire.latitude, 0),
                point: {
                    pixelSize: size,
                    color: Cesium.Color.fromCssColorString('#ff4500').withAlpha(0.85),
                    outlineColor: Cesium.Color.fromCssColorString('#ffd700'),
                    outlineWidth: 2,
                    heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
                },
                properties: fire
            });
        });
    }

    updateEarthquakes(quakes) {
        if (!this.visibility.earthquakes) return;
        this.quakeSource.entities.removeAll();

        quakes.forEach(q => {
            const radiusMeters = (q.radius_km || 25) * 1000;
            this.quakeSource.entities.add({
                id: q.id,
                position: Cesium.Cartesian3.fromDegrees(q.longitude, q.latitude, 0),
                ellipse: {
                    semiMinorAxis: radiusMeters,
                    semiMajorAxis: radiusMeters,
                    material: Cesium.Color.fromCssColorString('#f59e0b').withAlpha(0.25),
                    outline: true,
                    outlineColor: Cesium.Color.fromCssColorString('#f59e0b'),
                    outlineWidth: 2,
                    heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
                },
                point: {
                    pixelSize: 10,
                    color: Cesium.Color.fromCssColorString('#f59e0b'),
                    outlineColor: Cesium.Color.WHITE,
                    outlineWidth: 1.5
                },
                properties: q
            });
        });
    }

    updateCameras(cams) {
        if (!this.visibility.cameras) return;
        this.cameraSource.entities.removeAll();

        cams.forEach(cam => {
            this.cameraSource.entities.add({
                id: cam.id,
                position: Cesium.Cartesian3.fromDegrees(cam.longitude, cam.latitude, 0),
                billboard: {
                    image: this._createCameraIcon(),
                    scale: 0.9,
                    verticalOrigin: Cesium.VerticalOrigin.CENTER,
                    heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
                },
                properties: cam
            });
        });
    }

    updateConflicts(conflicts) {
        if (!this.visibility.conflicts) return;
        this.conflictSource.entities.removeAll();

        conflicts.forEach(inc => {
            this.conflictSource.entities.add({
                id: inc.id,
                position: Cesium.Cartesian3.fromDegrees(inc.longitude, inc.latitude, 0),
                billboard: {
                    image: this._createHazardIcon(),
                    scale: 0.9,
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
                    material: Cesium.Color.fromCssColorString(anom.pulse_color || '#ff0055').withAlpha(0.3),
                    outline: true,
                    outlineColor: Cesium.Color.fromCssColorString(anom.pulse_color || '#ff0055'),
                    outlineWidth: 3,
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
        handler.setInputAction((click) => {
            const picked = this.viewer.scene.pick(click.position);
            if (Cesium.defined(picked) && picked.id && picked.id.properties) {
                window.tacticalSound.playTargetLock();
                const props = {};
                const propNames = picked.id.properties.propertyNames;
                propNames.forEach(name => {
                    props[name] = picked.id.properties[name].getValue();
                });

                const entType = props.type || 'entity';
                const entId = props.id || picked.id.id;

                // If camera, trigger surveillance modal directly
                if (entType === 'live_cam') {
                    if (window.mavenApp) {
                        window.mavenApp.openCameraModal(props);
                    }
                }

                // Notify bridge / QML
                if (window.mavenBridge) {
                    window.mavenBridge.notifyEntitySelected(entType, entId, JSON.stringify(props));
                }
                if (window.parent && window.parent.onEntitySelected) {
                    window.parent.onEntitySelected(entType, entId, props);
                }
            }
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
    }
}

window.TacticalLayersManager = TacticalLayersManager;
