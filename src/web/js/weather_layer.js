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

            // Weather atmospheric sensor marker (no permanent clutter label; data visible on hover)
            this.weatherSource.entities.add({
                id: w.id,
                position: Cesium.Cartesian3.fromDegrees(w.longitude, w.latitude, 5000),
                point: {
                    pixelSize: 5,
                    color: Cesium.Color.fromCssColorString('#38bdf8').withAlpha(0.6),
                    outlineColor: Cesium.Color.fromCssColorString('#0284c7'),
                    outlineWidth: 1
                },
                properties: {
                    ...w,
                    type: 'weather',
                    title: `Atmospheric Hub: ${w.name}`,
                    details: `${temp}°C | Wind: ${wind} km/h (${dir}°)`
                }
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
