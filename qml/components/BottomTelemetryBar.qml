import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    height: 32
    color: "#e6080c14"
    border.color: "#3300f0ff"
    border.width: 1
    radius: 3

    property string coords: "25.0000° N, 15.0000° E"
    property string altitude: "18000 KM"
    property string heading: "0°"
    property string statusText: "ONLINE"

    Row {
        anchors.centerIn: parent
        spacing: 18

        Row {
            spacing: 5
            Text { text: "COORD:"; color: "#64748b"; font.pixelSize: 10 }
            Text { text: root.coords; color: "#00f0ff"; font.bold: true; font.pixelSize: 10; font.family: "Monospace" }
        }

        Row {
            spacing: 5
            Text { text: "ALT:"; color: "#64748b"; font.pixelSize: 10 }
            Text { text: root.altitude; color: "#38bdf8"; font.bold: true; font.pixelSize: 10; font.family: "Monospace" }
        }

        Row {
            spacing: 5
            Text { text: "HDG:"; color: "#64748b"; font.pixelSize: 10 }
            Text { text: root.heading; color: "#e2e8f0"; font.bold: true; font.pixelSize: 10; font.family: "Monospace" }
        }

        Row {
            spacing: 5
            Text { text: "ENGINE:"; color: "#64748b"; font.pixelSize: 10 }
            Text { text: root.statusText; color: "#10b981"; font.bold: true; font.pixelSize: 10; font.family: "Monospace" }
        }
    }
}
