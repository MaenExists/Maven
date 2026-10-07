/**
 * Satellite Change Detection Visualizer
 * Renders multi-temporal difference masks and flies camera to monitored target sectors.
 */

class SatelliteChangeViewer {
    constructor(viewer) {
        this.viewer = viewer;
        this.diffDataSource = new Cesium.CustomDataSource('change_detection');
        this.viewer.dataSources.add(this.diffDataSource);
        this.activeDiff = null;
    }

    async loadPreset(presetId) {
        window.tacticalSound.playTargetLock();
        try {
            const resp = await fetch('/api/change-detection/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ preset_id: presetId, threshold: 0.25 })
            });
            const data = await resp.json();
            this.activeDiff = data;
            this.renderChangeMask(data);

            // Fly camera to sector
            this.viewer.camera.flyTo({
                destination: Cesium.Cartesian3.fromDegrees(data.center[0], data.center[1], 15000),
                orientation: {
                    heading: Cesium.Math.toRadians(0),
                    pitch: Cesium.Math.toRadians(-65),
                    roll: 0.0
                },
                duration: 2.5
            });

            return data;
        } catch (e) {
            console.error('Failed to load change detection preset:', e);
            return null;
        }
    }

    renderChangeMask(diffData) {
        this.diffDataSource.entities.removeAll();

        const positions = diffData.mask_polygon.map(coord => {
            return Cesium.Cartesian3.fromDegrees(coord[0], coord[1]);
        });

        // Pulsing change detection polygon
        this.diffDataSource.entities.add({
            id: 'change-mask-active',
            polygon: {
                hierarchy: new Cesium.PolygonHierarchy(positions),
                material: Cesium.Color.fromCssColorString(diffData.color || '#00f0ff').withAlpha(0.35),
                outline: true,
                outlineColor: Cesium.Color.fromCssColorString(diffData.color || '#00f0ff'),
                outlineWidth: 3,
                heightReference: Cesium.HeightReference.CLAMP_TO_GROUND
            }
        });

        // Tactical sector marker
        this.diffDataSource.entities.add({
            id: 'change-marker-label',
            position: Cesium.Cartesian3.fromDegrees(diffData.center[0], diffData.center[1], 500),
            label: {
                text: `DIFF ANOMALY DETECTED\nTYPE: ${diffData.change_type}\nAREA: ${diffData.detected_area_km2} KM² (+${diffData.change_pct}%)\nCONFIDENCE: 94%`,
                font: '12px "JetBrains Mono", monospace',
                fillColor: Cesium.Color.fromCssColorString('#00f0ff'),
                showBackground: true,
                backgroundColor: Cesium.Color.fromCssColorString('#06090e').withAlpha(0.9),
                backgroundPadding: new Cesium.Cartesian2(8, 6),
                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                pixelOffset: new Cesium.Cartesian2(0, -20)
            }
        });
    }

    clear() {
        this.diffDataSource.entities.removeAll();
        this.activeDiff = null;
    }
}

window.SatelliteChangeViewer = SatelliteChangeViewer;
