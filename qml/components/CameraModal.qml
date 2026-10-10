import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: 620
    height: 490
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
    property real camLat: 0.0
    property real camLon: 0.0

    signal flyToStreetRequested(real lat, real lon)

    function open(data) {
        root.camTitle = data.name || "SURVEILLANCE UNIT";
        root.camLocation = data.city || "SECTOR";
        root.camLat = data.latitude || 0.0;
        root.camLon = data.longitude || 0.0;
        root.camCoords = (data.latitude ? data.latitude.toFixed(4) : "0") + ", " + (data.longitude ? data.longitude.toFixed(4) : "0");
        root.camImageUrl = data.image_url ? ("/api/proxy/image?url=" + encodeURIComponent(data.image_url)) : "";
        root.camStreamUrl = data.stream_url || "";
        root.visible = true;
    }

    Column {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 10

        // Header
        Item {
            width: parent.width
            height: 24

            Text {
                text: "LIVE SURVEILLANCE FEED // CLASSIFIED"
                color: "#00f0ff"
                font.bold: true
                font.pixelSize: 11
                font.letterSpacing: 1.2
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: "×"
                color: "#94a3b8"
                font.pixelSize: 20
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.visible = false
                }
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: "#3300f0ff"
        }

        // Camera Preview Frame
        Rectangle {
            width: parent.width
            height: 280
            color: "#000000"
            border.color: "#1e293b"
            border.width: 1

            Image {
                id: camImg
                anchors.fill: parent
                fillMode: Image.PreserveAspectFit
                source: root.camImageUrl
                cache: false

                // Auto-refresh snapshot every 5 seconds
                Timer {
                    interval: 5000
                    running: root.visible
                    repeat: true
                    onTriggered: {
                        if (root.camImageUrl) {
                            camImg.source = "";
                            camImg.source = root.camImageUrl + "&t=" + Date.now();
                        }
                    }
                }
            }

            // REC Indicator
            Rectangle {
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.margins: 10
                width: 58
                height: 22
                color: "#99000000"
                radius: 2

                Row {
                    anchors.centerIn: parent
                    spacing: 5
                    Rectangle {
                        width: 7
                        height: 7
                        radius: 3.5
                        color: "#ff0055"
                        anchors.verticalCenter: parent.verticalCenter
                        SequentialAnimation on opacity {
                            loops: Animation.Infinite
                            PropertyAnimation { to: 0.2; duration: 500 }
                            PropertyAnimation { to: 1.0; duration: 500 }
                        }
                    }
                    Text {
                        text: "LIVE"
                        color: "#ff0055"
                        font.bold: true
                        font.pixelSize: 10
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }
        }

        // Camera Metadata Grid
        Grid {
            width: parent.width
            columns: 2
            spacing: 8

            Rectangle {
                width: (parent.width - 8) / 2
                height: 28
                color: "#08ffffff"
                Row {
                    anchors.centerIn: parent
                    spacing: 6
                    Text { text: "UNIT:"; color: "#64748b"; font.pixelSize: 10 }
                    Text { text: root.camTitle; color: "#00f0ff"; font.bold: true; font.pixelSize: 10; elide: Text.ElideRight }
                }
            }

            Rectangle {
                width: (parent.width - 8) / 2
                height: 28
                color: "#08ffffff"
                Row {
                    anchors.centerIn: parent
                    spacing: 6
                    Text { text: "SECTOR:"; color: "#64748b"; font.pixelSize: 10 }
                    Text { text: root.camLocation; color: "#e2e8f0"; font.pixelSize: 10; elide: Text.ElideRight }
                }
            }

            Rectangle {
                width: (parent.width - 8) / 2
                height: 28
                color: "#08ffffff"
                Row {
                    anchors.centerIn: parent
                    spacing: 6
                    Text { text: "COORDS:"; color: "#64748b"; font.pixelSize: 10 }
                    Text { text: root.camCoords; color: "#10b981"; font.bold: true; font.pixelSize: 10 }
                }
            }

            Rectangle {
                width: (parent.width - 8) / 2
                height: 28
                color: "#08ffffff"
                Row {
                    anchors.centerIn: parent
                    spacing: 6
                    Text { text: "STATUS:"; color: "#64748b"; font.pixelSize: 10 }
                    Text { text: "STREAMING"; color: "#10b981"; font.bold: true; font.pixelSize: 10 }
                }
            }
        }

        // Action Toolbar
        Row {
            width: parent.width
            spacing: 10

            Rectangle {
                width: (parent.width - 20) / 3
                height: 32
                color: btnRef.containsMouse ? "#3300f0ff" : "#1a00f0ff"
                border.color: "#00f0ff"
                border.width: 1
                radius: 2

                Text {
                    anchors.centerIn: parent
                    text: "⟳ REFRESH FEED"
                    color: "#00f0ff"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                }

                MouseArea {
                    id: btnRef
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (root.camImageUrl) {
                            camImg.source = "";
                            camImg.source = root.camImageUrl + "&t=" + Date.now();
                        }
                    }
                }
            }

            Rectangle {
                width: (parent.width - 20) / 3
                height: 32
                color: btnStreet.containsMouse ? "#3310b981" : "#1a10b981"
                border.color: "#10b981"
                border.width: 1
                radius: 2

                Text {
                    anchors.centerIn: parent
                    text: "🎯 3D STREET VIEW"
                    color: "#10b981"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                }

                MouseArea {
                    id: btnStreet
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.flyToStreetRequested(root.camLat, root.camLon);
                    }
                }
            }

            Rectangle {
                width: (parent.width - 20) / 3
                height: 32
                color: btnCloseFeed.containsMouse ? "#33ffffff" : "#0dffffff"
                border.color: "#334155"
                border.width: 1
                radius: 2

                Text {
                    anchors.centerIn: parent
                    text: "DISMISS"
                    color: "#94a3b8"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                }

                MouseArea {
                    id: btnCloseFeed
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.visible = false
                }
            }
        }
    }
}
