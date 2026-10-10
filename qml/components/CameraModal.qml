import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebEngine

Rectangle {
    id: root
    width: Math.min(parent.width - 40, 780)
    height: Math.min(parent.height - 50, 560)
    color: "#0a0f18"
    border.color: "#00f0ff"
    border.width: 1
    radius: 4
    visible: false

    property string camTitle: "SURVEILLANCE UNIT"
    property string camLocation: "METROPOLITAN SECTOR"
    property string camCoords: "51.5074, -0.1278"
    property string camImageUrl: ""
    property string camStreamUrl: ""
    property string camStreamType: "video"
    property real camLat: 0.0
    property real camLon: 0.0

    signal flyToStreetRequested(real lat, real lon)

    function open(data) {
        root.camTitle = data.name || "SURVEILLANCE UNIT";
        root.camLocation = data.city || "SECTOR";
        root.camLat = data.latitude || 0.0;
        root.camLon = data.longitude || 0.0;
        root.camCoords = (data.latitude ? data.latitude.toFixed(4) : "0") + ", " + (data.longitude ? data.longitude.toFixed(4) : "0");
        root.camImageUrl = data.image_url || "";
        root.camStreamUrl = data.stream_url || data.image_url || "";
        root.camStreamType = data.stream_type || (root.camStreamUrl.indexOf("youtube") !== -1 ? "youtube" : (root.camStreamUrl.indexOf(".m3u8") !== -1 ? "hls" : "video"));

        var query = "url=" + encodeURIComponent(root.camStreamUrl) +
                    "&type=" + encodeURIComponent(root.camStreamType) +
                    "&name=" + encodeURIComponent(root.camTitle) +
                    "&city=" + encodeURIComponent(root.camLocation) +
                    "&lat=" + root.camLat.toFixed(4) +
                    "&lon=" + root.camLon.toFixed(4) +
                    "&img=" + encodeURIComponent(root.camImageUrl);
        playerWebEngine.url = "http://127.0.0.1:8765/player.html?" + query;
        root.visible = true;
    }

    function close() {
        playerWebEngine.url = "about:blank";
        root.visible = false;
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8

        // Header Bar
        RowLayout {
            Layout.fillWidth: true
            height: 24

            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: "#ff0055"
                Layout.alignment: Qt.AlignVCenter

                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    PropertyAnimation { to: 0.2; duration: 500 }
                    PropertyAnimation { to: 1.0; duration: 500 }
                }
            }

            Text {
                text: "LIVE SURVEILLANCE FEED // CLASSIFIED CCTV DOWNLINK"
                color: "#00f0ff"
                font.bold: true
                font.pixelSize: 11
                font.letterSpacing: 1.2
                font.family: "Monospace"
                Layout.fillWidth: true
            }

            Text {
                text: "×"
                color: "#94a3b8"
                font.pixelSize: 22
                font.bold: true

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.close()
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#3300f0ff"
        }

        // Live CCTV Video Player Frame
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#000000"
            border.color: "#1e293b"
            border.width: 1
            clip: true

            WebEngineView {
                id: playerWebEngine
                anchors.fill: parent
                settings.javascriptEnabled: true
                settings.webGLEnabled: true
                settings.localContentCanAccessRemoteUrls: true
                settings.allowRunningInsecureContent: true
                settings.playbackRequiresUserGesture: false
            }
        }

        // Metadata Readout Strip
        Rectangle {
            Layout.fillWidth: true
            height: 26
            color: "#08ffffff"
            border.color: "#1e293b"
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 8
                anchors.rightMargin: 8
                spacing: 12

                Row {
                    spacing: 4
                    Text { text: "TARGET:"; color: "#64748b"; font.pixelSize: 9; font.family: "Monospace" }
                    Text { text: root.camTitle; color: "#00f0ff"; font.bold: true; font.pixelSize: 9; font.family: "Monospace"; elide: Text.ElideRight; width: 240 }
                }

                Row {
                    spacing: 4
                    Text { text: "LOC:"; color: "#64748b"; font.pixelSize: 9; font.family: "Monospace" }
                    Text { text: root.camLocation; color: "#e2e8f0"; font.pixelSize: 9; font.family: "Monospace"; elide: Text.ElideRight; width: 180 }
                }

                Row {
                    spacing: 4
                    Text { text: "FIX:"; color: "#64748b"; font.pixelSize: 9; font.family: "Monospace" }
                    Text { text: root.camCoords; color: "#10b981"; font.bold: true; font.pixelSize: 9; font.family: "Monospace" }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: "● 60 FPS HD"
                    color: "#ff0055"
                    font.bold: true
                    font.pixelSize: 9
                    font.family: "Monospace"
                }
            }
        }

        // Action Toolbar
        RowLayout {
            Layout.fillWidth: true
            height: 32
            spacing: 8

            Button {
                id: btnStreet
                Layout.fillWidth: true
                Layout.fillHeight: true
                contentItem: Text {
                    anchors.centerIn: parent
                    text: "🎯 3D STREET VIEW PERSPECTIVE"
                    color: "#10b981"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                }
                background: Rectangle {
                    color: btnStreet.hovered ? "#3310b981" : "#1a10b981"
                    border.color: "#10b981"
                    border.width: 1
                    radius: 2
                }
                onClicked: {
                    root.flyToStreetRequested(root.camLat, root.camLon);
                }
            }

            Button {
                id: btnReconnect
                Layout.preferredWidth: 140
                Layout.fillHeight: true
                contentItem: Text {
                    anchors.centerIn: parent
                    text: "⟳ RECONNECT"
                    color: "#00f0ff"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                }
                background: Rectangle {
                    color: btnReconnect.hovered ? "#3300f0ff" : "#1a00f0ff"
                    border.color: "#00f0ff"
                    border.width: 1
                    radius: 2
                }
                onClicked: {
                    playerWebEngine.reload();
                }
            }

            Button {
                id: btnDismiss
                Layout.preferredWidth: 100
                Layout.fillHeight: true
                contentItem: Text {
                    anchors.centerIn: parent
                    text: "DISMISS"
                    color: "#94a3b8"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                }
                background: Rectangle {
                    color: btnDismiss.hovered ? "#33ffffff" : "#0dffffff"
                    border.color: "#334155"
                    border.width: 1
                    radius: 2
                }
                onClicked: root.close()
            }
        }
    }
}
