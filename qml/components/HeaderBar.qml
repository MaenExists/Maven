import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root
    height: 52
    color: "#080c14"
    border.color: "rgba(0, 240, 255, 0.3)"
    border.width: 1

    property string threatLevel: "ELEVATED"
    property string utcTime: ""

    Timer {
        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: {
            var now = new Date();
            root.utcTime = now.toUTCString().replace("GMT", "UTC");
        }
    }

    Row {
        anchors.left: parent.left
        anchors.leftMargin: 18
        anchors.verticalCenter: parent.verticalCenter
        spacing: 14

        // Logo / Emblem
        Rectangle {
            width: 28
            height: 28
            color: "transparent"
            border.color: "#00f0ff"
            border.width: 2
            rotation: 45
            anchors.verticalCenter: parent.verticalCenter

            Rectangle {
                anchors.centerIn: parent
                width: 10
                height: 10
                color: "#ff0055"
            }
        }

        Column {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 2

            Text {
                text: "MAVEN // PLANETARY RECONNAISSANCE"
                color: "#ffffff"
                font.bold: true
                font.pixelSize: 14
                font.letterSpacing: 1.5
            }

            Text {
                text: "GLOBAL OSINT & SPATIAL WAR ROOM"
                color: "#00f0ff"
                font.pixelSize: 9
                font.letterSpacing: 1.2
            }
        }
    }

    // Threat Level & Status (Center)
    Rectangle {
        anchors.centerIn: parent
        width: 220
        height: 30
        color: "rgba(255, 0, 85, 0.12)"
        border.color: "#ff0055"
        border.width: 1
        radius: 3

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
                    PropertyAnimation { to: 0.2; duration: 600 }
                    PropertyAnimation { to: 1.0; duration: 600 }
                }
            }

            Text {
                text: "DEFCON / THREAT: " + root.threatLevel
                color: "#ff0055"
                font.bold: true
                font.pixelSize: 11
                font.letterSpacing: 1.0
            }
        }
    }

    // UTC Telemetry Clock (Right)
    Row {
        anchors.right: parent.right
        anchors.rightMargin: 18
        anchors.verticalCenter: parent.verticalCenter
        spacing: 12

        Text {
            text: root.utcTime
            color: "#94a3b8"
            font.pixelSize: 11
            font.family: "Monospace"
        }

        Rectangle {
            width: 70
            height: 24
            color: "rgba(16, 185, 129, 0.15)"
            border.color: "#10b981"
            border.width: 1
            radius: 2

            Text {
                anchors.centerIn: parent
                text: "ACTIVE"
                color: "#10b981"
                font.bold: true
                font.pixelSize: 10
                font.letterSpacing: 1
            }
        }
    }
}
