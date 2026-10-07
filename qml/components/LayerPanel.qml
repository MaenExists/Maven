import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: 220
    height: 380
    color: "#080c14"
    border.color: "#4000f0ff"
    border.width: 1
    radius: 4

    signal layerToggled(string layerId, bool enabled)

    Column {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 10

        Text {
            text: "TACTICAL SENSORS"
            color: "#00f0ff"
            font.bold: true
            font.pixelSize: 11
            font.letterSpacing: 1.5
        }

        Rectangle {
            width: parent.width
            height: 1
            color: "#3300f0ff"
        }

        // Layer rows
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
                color: "#08ffffff"
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
                    anchors.fill: parent
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
