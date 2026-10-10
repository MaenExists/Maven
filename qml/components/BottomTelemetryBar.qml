import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    height: collapsed ? 22 : 32
    width: collapsed ? 110 : Math.min(parent.width - 32, 560)
    color: "#e6080c14"
    border.color: "#3300f0ff"
    border.width: 1
    radius: 3
    clip: true

    property string coords: "25.0000° N, 15.0000° E"
    property string altitude: "18000 KM"
    property string heading: "0°"
    property string statusText: "ONLINE"
    property bool collapsed: false

    Behavior on height {
        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
    }
    Behavior on width {
        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
    }

    // Collapsed Pill
    Item {
        anchors.fill: parent
        visible: root.collapsed

        Row {
            anchors.centerIn: parent
            spacing: 5
            Text { text: "GEO DATA ▴"; color: "#00f0ff"; font.bold: true; font.pixelSize: 8; font.family: "Monospace" }
        }

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: root.collapsed = false
        }
    }

    // Expanded Readout
    Row {
        anchors.centerIn: parent
        spacing: 14
        visible: !root.collapsed

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

        // Collapse Button
        Text {
            text: "▼"
            color: "#64748b"
            font.pixelSize: 8
            font.bold: true
            anchors.verticalCenter: parent.verticalCenter

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: root.collapsed = true
            }
        }
    }
}
