import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    width: 280
    height: 320
    color: "#080c14"
    border.color: "#00f0ff"
    border.width: 1
    radius: 4
    visible: false

    property var entityData: ({})
    signal flyToRequested(real lon, real lat, real height)
    signal closed()

    function showEntity(data) {
        root.entityData = data;
        root.visible = true;
    }

    Column {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 10

        // Header
        Row {
            width: parent.width
            Text {
                text: "TARGET TELEMETRY"
                color: "#00f0ff"
                font.bold: true
                font.pixelSize: 11
                font.letterSpacing: 1.2
            }
            Item { width: 1; height: 1; Layout.fillWidth: true }
            Text {
                text: "×"
                color: "#94a3b8"
                font.pixelSize: 16
                anchors.right: parent.right
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.visible = false;
                        root.closed();
                    }
                }
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: "rgba(0, 240, 255, 0.2)"
        }

        // Target Name & Type
        Text {
            text: root.entityData.callsign || root.entityData.name || root.entityData.id || "UNKNOWN TARGET"
            color: "#ffffff"
            font.bold: true
            font.pixelSize: 14
            elide: Text.ElideRight
            width: parent.width
        }

        Text {
            text: "TYPE: " + (root.entityData.type || "TARGET").toUpperCase()
            color: "#64748b"
            font.pixelSize: 10
        }

        // Details Grid
        Column {
            width: parent.width
            spacing: 6

            Row {
                Text { text: "COORDS: "; color: "#64748b"; font.pixelSize: 10 }
                Text {
                    text: (root.entityData.latitude ? root.entityData.latitude.toFixed(4) : "0.0") + ", " + 
                          (root.entityData.longitude ? root.entityData.longitude.toFixed(4) : "0.0")
                    color: "#00f0ff"
                    font.pixelSize: 10
                    font.bold: true
                }
            }

            Row {
                Text { text: "SPEED: "; color: "#64748b"; font.pixelSize: 10 }
                Text {
                    text: root.entityData.velocity_knots ? (root.entityData.velocity_knots + " KTS") : 
                          (root.entityData.speed_knots ? (root.entityData.speed_knots + " KTS") : "N/A")
                    color: "#10b981"
                    font.pixelSize: 10
                    font.bold: true
                }
            }

            Row {
                Text { text: "ALTITUDE: "; color: "#64748b"; font.pixelSize: 10 }
                Text {
                    text: root.entityData.altitude ? (root.entityData.altitude.toFixed(0) + " M") : "SURFACE"
                    color: "#f59e0b"
                    font.pixelSize: 10
                }
            }

            Row {
                Text { text: "HEADING: "; color: "#64748b"; font.pixelSize: 10 }
                Text {
                    text: root.entityData.heading ? (root.entityData.heading.toFixed(0) + "°") : "0°"
                    color: "#e2e8f0"
                    font.pixelSize: 10
                }
            }

            Row {
                Text { text: "STATUS / SQUAWK: "; color: "#64748b"; font.pixelSize: 10 }
                Text {
                    text: root.entityData.squawk || root.entityData.status || "NORMAL"
                    color: (root.entityData.squawk === "7700") ? "#ff0055" : "#10b981"
                    font.pixelSize: 10
                    font.bold: true
                }
            }
        }

        // Action Buttons
        Button {
            width: parent.width
            height: 32
            text: "INTERCEPT & FLY TO"
            contentItem: Text {
                text: parent.text
                color: "#00f0ff"
                font.bold: true
                font.pixelSize: 10
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            background: Rectangle {
                color: "rgba(0, 240, 255, 0.15)"
                border.color: "#00f0ff"
                border.width: 1
                radius: 2
            }
            onClicked: {
                if (root.entityData.longitude && root.entityData.latitude) {
                    root.flyToRequested(root.entityData.longitude, root.entityData.latitude, 25000.0);
                }
            }
        }
    }
}
