/**
 * Weather Layer & Particle Effects
 * Renders atmospheric cloud cover and dynamic precipitation particle systems.
 */

class WeatherSimulationLayer {
    constructor(viewer) {
        this.viewer = viewer;
        this.enabled = true;
        this.weatherSource = new Cesium.CustomDataSource('weather_hubs');
        this.viewer.dataSources.add(this.weatherSource);
        this.particleSystem = null;
    }

    updateWeatherGrid(weatherList) {
        if (!this.enabled) return;
        this.weatherSource.entities.removeAll();

        weatherList.forEach(w => {
            const temp = w.temperature_c;
            const wind = w.wind_speed_kmh;
            const dir = w.wind_direction_deg;

            // Weather telemetry label & storm marker
            this.weatherSource.entities.add({
                id: w.id,
                position: Cesium.Cartesian3.fromDegrees(w.longitude, w.latitude, 5000),
                point: {
                    pixelSize: 6,
                    color: Cesium.Color.fromCssColorString('#38bdf8').withAlpha(0.7),
                    outlineColor: Cesium.Color.WHITE,
                    outlineWidth: 1
                },
                label: {
                    text: `${w.name || ''}\n${temp}°C | ${wind} km/h ➔ ${dir}°`,
                    font: '10px "JetBrains Mono", monospace',
                    fillColor: Cesium.Color.fromCssColorString('#bae6fd'),
                    showBackground: true,
                    backgroundColor: Cesium.Color.fromCssColorString('#06090e').withAlpha(0.85),
                    backgroundPadding: new Cesium.Cartesian2(4, 3),
                    pixelOffset: new Cesium.Cartesian2(0, -18)
                },
                properties: w
            });
        });
    }

    toggle(state) {
        this.enabled = state;
        this.weatherSource.show = state;
        if (!state && this.particleSystem) {
            this.viewer.scene.primitives.remove(this.particleSystem);
            this.particleSystem = null;
        }
    }
}

window.WeatherSimulationLayer = WeatherSimulationLayer;
