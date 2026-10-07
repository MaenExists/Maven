/**
 * Interactive Geofence Polygon Drawing & Zone Management
 * Enables operators to sketch tactical boundary polygons directly on the 3D terrain.
 */

class GeofenceDrawer {
    constructor(viewer) {
        this.viewer = viewer;
        this.active = false;
        this.positions = [];
        this.tempEntity = null;
        this.handler = null;
        this.zonesDataSource = new Cesium.CustomDataSource('geofences');
        this.viewer.dataSources.add(this.zonesDataSource);
    }

    startDrawing() {
        if (this.active) return;
        this.active = true;
        this.positions = [];

        window.tacticalSound.playClick();
        this.handler = new Cesium.ScreenSpaceEventHandler(this.viewer.scene.canvas);

        // Dynamic rubberband polygon
        this.tempEntity = this.viewer.entities.add({
            polygon: {
                hierarchy: new Cesium.CallbackProperty(() => {
                    return new Cesium.PolygonHierarchy(this.positions);
                }, false),
                material: Cesium.Color.fromCssColorString('#ff0055').withAlpha(0.25),
                outline: true,
                outlineColor: Cesium.Color.fromCssColorString('#ff0055'),
                outlineWidth: 2,
                extrudedHeight: 2500
            }
        });

        // Click to add vertex
        this.handler.setInputAction((click) => {
            const earthPos = this._getRayPosition(click.position);
            if (earthPos) {
                window.tacticalSound.playClick();
                this.positions.push(earthPos);
            }
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

        // Move to rubberband
        this.handler.setInputAction((movement) => {
            if (this.positions.length > 0) {
                const earthPos = this._getRayPosition(movement.endPosition);
                if (earthPos) {
                    if (this.positions.length === 1) {
                        this.positions.push(earthPos);
                    } else {
                        this.positions[this.positions.length - 1] = earthPos;
                    }
                }
            }
        }, Cesium.ScreenSpaceEventType.MOUSE_MOVE);

        // Right-click to finish
        this.handler.setInputAction(() => {
            this.finishDrawing();
        }, Cesium.ScreenSpaceEventType.RIGHT_CLICK);
    }

    finishDrawing() {
        if (!this.active) return;
        this.active = false;

        if (this.handler) {
            this.handler.destroy();
            this.handler = null;
        }

        if (this.tempEntity) {
            this.viewer.entities.remove(this.tempEntity);
            this.tempEntity = null;
        }

        if (this.positions.length >= 3) {
            window.tacticalSound.playSonarPing();
            const coordinates = this.positions.map(pos => {
                const carto = Cesium.Cartographic.fromCartesian(pos);
                return [
                    parseFloat(Cesium.Math.toDegrees(carto.longitude).toFixed(5)),
                    parseFloat(Cesium.Math.toDegrees(carto.latitude).toFixed(5))
                ];
            });

            this._registerNewGeofence(coordinates);
        }
    }

    _getRayPosition(screenPos) {
        const ray = this.viewer.camera.getPickRay(screenPos);
        return this.viewer.scene.globe.pick(ray, this.viewer.scene);
    }

    async _registerNewGeofence(coordinates) {
        const zoneId = `zone-${Date.now()}`;
        const payload = {
            id: zoneId,
            name: `Restricted Sector ${new Date().toLocaleTimeString()}`,
            polygon: coordinates,
            alert_types: ['flight', 'vessel'],
            description: 'Custom operator-defined tactical exclusion perimeter.',
            color: '#ff0055'
        };

        try {
            const resp = await fetch('/api/geofences', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (resp.ok) {
                const created = await resp.json();
                this.renderZone(created);
            }
        } catch (e) {
            console.error('Failed to submit geofence:', e);
            // Render locally
            this.renderZone(payload);
        }
    }

    renderZone(zone) {
        const positions = zone.polygon.map(coord => {
            return Cesium.Cartesian3.fromDegrees(coord[0], coord[1]);
        });

        this.zonesDataSource.entities.add({
            id: zone.id,
            name: zone.name,
            polygon: {
                hierarchy: new Cesium.PolygonHierarchy(positions),
                material: Cesium.Color.fromCssColorString(zone.color || '#ff0055').withAlpha(0.2),
                outline: true,
                outlineColor: Cesium.Color.fromCssColorString(zone.color || '#ff0055'),
                outlineWidth: 2,
                extrudedHeight: 3500
            },
            properties: zone
        });
    }

    loadInitialZones(zones) {
        this.zonesDataSource.entities.removeAll();
        zones.forEach(z => this.renderZone(z));
    }
}

window.GeofenceDrawer = GeofenceDrawer;
