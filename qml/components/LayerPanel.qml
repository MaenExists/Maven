import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: 220
    height: collapsed ? 36 : 380
    color: "#e6080c14"
    border.color: collapsed ? "#3300f0ff" : "#4000f0ff"
    border.width: 1
    radius: 4
    clip: true

    property bool collapsed: false
    signal layerToggled(string layerId, bool enabled)

    Behavior on height {
        NumberAnimation { duration: 220; easing.type: Easing.OutCubic }
    }

    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 8

        // Header with Collapse Toggle
        Item {
            width: parent.width
            height: 18

            Row {
                spacing: 6
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter

                Rectangle {
                    width: 6
                    height: 6
                    radius: 3
                    color: "#00f0ff"
                    anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                    text: root.collapsed ? "SENSORS (7 ACTIVE)" : "TACTICAL SENSORS"
                    color: "#00f0ff"
                    font.bold: true
                    font.pixelSize: 10
                    font.letterSpacing: 1.2
                    font.family: "Monospace"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            // Collapse Button
            Rectangle {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                width: 22
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
        }

        Rectangle {
            width: parent.width
            height: 1
            color: "#3300f0ff"
            visible: !root.collapsed
        }

        // Layer rows (Hidden when collapsed)
        Column {
            width: parent.width
            spacing: 6
            visible: !root.collapsed
            opacity: root.collapsed ? 0.0 : 1.0

            Behavior on opacity {
                NumberAnimation { duration: 180 }
            }

            Repeater {
                model: [
                    { id: "flights", name: "AIR RECON (FLIGHTS)", color: "#00f0ff" },
                    { id: "vessels", name: "MARITIME AIS (SHIPS)", color: "#10b981" },
                    { id: "wildfires", name: "THERMAL FRONTS (FIRMS)", color: "#ff4500" },
                    { id: "earthquakes", name: "SEISMIC (USGS)", color: "#f59e0b" },
                    { id: "cameras", name: "STREET CCTV CAMS", color: "#38bdf8" },
                    { id: "conflicts", name: "SECURITY INCIDENTS", color: "#ff0055" },
                    { id: "anomalies", name: "ANOMALY BEACONS", color: "#ff007f" }
                ]

                delegate: Rectangle {
                    width: parent.width
                    height: 32
                    color: itemMouse.containsMouse ? "#1f00f0ff" : "#08ffffff"
                    border.color: activeState ? modelData.color : "transparent"
                    border.width: 1
                    radius: 3

                    property bool activeState: true

                    Row {
                        anchors.fill: parent
                        anchors.margins: 6
                        spacing: 8

                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4
                            color: activeState ? modelData.color : "#475569"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: modelData.name
                            color: activeState ? "#e2e8f0" : "#64748b"
                            font.pixelSize: 10
                            font.bold: activeState
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    MouseArea {
                        id: itemMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            activeState = !activeState;
                            root.layerToggled(modelData.id, activeState);
                        }
                    }
                }
            }
        }
    }
}
