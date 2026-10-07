/**
 * Geodesic Measurement Toolkit for Cesium Globe
 * Interactive geodesic distance ruler, azimuth bearing, and surface area polygon calculator.
 */

class MeasurementTool {
    constructor(viewer) {
        this.viewer = viewer;
        this.mode = 'none'; // 'distance' | 'area' | 'none'
        this.points = [];
        this.handler = null;
        this.measureDataSource = new Cesium.CustomDataSource('measurements');
        this.viewer.dataSources.add(this.measureDataSource);
    }

    setMode(mode) {
        this.clear();
        this.mode = mode;
        if (mode === 'none') {
            if (this.handler) {
                this.handler.destroy();
                this.handler = null;
            }
            return;
        }

        window.tacticalSound.playClick();
        this.handler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas);

        this.handler.setInputAction((click) => {
            const earthPos = this._getRayPosition(click.position);
            if (earthPos) {
                window.tacticalSound.playClick();
                this.points.push(earthPos);
                this._renderCurrentMeasurement();
            }
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

        this.handler.setInputAction(() => {
            window.tacticalSound.playSonarPing();
            this.setMode('none');
        }, Cesium.ScreenSpaceEventType.RIGHT_CLICK);
    }

    clear() {
        this.points = [];
        this.measureDataSource.entities.removeAll();
        if (this.handler) {
            this.handler.destroy();
            this.handler = null;
        }
    }

    _getRayPosition(screenPos) {
        const ray = this.viewer.camera.getPickRay(screenPos);
        return this.viewer.scene.globe.pick(ray, this.viewer.scene);
    }

    _renderCurrentMeasurement() {
        this.measureDataSource.entities.removeAll();

        // Add point markers
        this.points.forEach((pos, idx) => {
            this.measureDataSource.entities.add({
                position: pos,
                point: {
                    pixelSize: 8,
                    color: Cesium.Color.fromCssColorString('#00f0ff'),
                    outlineColor: Cesium.Color.BLACK,
                    outlineWidth: 2
                },
                label: {
                    text: `P${idx + 1}`,
                    font: '11px "JetBrains Mono", monospace',
                    fillColor: Cesium.Color.WHITE,
                    pixelOffset: new Cesium.Cartesian2(0, -14)
                }
            });
        });

        if (this.mode === 'distance' && this.points.length >= 2) {
            // Geodesic polyline between points
            this.measureDataSource.entities.add({
                polyline: {
                    positions: this.points,
                    width: 3,
                    material: new Cesium.PolylineDashMaterialProperty({
                        color: Cesium.Color.fromCssColorString('#00f0ff'),
                        dashLength: 16.0
                    }),
                    arcType: Cesium.ArcType.GEODESIC
                }
            });

            // Calculate distance
            const p1 = Cesium.Cartographic.fromCartesian(this.points[0]);
            const p2 = Cesium.Cartographic.fromCartesian(this.points[1]);
            const lat1 = Cesium.Math.toDegrees(p1.latitude);
            const lon1 = Cesium.Math.toDegrees(p1.longitude);
            const lat2 = Cesium.Math.toDegrees(p2.latitude);
            const lon2 = Cesium.Math.toDegrees(p2.longitude);

            fetch(`/api/measure/distance?lat1=${lat1}&lon1=${lon1}&lat2=${lat2}&lon2=${lon2}`)
                .then(r => r.json())
                .then(res => {
                    const midPos = Cesium.Cartesian3.midpoint(this.points[0], this.points[1], new Cesium.Cartesian3());
                    this.measureDataSource.entities.add({
                        position: midPos,
                        label: {
                            text: `DIST: ${res.distance_km} KM (${res.distance_nm} NM)\nBEARING: ${res.bearing_deg}°`,
                            font: '12px "JetBrains Mono", monospace',
                            fillColor: Cesium.Color.fromCssColorString('#00f0ff'),
                            showBackground: true,
                            backgroundColor: Cesium.Color.fromCssColorString('#06090e').withAlpha(0.9),
                            backgroundPadding: new Cesium.Cartesian2(6, 4)
                        }
                    });
                })
                .catch(() => {});
        }

        if (this.mode === 'area' && this.points.length >= 3) {
            this.measureDataSource.entities.add({
                polygon: {
                    hierarchy: new Cesium.PolygonHierarchy(this.points),
                    material: Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.2),
                    outline: true,
                    outlineColor: Cesium.Color.fromCssColorString('#00f0ff'),
                    outlineWidth: 2
                }
            });

            const coords = this.points.map(pos => {
                const c = Cesium.Cartographic.fromCartesian(pos);
                return [Cesium.Math.toDegrees(c.longitude), Cesium.Math.toDegrees(c.latitude)];
            });

            fetch('/api/measure/area', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ coordinates: coords })
            })
                .then(r => r.json())
                .then(res => {
                    const centerPos = this.points[0];
                    this.measureDataSource.entities.add({
                        position: centerPos,
                        label: {
                            text: `AREA: ${res.area_km2} KM²\n(${res.hectares} HA)`,
                            font: '12px "JetBrains Mono", monospace',
                            fillColor: Cesium.Color.fromCssColorString('#00f0ff'),
                            showBackground: true,
                            backgroundColor: Cesium.Color.fromCssColorString('#06090e').withAlpha(0.9),
                            backgroundPadding: new Cesium.Cartesian2(6, 4)
                        }
                    });
                })
                .catch(() => {});
        }
    }
}

window.MeasurementTool = MeasurementTool;
