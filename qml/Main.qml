import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtWebEngine
import "components"

Window {
    id: mainWindow
    width: 1400
    height: 900
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

    // Left Tactical Sensor Layer Panel
    LayerPanel {
        id: layerPanel
        anchors.top: headerBar.bottom
        anchors.topMargin: 20
        anchors.left: parent.left
        anchors.leftMargin: 20

        onLayerToggled: function(layerId, enabled) {
            if (typeof mavenBridge !== "undefined") {
                mavenBridge.toggleLayer(layerId, enabled);
            }
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.layers.toggleLayer('" + layerId + "', " + enabled + "); }");
        }
    }

    // Top Center Anomaly Alert Ticker
    AnomalyAlertBanner {
        id: alertBanner
        anchors.top: headerBar.bottom
        anchors.topMargin: 16
        anchors.horizontalCenter: parent.horizontalCenter
        onAlertClicked: {
            globeWebEngine.runJavaScript("if (window.mavenApp) { window.mavenApp.flyTo(42.60, 13.80, 200000); }");
        }
    }

    // Floating Target Telemetry Card (Right)
    TelemetryCard {
        id: telemetryCard
        anchors.top: headerBar.bottom
        anchors.topMargin: 20
        anchors.right: parent.right
        anchors.rightMargin: 20

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
