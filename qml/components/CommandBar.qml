import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    height: 38
    color: "#e6080c14"
    border.color: "#4d00f0ff"
    border.width: 1
    radius: 3

    property string currentBasemap: "SATELLITE"

    signal basemapClicked()
    signal sunClicked()
    signal buildingsClicked()
    signal drawZoneClicked()
    signal rulerClicked()
    signal areaClicked()
    signal satDiffClicked()
    signal chokepointClicked()
    signal clearClicked()

    RowLayout {
        anchors.fill: parent
        anchors.margins: 4
        spacing: 6

        // Basemap Switcher
        Button {
            id: btnBasemap
            Layout.fillHeight: true
            contentItem: Row {
                spacing: 5
                anchors.centerIn: parent
                Text { text: "🌍"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                Text {
                    text: root.currentBasemap
                    color: "#00f0ff"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
            background: Rectangle {
                color: btnBasemap.hovered ? "#4000f0ff" : "#1a00f0ff"
                border.color: "#00f0ff"
                border.width: 1
                radius: 2
            }
            onClicked: root.basemapClicked()
        }

        // Sun Lighting
        Button {
            id: btnSun
            Layout.fillHeight: true
            contentItem: Row {
                spacing: 5
                anchors.centerIn: parent
                Text { text: "☀️"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                Text {
                    text: "SUN"
                    color: "#e2e8f0"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
            background: Rectangle {
                color: btnSun.hovered ? "#33ffffff" : "#0dffffff"
                border.color: "#4000f0ff"
                border.width: 1
                radius: 2
            }
            onClicked: root.sunClicked()
        }

        // 3D Buildings
        Button {
            id: btn3D
            Layout.fillHeight: true
            contentItem: Row {
                spacing: 5
                anchors.centerIn: parent
                Text { text: "🏙️"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                Text {
                    text: "3D TILES"
                    color: "#e2e8f0"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
            background: Rectangle {
                color: btn3D.hovered ? "#33ffffff" : "#0dffffff"
                border.color: "#4000f0ff"
                border.width: 1
                radius: 2
            }
            onClicked: root.buildingsClicked()
        }

        // Draw Zone (Geofence)
        Button {
            id: btnZone
            Layout.fillHeight: true
            contentItem: Row {
                spacing: 5
                anchors.centerIn: parent
                Text { text: "🛡️"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                Text {
                    text: "DRAW ZONE"
                    color: "#ff0055"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
            background: Rectangle {
                color: btnZone.hovered ? "#40ff0055" : "#1aff0055"
                border.color: "#ff0055"
                border.width: 1
                radius: 2
            }
            onClicked: root.drawZoneClicked()
        }

        // Distance Ruler
        Button {
            id: btnRuler
            Layout.fillHeight: true
            contentItem: Row {
                spacing: 5
                anchors.centerIn: parent
                Text { text: "📏"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                Text {
                    text: "RULER"
                    color: "#00f0ff"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
            background: Rectangle {
                color: btnRuler.hovered ? "#33ffffff" : "#0dffffff"
                border.color: "#4000f0ff"
                border.width: 1
                radius: 2
            }
            onClicked: root.rulerClicked()
        }

        // Area Polygon
        Button {
            id: btnArea
            Layout.fillHeight: true
            contentItem: Row {
                spacing: 5
                anchors.centerIn: parent
                Text { text: "📐"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                Text {
                    text: "AREA"
                    color: "#00f0ff"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
            background: Rectangle {
                color: btnArea.hovered ? "#33ffffff" : "#0dffffff"
                border.color: "#4000f0ff"
                border.width: 1
                radius: 2
            }
            onClicked: root.areaClicked()
        }

        // Satellite Diff
        Button {
            id: btnSatDiff
            Layout.fillHeight: true
            contentItem: Row {
                spacing: 5
                anchors.centerIn: parent
                Text { text: "🛰️"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                Text {
                    text: "SAT DIFF"
                    color: "#f59e0b"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
            background: Rectangle {
                color: btnSatDiff.hovered ? "#40f59e0b" : "#1af59e0b"
                border.color: "#f59e0b"
                border.width: 1
                radius: 2
            }
            onClicked: root.satDiffClicked()
        }

        // Chokepoint Intercept
        Button {
            id: btnChoke
            Layout.fillHeight: true
            contentItem: Row {
                spacing: 5
                anchors.centerIn: parent
                Text { text: "🎯"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                Text {
                    text: "CHOKEPOINT"
                    color: "#ff0055"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }
            background: Rectangle {
                color: btnChoke.hovered ? "#40ff0055" : "#1aff0055"
                border.color: "#ff0055"
                border.width: 1
                radius: 2
            }
            onClicked: root.chokepointClicked()
        }

        // Clear Tool
        Button {
            id: btnClear
            Layout.fillHeight: true
            contentItem: Text {
                anchors.centerIn: parent
                text: "RESET"
                color: "#94a3b8"
                font.bold: true
                font.pixelSize: 10
                font.family: "Monospace"
            }
            background: Rectangle {
                color: btnClear.hovered ? "#33ffffff" : "#0dffffff"
                border.color: "#334155"
                border.width: 1
                radius: 2
            }
            onClicked: root.clearClicked()
        }
    }
}
