import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: 280
    height: collapsed ? 36 : 320
    color: "#e6080c14"
    border.color: "#00f0ff"
    border.width: 1
    radius: 4
    visible: false
    clip: true

    property var entityData: ({})
    property bool collapsed: false
    signal flyToRequested(real lon, real lat, real height)
    signal closed()

    Behavior on height {
        NumberAnimation { duration: 220; easing.type: Easing.OutCubic }
    }

    function showEntity(data) {
        root.entityData = data;
        root.collapsed = false;
        root.visible = true;
    }

    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8

        // Header
        Item {
            width: parent.width
            height: 18

            Row {
                spacing: 6
                anchors.left: parent.left
                anchors.right: headerControls.left
                anchors.rightMargin: 6
                anchors.verticalCenter: parent.verticalCenter
                clip: true

                Rectangle {
                    width: 6
                    height: 6
                    radius: 3
                    color: "#00f0ff"
                    anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                    text: root.collapsed ? ("TARGET: " + (root.entityData.callsign || root.entityData.name || root.entityData.id || "INSPECT")) : "TARGET TELEMETRY"
                    color: "#00f0ff"
                    font.bold: true
                    font.pixelSize: 10
                    font.letterSpacing: 1.1
                    font.family: "Monospace"
                    elide: Text.ElideRight
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            Row {
                id: headerControls
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                spacing: 6

                // Collapse Button
                Rectangle {
                    width: 20
                    height: 18
                    color: btnCollapse.containsMouse ? "#3300f0ff" : "#1a00f0ff"
                    border.color: "#00f0ff"
                    border.width: 1
                    radius: 2

                    Text {
                        anchors.centerIn: parent
                        text: root.collapsed ? "▼" : "▲"
                        color: "#00f0ff"
                        font.pixelSize: 9
                        font.bold: true
                    }

                    MouseArea {
                        id: btnCollapse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.collapsed = !root.collapsed
                    }
                }

                // Close Button
                Rectangle {
                    width: 20
                    height: 18
                    color: btnClose.containsMouse ? "#33ff0055" : "#1aff0055"
                    border.color: "#ff0055"
                    border.width: 1
                    radius: 2

                    Text {
                        anchors.centerIn: parent
                        text: "×"
                        color: "#ff0055"
                        font.pixelSize: 12
                        font.bold: true
                    }

                    MouseArea {
                        id: btnClose
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            root.visible = false;
                            root.closed();
                        }
                    }
                }
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: "#3300f0ff"
            visible: !root.collapsed
        }

        // Details Body (Hidden when collapsed)
        Column {
            width: parent.width
            spacing: 8
            visible: !root.collapsed
            opacity: root.collapsed ? 0.0 : 1.0

            Behavior on opacity {
                NumberAnimation { duration: 180 }
            }

            // Target Name & Type
            Text {
                text: root.entityData.callsign || root.entityData.name || root.entityData.id || "UNKNOWN TARGET"
                color: "#ffffff"
                font.bold: true
                font.pixelSize: 13
                font.family: "Monospace"
                elide: Text.ElideRight
                width: parent.width
            }

            Text {
                text: "TYPE: " + (root.entityData.type || "TARGET").toUpperCase()
                color: "#64748b"
                font.pixelSize: 9
                font.family: "Monospace"
            }

            // Details Grid
            Column {
                width: parent.width
                spacing: 5

                Row {
                    Text { text: "COORDS: "; color: "#64748b"; font.pixelSize: 9; font.family: "Monospace" }
                    Text {
                        text: (root.entityData.latitude ? root.entityData.latitude.toFixed(4) : "0.0") + ", " + 
                              (root.entityData.longitude ? root.entityData.longitude.toFixed(4) : "0.0")
                        color: "#00f0ff"
                        font.pixelSize: 9
                        font.bold: true
                        font.family: "Monospace"
                    }
                }

                Row {
                    Text { text: "SPEED: "; color: "#64748b"; font.pixelSize: 9; font.family: "Monospace" }
                    Text {
                        text: root.entityData.velocity_knots ? (root.entityData.velocity_knots + " KTS") : 
                              (root.entityData.speed_knots ? (root.entityData.speed_knots + " KTS") : "N/A")
                        color: "#10b981"
                        font.pixelSize: 9
                        font.bold: true
                        font.family: "Monospace"
                    }
                }

                Row {
                    Text { text: "ALTITUDE: "; color: "#64748b"; font.pixelSize: 9; font.family: "Monospace" }
                    Text {
                        text: root.entityData.altitude ? (root.entityData.altitude.toFixed(0) + " M") : "SURFACE"
                        color: "#f59e0b"
                        font.pixelSize: 9
                        font.family: "Monospace"
                    }
                }

                Row {
                    Text { text: "HEADING: "; color: "#64748b"; font.pixelSize: 9; font.family: "Monospace" }
                    Text {
                        text: root.entityData.heading ? (root.entityData.heading.toFixed(0) + "°") : "0°"
                        color: "#e2e8f0"
                        font.pixelSize: 9
                        font.family: "Monospace"
                    }
                }

                Row {
                    Text { text: "STATUS / SQUAWK: "; color: "#64748b"; font.pixelSize: 9; font.family: "Monospace" }
                    Text {
                        text: root.entityData.squawk || root.entityData.status || "NORMAL"
                        color: (root.entityData.squawk === "7700") ? "#ff0055" : "#10b981"
                        font.pixelSize: 9
                        font.bold: true
                        font.family: "Monospace"
                    }
                }
            }

            // Action Button
            Rectangle {
                width: parent.width
                height: 30
                color: btnIntercept.containsMouse ? "#4000f0ff" : "#1a00f0ff"
                border.color: "#00f0ff"
                border.width: 1
                radius: 2

                Text {
                    anchors.centerIn: parent
                    text: "🎯 INTERCEPT & FLY TO"
                    color: "#00f0ff"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                }

                MouseArea {
                    id: btnIntercept
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (root.entityData.longitude && root.entityData.latitude) {
                            root.flyToRequested(root.entityData.longitude, root.entityData.latitude, 25000.0);
                        }
                    }
                }
            }
        }
    }
}
