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

    // Cesium WebEngine 3D Globe Container
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

    // Top Operational Command Bar (Tool Dock)
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
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.measureTool.clear(); window.mavenApp.changeViewer.clear(); }");
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

    // Bridge signal handlers
    Connections {
        target: mavenBridge
        ignoreUnknownSignals: true

        function onEntitySelected(entityType, entityId, jsonStr) {
            try {
                var data = JSON.parse(jsonStr);
                telemetryCard.showEntity(data);
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
