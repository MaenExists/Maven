/**
 * Global Countries & Borders Layer Manager
 * Renders interactive vector country borders, hover highlighting, and territory intelligence inspection.
 */

class CountriesLayerManager {
    constructor(viewer) {
        this.viewer = viewer;
        this.dataSource = new Cesium.CustomDataSource('countries');
        this.enabled = true;
        this.hoveredEntity = null;
        this.selectedEntity = null;
        this.countryList = [];

        this._loadCountries();
    }

    async _loadCountries() {
        try {
            const resp = await fetch('/data/countries_110m.geojson');
            const geojson = await resp.json();

            const geoJsonSource = await Cesium.GeoJsonDataSource.load(geojson, {
                stroke: Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.55),
                fill: Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.01),
                strokeWidth: 1.5,
                clampToGround: false // Huge performance boost - renders directly on ellipsoid
            });

            this.viewer.dataSources.add(geoJsonSource);
            this.geoJsonSource = geoJsonSource;

            const features = geojson.features || [];
            const entities = geoJsonSource.entities.values;
            for (let i = 0; i < entities.length; i++) {
                const entity = entities[i];
                const props = entity.properties;
                const name = (props && props.NAME) ? props.NAME.getValue() : (entity.name || 'Territory');
                const continent = (props && props.CONTINENT) ? props.CONTINENT.getValue() : 'Global';
                const pop = (props && props.POP_EST) ? props.POP_EST.getValue() : 0;
                const iso = (props && props.ISO_A3) ? props.ISO_A3.getValue() : '';

                // Extract approximate centroid for intelligence and camera positioning
                let centerLon = 0.0, centerLat = 0.0;
                const feat = features[i];
                if (feat && feat.geometry && feat.geometry.coordinates) {
                    const coords = feat.geometry.type === 'Polygon' ? feat.geometry.coordinates[0] : (feat.geometry.coordinates[0] ? feat.geometry.coordinates[0][0] : []);
                    if (coords && coords.length > 0) {
                        let sumLon = 0, sumLat = 0;
                        for (let c = 0; c < coords.length; c++) {
                            sumLon += coords[c][0];
                            sumLat += coords[c][1];
                        }
                        centerLon = sumLon / coords.length;
                        centerLat = sumLat / coords.length;
                    }
                }

                entity.customCountryData = {
                    name: name,
                    continent: continent,
                    population: pop,
                    iso: iso,
                    latitude: centerLat,
                    longitude: centerLon,
                    type: 'country'
                };

                if (entity.polygon) {
                    entity.polygon.material = Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.01);
                    entity.polygon.outline = true;
                    entity.polygon.outlineColor = Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.55);
                    entity.polygon.outlineWidth = 1.5;
                }
            }

            console.log(`Loaded ${entities.length} world countries into interactive vector layer`);
        } catch (err) {
            console.warn('Failed to load world countries GeoJSON:', err);
        }
    }

    highlightCountryOnHover(entity) {
        if (this.hoveredEntity === entity) return;

        // Reset previous hovered country (unless it is currently selected)
        if (this.hoveredEntity && this.hoveredEntity !== this.selectedEntity && this.hoveredEntity.polygon) {
            this.hoveredEntity.polygon.material = Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.01);
            this.hoveredEntity.polygon.outlineColor = Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.55);
        }

        this.hoveredEntity = entity;

        if (entity && entity !== this.selectedEntity && entity.polygon) {
            entity.polygon.material = Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.18);
            entity.polygon.outlineColor = Cesium.Color.fromCssColorString('#38bdf8').withAlpha(0.9);
        }
    }

    clearHover() {
        if (this.hoveredEntity && this.hoveredEntity !== this.selectedEntity && this.hoveredEntity.polygon) {
            this.hoveredEntity.polygon.material = Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.01);
            this.hoveredEntity.polygon.outlineColor = Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.55);
        }
        this.hoveredEntity = null;
    }

    selectCountry(entity) {
        // Reset previous selected country
        if (this.selectedEntity && this.selectedEntity.polygon) {
            this.selectedEntity.polygon.material = Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.01);
            this.selectedEntity.polygon.outlineColor = Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.55);
        }

        this.selectedEntity = entity;

        if (entity && entity.polygon) {
            entity.polygon.material = Cesium.Color.fromCssColorString('#00f0ff').withAlpha(0.28);
            entity.polygon.outlineColor = Cesium.Color.fromCssColorString('#ffd700'); // Gold boundary highlight
            entity.polygon.outlineWidth = 2.5;
        }

        return entity ? entity.customCountryData : null;
    }

    toggleBorders(show) {
        this.enabled = (show !== undefined) ? show : !this.enabled;
        if (this.geoJsonSource) {
            this.geoJsonSource.show = this.enabled;
        }
        return this.enabled;
    }
}

window.CountriesLayerManager = CountriesLayerManager;
