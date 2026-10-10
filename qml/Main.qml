import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtWebEngine
import "components"

Window {
    id: mainWindow
    width: 1400
    height: 900
    minimumWidth: 800
    minimumHeight: 600
    visible: true
    title: "MAVEN // Planetary Intelligence Operations Center"
    color: "#06090e"

    // Cesium WebGL 3D Globe Viewport
    WebEngineView {
        id: globeWebEngine
        anchors.fill: parent
        url: "http://127.0.0.1:8765/index.html"
        settings.javascriptEnabled: true
        settings.webGLEnabled: true
        settings.localContentCanAccessRemoteUrls: true
        settings.allowRunningInsecureContent: true
    }

    // Top Header Banner
    HeaderBar {
        id: headerBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
    }

    // Top Operational Command Bar
    CommandBar {
        id: commandBar
        anchors.top: headerBar.bottom
        anchors.topMargin: 8
        anchors.horizontalCenter: parent.horizontalCenter
        width: Math.min(parent.width - 32, 780)

        onBasemapClicked: {
            globeWebEngine.runJavaScript("if (window.mavenApp) { var m = window.mavenApp.cycleBasemap(); m; }", function(result) {
                if (result) commandBar.currentBasemap = result.toUpperCase();
            });
        }

        onSunClicked: {
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.toggleSunLighting(); }");
        }

        onBuildingsClicked: {
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.toggle3DBuildings(); }");
        }

        onDrawZoneClicked: {
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.geofenceDrawer.startDrawing(); }");
        }

        onRulerClicked: {
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.measureTool.setMode('distance'); }");
        }

        onAreaClicked: {
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.measureTool.setMode('area'); }");
        }

        onSatDiffClicked: {
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.changeViewer.loadPreset('diff-port-singapore'); }");
        }

        onChokepointClicked: {
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.flyTo(103.80, 1.25, 45000); }");
        }

        onClearClicked: {
            globeWebEngine.runJavaScript("if (window.mavenApp) { if (window.mavenApp.measureTool) window.mavenApp.measureTool.clear(); if (window.mavenApp.changeViewer) window.mavenApp.changeViewer.clear(); }");
        }
    }

    // Left Tactical Sensor Layer Panel
    LayerPanel {
        id: layerPanel
        anchors.top: commandBar.bottom
        anchors.topMargin: 12
        anchors.left: parent.left
        anchors.leftMargin: 16

        onLayerToggled: function(layerId, enabled) {
            if (typeof mavenBridge !== "undefined") {
                mavenBridge.toggleLayer(layerId, enabled);
            }
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.layers.toggleLayer('" + layerId + "', " + enabled + "); }");
        }
    }

    // Tactical Anomaly Alert Ticker
    AnomalyAlertBanner {
        id: alertBanner
        anchors.top: commandBar.bottom
        anchors.topMargin: 12
        anchors.right: parent.right
        anchors.rightMargin: 16
        width: Math.min(380, parent.width * 0.35)

        onAlertClicked: {
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.flyTo(42.60, 13.80, 200000); }");
        }
    }

    // Floating Target Telemetry Card (Right)
    TelemetryCard {
        id: telemetryCard
        anchors.top: alertBanner.bottom
        anchors.topMargin: 12
        anchors.right: parent.right
        anchors.rightMargin: 16

        onFlyToRequested: function(lon, lat, height) {
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.flyTo(" + lon + ", " + lat + ", " + height + "); }");
        }
    }

    // Bottom Telemetry Coordinates & Altitude Bar
    BottomTelemetryBar {
        id: bottomTelemetryBar
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 12
        anchors.horizontalCenter: parent.horizontalCenter
        width: Math.min(parent.width - 32, 540)
    }

    // Live Surveillance Camera Pop-out Modal
    CameraModal {
        id: cameraModal
        anchors.centerIn: parent
    }

    // Periodic camera position polling for native bottom telemetry bar
    Timer {
        interval: 300
        running: true
        repeat: true
        onTriggered: {
            globeWebEngine.runJavaScript("(function() { " +
                "if (!window.mavenApp || !window.mavenApp.viewer) return null; " +
                "var cam = window.mavenApp.viewer.camera; " +
                "var carto = cam.positionCartographic; " +
                "var lon = Cesium.Math.toDegrees(carto.longitude).toFixed(4); " +
                "var lat = Cesium.Math.toDegrees(carto.latitude).toFixed(4); " +
                "var height = (carto.height / 1000).toFixed(0); " +
                "var heading = Cesium.Math.toDegrees(cam.heading).toFixed(0); " +
                "return { lat: lat, lon: lon, height: height, heading: heading }; " +
            "})()", function(data) {
                if (data) {
                    bottomTelemetryBar.coords = data.lat + "° N, " + data.lon + "° E";
                    bottomTelemetryBar.altitude = data.height + " KM";
                    bottomTelemetryBar.heading = data.heading + "°";
                }
            });
        }
    }

    // Bridge signal handlers
    Connections {
        target: mavenBridge
        ignoreUnknownSignals: true

        function onEntitySelected(entityType, entityId, jsonStr) {
            try {
                var data = JSON.parse(jsonStr);
                if (entityType === "live_cam") {
                    cameraModal.open(data);
                } else {
                    telemetryCard.showEntity(data);
                }
            } catch (e) {
                console.error("Error parsing entity JSON:", e);
            }
        }

        function onAlertTriggered(alertId, alertTitle, jsonStr) {
            alertBanner.alertTitle = alertTitle;
            alertBanner.visible = true;
        }
    }
}
