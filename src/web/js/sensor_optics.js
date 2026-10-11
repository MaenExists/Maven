/**
 * MAVEN Tactical Sensor Optics Engine
 * Full-screen GLSL post-processing stages for military and intelligence sensor modes:
 * - VISUAL (Normal photorealistic satellite)
 * - NVG (Night Vision Goggles - P43 green phosphor, noise, vignette, scanlines)
 * - FLIR (Forward Looking Infrared - Ironbow thermography heat mapping)
 * - CRT (Tactical C2 Command Display - chromatic aberration, raster scanlines)
 * - NOIR (High-contrast monochromatic orbital reconnaissance)
 */

class TacticalSensorOptics {
    constructor(viewer) {
        this.viewer = viewer;
        this.currentMode = 'VISUAL';
        this.stages = {};

        this._initStages();
    }

    _initStages() {
        const scene = this.viewer.scene;
        if (!scene || !scene.postProcessStages) return;

        // 1. NVG Stage (Night Vision Goggles)
        const nvgShader = `
            uniform sampler2D colorTexture;
            varying vec2 v_textureCoordinates;

            void main() {
                vec4 color = texture2D(colorTexture, v_textureCoordinates);
                vec2 uv = v_textureCoordinates;

                // Luminance calculation
                float lum = dot(color.rgb, vec3(0.299, 0.587, 0.114));

                // Military lens vignette (circular scope)
                vec2 center = vec2(0.5, 0.5);
                float dist = distance(uv, center);
                float vignette = smoothstep(0.72, 0.28, dist);

                // Phosphor scanline texture
                float scanline = sin(uv.y * 1100.0) * 0.07;

                // Military P43 Green Phosphor tint with amplified gain
                vec3 nvg = vec3(0.06, lum * 1.48, 0.16) + scanline;
                nvg *= vignette;

                gl_FragColor = vec4(nvg, color.a);
            }
        `;

        // 2. FLIR Stage (Forward Looking Infrared / Ironbow Thermal)
        const flirShader = `
            uniform sampler2D colorTexture;
            varying vec2 v_textureCoordinates;

            vec3 flirPalette(float t) {
                t = clamp(t, 0.0, 1.0);
                vec3 c1 = vec3(0.05, 0.05, 0.25); // Deep cold navy
                vec3 c2 = vec3(0.55, 0.05, 0.65); // Thermal magenta
                vec3 c3 = vec3(0.95, 0.35, 0.05); // Hot orange
                vec3 c4 = vec3(1.00, 0.95, 0.20); // Hot yellow
                vec3 c5 = vec3(1.00, 1.00, 1.00); // White-hot core
                
                if (t < 0.25) return mix(c1, c2, t * 4.0);
                if (t < 0.50) return mix(c2, c3, (t - 0.25) * 4.0);
                if (t < 0.75) return mix(c3, c4, (t - 0.50) * 4.0);
                return mix(c4, c5, (t - 0.75) * 4.0);
            }

            void main() {
                vec4 color = texture2D(colorTexture, v_textureCoordinates);
                float lum = dot(color.rgb, vec3(0.299, 0.587, 0.114));

                // Dynamic thermal curve emphasizing heat signatures
                float heat = pow(lum, 1.22);
                vec3 thermal = flirPalette(heat);

                gl_FragColor = vec4(thermal, color.a);
            }
        `;

        // 3. CRT Stage (Surveillance / Tactical Command C2 Display)
        const crtShader = `
            uniform sampler2D colorTexture;
            varying vec2 v_textureCoordinates;

            void main() {
                vec2 uv = v_textureCoordinates;

                // Chromatic aberration (RGB channel divergence)
                vec2 shift = vec2(0.0016, 0.0);
                float r = texture2D(colorTexture, uv - shift).r;
                float g = texture2D(colorTexture, uv).g;
                float b = texture2D(colorTexture, uv + shift).b;
                vec3 col = vec3(r, g, b);

                // Horizontal scanline grid
                float scan = sin(uv.y * 850.0) * 0.10;
                col -= scan;

                // Tactical phosphor grading
                col = mix(col, vec3(col.r * 1.08, col.g * 1.04, col.b * 0.92), 0.35);

                gl_FragColor = vec4(col, 1.0);
            }
        `;

        // 4. NOIR Stage (Reconnaissance Monochromatic High-Contrast)
        const noirShader = `
            uniform sampler2D colorTexture;
            varying vec2 v_textureCoordinates;

            void main() {
                vec4 color = texture2D(colorTexture, v_textureCoordinates);
                float lum = dot(color.rgb, vec3(0.299, 0.587, 0.114));

                // High-pass contrast curve
                float highContrast = smoothstep(0.10, 0.88, lum);
                vec3 noir = vec3(highContrast);

                gl_FragColor = vec4(noir, color.a);
            }
        `;

        try {
            this.stages['NVG'] = new Cesium.PostProcessStage({
                name: 'sensor_optics_nvg',
                fragmentShader: nvgShader
            });
            this.stages['NVG'].enabled = false;
            scene.postProcessStages.add(this.stages['NVG']);

            this.stages['FLIR'] = new Cesium.PostProcessStage({
                name: 'sensor_optics_flir',
                fragmentShader: flirShader
            });
            this.stages['FLIR'].enabled = false;
            scene.postProcessStages.add(this.stages['FLIR']);

            this.stages['CRT'] = new Cesium.PostProcessStage({
                name: 'sensor_optics_crt',
                fragmentShader: crtShader
            });
            this.stages['CRT'].enabled = false;
            scene.postProcessStages.add(this.stages['CRT']);

            this.stages['NOIR'] = new Cesium.PostProcessStage({
                name: 'sensor_optics_noir',
                fragmentShader: noirShader
            });
            this.stages['NOIR'].enabled = false;
            scene.postProcessStages.add(this.stages['NOIR']);

            console.log('Tactical Sensor Optics post-processing stages initialized.');
        } catch (e) {
            console.warn('Failed to initialize PostProcessStages:', e);
        }
    }

    setMode(mode) {
        mode = (mode || 'VISUAL').toUpperCase();
        this.currentMode = mode;

        // Disable all stages first
        Object.keys(this.stages).forEach(k => {
            if (this.stages[k]) this.stages[k].enabled = false;
        });

        // Enable target stage if not default visual
        if (this.stages[mode]) {
            this.stages[mode].enabled = true;
        }

        if (window.tacticalSound) {
            window.tacticalSound.playClick();
        }

        console.log(`Sensor optics switched to: ${mode}`);
        return this.currentMode;
    }

    cycleMode() {
        const modes = ['VISUAL', 'NVG', 'FLIR', 'CRT', 'NOIR'];
        const nextIdx = (modes.indexOf(this.currentMode) + 1) % modes.length;
        return this.setMode(modes[nextIdx]);
    }
}

window.TacticalSensorOptics = TacticalSensorOptics;
