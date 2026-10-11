/**
 * MAVEN Screen-Space AI Detection Mesh & Target Recognition Overlay
 * Projects real-time military ATR (Automated Target Recognition) bounding brackets
 * and telemetry tags onto tracked aircraft, maritime vessels, and orbital contacts.
 */

class TacticalDetectionMesh {
    constructor(viewer) {
        this.viewer = viewer;
        this.enabled = false;
        this.canvas = null;
        this.ctx = null;
        this.active = false;
        this.animFrameId = null;

        this._initCanvas();
        this._bindKeyEvents();
    }

    _initCanvas() {
        const container = document.getElementById('cesiumContainer') || document.body;
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'detectionMeshCanvas';
        this.canvas.style.position = 'absolute';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.pointerEvents = 'none'; // Click-through to Cesium
        this.canvas.style.zIndex = '50';
        this.canvas.style.display = 'none';

        container.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');

        this._resize();
        window.addEventListener('resize', () => this._resize());
    }

    _resize() {
        if (!this.canvas) return;
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    _bindKeyEvents() {
        window.addEventListener('keydown', (e) => {
            // Hotkey 'D' or 'd' toggles ATR Detection Mesh
            if (e.key === 'd' || e.key === 'D') {
                if (!['input', 'textarea'].includes(document.activeElement.tagName.toLowerCase())) {
                    this.toggle();
                }
            }
        });
    }

    toggle() {
        this.enabled = !this.enabled;
        this.canvas.style.display = this.enabled ? 'block' : 'none';

        if (window.tacticalSound) {
            window.tacticalSound.playClick();
        }

        if (this.enabled) {
            this._startRenderLoop();
        } else {
            this._stopRenderLoop();
            this._clear();
        }

        console.log(`ATR Detection Mesh: ${this.enabled ? 'ACTIVE' : 'STANDBY'}`);
        return this.enabled;
    }

    _startRenderLoop() {
        if (this.active) return;
        this.active = true;

        const render = () => {
            if (!this.enabled) {
                this.active = false;
                return;
            }

            this._drawDetections();
            this.animFrameId = requestAnimationFrame(render);
        };

        this.animFrameId = requestAnimationFrame(render);
    }

    _stopRenderLoop() {
        this.active = false;
        if (this.animFrameId) {
            cancelAnimationFrame(this.animFrameId);
            this.animFrameId = null;
        }
    }

    _clear() {
        if (this.ctx && this.canvas) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    }

    _drawDetections() {
        const scene = this.viewer.scene;
        if (!scene) return;

        this._clear();
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;

        // Collect entities to project
        const entities = [];
        if (window.mavenApp && window.mavenApp.layers) {
            const layers = window.mavenApp.layers;
            // Sample aircraft
            if (layers.flightSource && layers.flightSource.entities) {
                const flValues = layers.flightSource.entities.values;
                const count = Math.min(flValues.length, 60); // Cap to 60 for 60 FPS performance
                for (let i = 0; i < count; i++) {
                    entities.push({ entity: flValues[i], type: 'flight' });
                }
            }

            // Sample vessels
            if (layers.vesselSource && layers.vesselSource.entities) {
                const vsValues = layers.vesselSource.entities.values;
                const count = Math.min(vsValues.length, 30);
                for (let i = 0; i < count; i++) {
                    entities.push({ entity: vsValues[i], type: 'vessel' });
                }
            }

            // Sample satellites
            if (layers.satelliteSource && layers.satelliteSource.entities) {
                layers.satelliteSource.entities.values.forEach(e => {
                    entities.push({ entity: e, type: 'satellite' });
                });
            }
        }

        const now = Cesium.JulianDate.now();
        const scratchCartesian2 = new Cesium.Cartesian2();

        ctx.font = '9px "JetBrains Mono", monospace';
        ctx.textBaseline = 'top';

        for (let i = 0; i < entities.length; i++) {
            const item = entities[i];
            const entity = item.entity;
            if (!entity.position) continue;

            const posCartesian = entity.position.getValue(now);
            if (!posCartesian) continue;

            // Project to screen space
            const screenPos = Cesium.SceneTransforms.wgs84ToWindowCoordinates(scene, posCartesian, scratchCartesian2);
            if (!screenPos) continue;

            const sx = screenPos.x;
            const sy = screenPos.y;

            // Clip offscreen
            if (sx < 20 || sx > width - 20 || sy < 20 || sy > height - 20) continue;

            // Draw Military ATR Corner Brackets
            const boxSize = 22;
            const bracketLen = 6;

            const isEmergency = entity.properties && entity.properties.squawk && entity.properties.squawk.getValue() === '7700';
            const strokeColor = isEmergency ? '#ff0055' : (item.type === 'flight' ? '#00f0ff' : (item.type === 'satellite' ? '#ffd700' : '#10b981'));

            ctx.strokeStyle = strokeColor;
            ctx.fillStyle = strokeColor;
            ctx.lineWidth = 1.2;

            const left = sx - boxSize / 2;
            const top = sy - boxSize / 2;
            const right = sx + boxSize / 2;
            const bottom = sy + boxSize / 2;

            ctx.beginPath();
            // Top-left
            ctx.moveTo(left, top + bracketLen);
            ctx.lineTo(left, top);
            ctx.lineTo(left + bracketLen, top);

            // Top-right
            ctx.moveTo(right - bracketLen, top);
            ctx.lineTo(right, top);
            ctx.lineTo(right, top + bracketLen);

            // Bottom-right
            ctx.moveTo(right, bottom - bracketLen);
            ctx.lineTo(right, bottom);
            ctx.lineTo(right - bracketLen, bottom);

            // Bottom-left
            ctx.moveTo(left + bracketLen, bottom);
            ctx.lineTo(left, bottom);
            ctx.lineTo(left, bottom - bracketLen);
            ctx.stroke();

            // Label tag
            let label = entity.id || 'TGT';
            let sub = '';

            if (entity.properties) {
                const props = entity.properties;
                const cs = props.callsign ? props.callsign.getValue() : null;
                const alt = props.altitude ? props.altitude.getValue() : null;
                const spd = props.velocity_mps ? Math.round(props.velocity_mps.getValue() * 1.94384) : null;

                if (cs) label = cs;
                if (alt) sub = `FL${Math.round(alt / 100 * 3.28084 / 100)}`;
                if (spd) sub += ` ${spd}KT`;
            }

            ctx.fillText(label, right + 4, top - 2);
            if (sub) {
                ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
                ctx.fillText(sub, right + 4, top + 9);
            }
        }
    }
}

window.TacticalDetectionMesh = TacticalDetectionMesh;
