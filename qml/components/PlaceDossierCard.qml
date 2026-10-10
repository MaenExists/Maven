import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    width: 390
    height: Math.min(620, parent.height - 180)
    color: "#f2080c16"
    border.color: "#00f0ff"
    border.width: 1
    radius: 4
    visible: false
    clip: true

    property string placeName: ""
    property real placeLat: 0.0
    property real placeLon: 0.0
    property string placeDescription: ""
    property string placeSummary: ""
    property string placeThumbnail: ""
    property var placeWeather: ({})
    property var placeCameras: []
    property var placeContext: ({})
    property bool isLoading: false

    signal cameraSelected(var camData)
    signal groundPerspectiveRequested(real lat, real lon)
    signal orbitPerspectiveRequested(real lat, real lon)
    signal closeRequested()

    function loadDossier(name, lat, lon, displayName) {
        root.placeName = name || "TARGET SECTOR";
        root.placeLat = lat;
        root.placeLon = lon;
        root.placeDescription = displayName || "";
        root.placeSummary = "Compiling tactical intelligence dossier for sector...";
        root.placeThumbnail = "";
        root.placeCameras = [];
        root.placeWeather = {};
        root.placeContext = {};
        root.isLoading = true;
        root.visible = true;

        var xhr = new XMLHttpRequest();
        var url = "http://127.0.0.1:8765/api/intel/dossier?lat=" + lat + "&lon=" + lon + "&name=" + encodeURIComponent(name);
        xhr.open("GET", url);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                root.isLoading = false;
                if (xhr.status === 200) {
                    try {
                        var data = JSON.parse(xhr.responseText);
                        root.placeDescription = data.description || displayName;
                        root.placeSummary = data.summary || "No active intelligence extract available.";
                        root.placeThumbnail = data.thumbnail_url ? ("/api/proxy/image?url=" + encodeURIComponent(data.thumbnail_url)) : "";
                        root.placeWeather = data.weather || {};
                        root.placeCameras = data.cameras || [];
                        root.placeContext = data.tactical_context || {};
                    } catch (e) {
                        console.error("Error parsing dossier:", e);
                    }
                }
            }
        };
        xhr.send();
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        // Header Bar
        RowLayout {
            Layout.fillWidth: true
            height: 24

            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: root.isLoading ? "#ff0055" : "#10b981"
                Layout.alignment: Qt.AlignVCenter

                SequentialAnimation on opacity {
                    running: root.isLoading
                    loops: Animation.Infinite
                    PropertyAnimation { to: 0.2; duration: 400 }
                    PropertyAnimation { to: 1.0; duration: 400 }
                }
            }

            Text {
                text: "DOSSIER // SECTOR RECON"
                color: "#00f0ff"
                font.bold: true
                font.pixelSize: 11
                font.family: "Monospace"
                font.letterSpacing: 1.1
                Layout.alignment: Qt.AlignVCenter
            }

            Item { Layout.fillWidth: true }

            Text {
                text: "×"
                color: "#94a3b8"
                font.pixelSize: 20
                Layout.alignment: Qt.AlignVCenter

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.visible = false;
                        root.closeRequested();
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: "#3300f0ff"
        }

        // Scrollable Dossier Content
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            ColumnLayout {
                width: parent.width
                spacing: 10

                // Satellite / Sector Thumbnail
                Rectangle {
                    Layout.fillWidth: true
                    height: 120
                    color: "#050810"
                    border.color: "#1e293b"
                    border.width: 1
                    visible: root.placeThumbnail.length > 0

                    Image {
                        anchors.fill: parent
                        source: root.placeThumbnail
                        fillMode: Image.PreserveAspectCrop
                        cache: true
                    }

                    // Tactical HUD Overlays
                    Rectangle {
                        anchors.top: parent.top
                        anchors.left: parent.left
                        anchors.margins: 6
                        width: 48
                        height: 16
                        color: "#cc000000"
                        radius: 2
                        Text {
                            anchors.centerIn: parent
                            text: "OPTICAL"
                            color: "#00f0ff"
                            font.pixelSize: 8
                            font.bold: true
                            font.family: "Monospace"
                        }
                    }

                    // Crosshair Corners
                    Rectangle { width: 8; height: 1; color: "#00f0ff"; anchors.left: parent.left; anchors.top: parent.top }
                    Rectangle { width: 1; height: 8; color: "#00f0ff"; anchors.left: parent.left; anchors.top: parent.top }
                    Rectangle { width: 8; height: 1; color: "#00f0ff"; anchors.right: parent.right; anchors.bottom: parent.bottom }
                    Rectangle { width: 1; height: 8; color: "#00f0ff"; anchors.right: parent.right; anchors.bottom: parent.bottom }
                }

                // Place Title & Geodetics
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: root.placeName
                        color: "#ffffff"
                        font.bold: true
                        font.pixelSize: 15
                        font.family: "Monospace"
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }

                    Text {
                        text: root.placeDescription
                        color: "#94a3b8"
                        font.pixelSize: 10
                        font.family: "Monospace"
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }

                    Row {
                        spacing: 8
                        Text {
                            text: "COORD: " + root.placeLat.toFixed(4) + "° N, " + root.placeLon.toFixed(4) + "° E"
                            color: "#10b981"
                            font.bold: true
                            font.pixelSize: 10
                            font.family: "Monospace"
                        }
                    }
                }

                // Intelligence Extract
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: intelText.implicitHeight + 12
                    color: "#0dffffff"
                    border.color: "#1e293b"
                    border.width: 1
                    radius: 2

                    Text {
                        id: intelText
                        anchors.fill: parent
                        anchors.margins: 8
                        text: root.placeSummary
                        color: "#cbd5e1"
                        font.pixelSize: 10
                        lineHeight: 1.25
                        wrapMode: Text.WordWrap
                    }
                }

                // Telemetry & Environment Grid
                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    rowSpacing: 4
                    columnSpacing: 6

                    // Weather
                    Rectangle {
                        Layout.fillWidth: true
                        height: 38
                        color: "#08ffffff"
                        border.color: "#1e293b"
                        border.width: 1
                        Column {
                            anchors.centerIn: parent
                            spacing: 1
                            Text { text: "ATMOSPHERE"; color: "#64748b"; font.pixelSize: 8; font.family: "Monospace"; anchors.horizontalCenter: parent.horizontalCenter }
                            Text {
                                text: (root.placeWeather.temperature_c !== undefined ? (root.placeWeather.temperature_c.toFixed(1) + "°C") : "20.0°C") + " // " +
                                      (root.placeWeather.wind_speed_kmh !== undefined ? (root.placeWeather.wind_speed_kmh.toFixed(0) + " KM/H") : "15 KM/H")
                                color: "#00f0ff"
                                font.bold: true
                                font.pixelSize: 10
                                font.family: "Monospace"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }

                    // Airspace Presence
                    Rectangle {
                        Layout.fillWidth: true
                        height: 38
                        color: "#08ffffff"
                        border.color: "#1e293b"
                        border.width: 1
                        Column {
                            anchors.centerIn: parent
                            spacing: 1
                            Text { text: "AIRSPACE PRESENCE"; color: "#64748b"; font.pixelSize: 8; font.family: "Monospace"; anchors.horizontalCenter: parent.horizontalCenter }
                            Text {
                                text: (root.placeContext.flights_in_sector !== undefined ? root.placeContext.flights_in_sector : 0) + " FLIGHTS IN SECTOR"
                                color: "#10b981"
                                font.bold: true
                                font.pixelSize: 10
                                font.family: "Monospace"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }

                    // Maritime Presence
                    Rectangle {
                        Layout.fillWidth: true
                        height: 38
                        color: "#08ffffff"
                        border.color: "#1e293b"
                        border.width: 1
                        Column {
                            anchors.centerIn: parent
                            spacing: 1
                            Text { text: "MARITIME PRESENCE"; color: "#64748b"; font.pixelSize: 8; font.family: "Monospace"; anchors.horizontalCenter: parent.horizontalCenter }
                            Text {
                                text: (root.placeContext.vessels_in_sector !== undefined ? root.placeContext.vessels_in_sector : 0) + " VESSELS IN SECTOR"
                                color: "#00f0ff"
                                font.bold: true
                                font.pixelSize: 10
                                font.family: "Monospace"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }

                    // Seismic / Hazard Status
                    Rectangle {
                        Layout.fillWidth: true
                        height: 38
                        color: "#08ffffff"
                        border.color: "#1e293b"
                        border.width: 1
                        Column {
                            anchors.centerIn: parent
                            spacing: 1
                            Text { text: "SEISMIC STATUS"; color: "#64748b"; font.pixelSize: 8; font.family: "Monospace"; anchors.horizontalCenter: parent.horizontalCenter }
                            Text {
                                text: root.placeContext.seismic_hazard ? ("M" + root.placeContext.seismic_hazard.magnitude + " (" + root.placeContext.seismic_hazard.distance_km + " KM)") : "NOMINAL // NO HAZARD"
                                color: root.placeContext.seismic_hazard ? "#ff0055" : "#10b981"
                                font.bold: true
                                font.pixelSize: 9
                                font.family: "Monospace"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }
                }

                // Live Street & CCTV Feeds Section
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 6

                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            text: "SURVEILLANCE & STREET CAMERAS"
                            color: "#00f0ff"
                            font.bold: true
                            font.pixelSize: 10
                            font.family: "Monospace"
                            Layout.fillWidth: true
                        }
                        Text {
                            text: root.placeCameras.length + " ACTIVE SENSORS"
                            color: "#10b981"
                            font.pixelSize: 9
                            font.family: "Monospace"
                        }
                    }

                    // Primary Live Street View Button
                    Rectangle {
                        Layout.fillWidth: true
                        height: 36
                        color: btnStreetConnect.containsMouse ? "#40ff0055" : "#26ff0055"
                        border.color: "#ff0055"
                        border.width: 1
                        radius: 3
                        visible: root.placeCameras.length > 0

                        Row {
                            anchors.centerIn: parent
                            spacing: 8
                            Rectangle {
                                width: 8
                                height: 8
                                radius: 4
                                color: "#ff0055"
                                anchors.verticalCenter: parent.verticalCenter
                                SequentialAnimation on opacity {
                                    loops: Animation.Infinite
                                    PropertyAnimation { to: 0.2; duration: 400 }
                                    PropertyAnimation { to: 1.0; duration: 400 }
                                }
                            }
                            Text {
                                text: "CONNECT TO LIVE STREET VIEW (" + (root.placeCameras[0] ? root.placeCameras[0].distance_km : 0) + " KM)"
                                color: "#ffffff"
                                font.bold: true
                                font.pixelSize: 10
                                font.family: "Monospace"
                                font.letterSpacing: 0.8
                                anchors.verticalCenter: parent.verticalCenter
                            }
                        }

                        MouseArea {
                            id: btnStreetConnect
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (root.placeCameras.length > 0) {
                                    root.cameraSelected(root.placeCameras[0]);
                                }
                            }
                        }
                    }

                    // List of Nearby Cameras
                    Repeater {
                        model: root.placeCameras.slice(0, 3)
                        delegate: Rectangle {
                            Layout.fillWidth: true
                            height: 36
                            color: camItemMouse.containsMouse ? "#2600f0ff" : "#0dffffff"
                            border.color: "#1e293b"
                            border.width: 1
                            radius: 2

                            RowLayout {
                                anchors.fill: parent
                                anchors.margins: 4
                                spacing: 8

                                Image {
                                    width: 40
                                    height: 28
                                    fillMode: Image.PreserveAspectCrop
                                    source: modelData.image_url ? ("/api/proxy/image?url=" + encodeURIComponent(modelData.image_url)) : ""
                                    cache: true
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 1
                                    Text {
                                        text: modelData.name || "SURVEILLANCE UNIT"
                                        color: "#ffffff"
                                        font.bold: true
                                        font.pixelSize: 9
                                        font.family: "Monospace"
                                        elide: Text.ElideRight
                                        Layout.fillWidth: true
                                    }
                                    Text {
                                        text: (modelData.distance_km !== undefined ? (modelData.distance_km + " KM") : "") + " // " + (modelData.direction || "Overview")
                                        color: "#64748b"
                                        font.pixelSize: 8
                                        font.family: "Monospace"
                                    }
                                }

                                Rectangle {
                                    width: 52
                                    height: 20
                                    color: "#1a00f0ff"
                                    border.color: "#00f0ff"
                                    border.width: 1
                                    radius: 2
                                    Layout.alignment: Qt.AlignVCenter

                                    Text {
                                        anchors.centerIn: parent
                                        text: "VIEW"
                                        color: "#00f0ff"
                                        font.bold: true
                                        font.pixelSize: 8
                                        font.family: "Monospace"
                                    }
                                }
                            }

                            MouseArea {
                                id: camItemMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: root.cameraSelected(modelData)
                            }
                        }
                    }
                }

                // Vantage Viewport Controls
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Rectangle {
                        Layout.fillWidth: true
                        height: 30
                        color: btnGround.containsMouse ? "#3310b981" : "#1a10b981"
                        border.color: "#10b981"
                        border.width: 1
                        radius: 2

                        Text {
                            anchors.centerIn: parent
                            text: "🏙️ GROUND VIEW (500 M)"
                            color: "#10b981"
                            font.bold: true
                            font.pixelSize: 9
                            font.family: "Monospace"
                        }

                        MouseArea {
                            id: btnGround
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.groundPerspectiveRequested(root.placeLat, root.placeLon)
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 30
                        color: btnOrbit.containsMouse ? "#3300f0ff" : "#1a00f0ff"
                        border.color: "#00f0ff"
                        border.width: 1
                        radius: 2

                        Text {
                            anchors.centerIn: parent
                            text: "🛰️ ORBIT (150 KM)"
                            color: "#00f0ff"
                            font.bold: true
                            font.pixelSize: 9
                            font.family: "Monospace"
                        }

                        MouseArea {
                            id: btnOrbit
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: root.orbitPerspectiveRequested(root.placeLat, root.placeLon)
                        }
                    }
                }
            }
        }
    }
}
