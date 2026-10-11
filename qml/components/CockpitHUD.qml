import QtQuick 2.15
import QtQuick.Controls 2.15

/**
 * Tactical Fighter-Style Cockpit HUD Overlay
 * Provides synthetic airspeed tape, altitude ladder, pitch ladder, heading tape,
 * and target lock reticle during real-time aircraft chase mode.
 */
Item {
    id: root
    visible: active
    anchors.fill: parent

    property bool active: false
    property string targetId: ""
    property string callsign: "TARGET"
    property int altitudeFt: 30000
    property int speedKnots: 450
    property int headingDeg: 90

    signal exitRequested()

    // Top Tactical Header Banner
    Rectangle {
        anchors.top: parent.top
        anchors.topMargin: 56
        anchors.horizontalCenter: parent.horizontalCenter
        width: 440
        height: 32
        color: Qt.rgba(0.02, 0.05, 0.10, 0.88)
        border.color: "#00f0ff"
        border.width: 1
        radius: 4

        Row {
            anchors.centerIn: parent
            spacing: 12

            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: "#10b981"
                anchors.verticalCenter: parent.verticalCenter
                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    PropertyAnimation { to: 0.3; duration: 600 }
                    PropertyAnimation { to: 1.0; duration: 600 }
                }
            }

            Text {
                text: "COCKPIT CHASE ENGAGED // " + root.callsign
                font.family: "JetBrains Mono"
                font.pixelSize: 11
                font.bold: true
                color: "#00f0ff"
                anchors.verticalCenter: parent.verticalCenter
            }

            Text {
                text: "// HDG: " + String(root.headingDeg).padStart(3, '0') + "°"
                font.family: "JetBrains Mono"
                font.pixelSize: 11
                color: "#94a3b8"
                anchors.verticalCenter: parent.verticalCenter
            }
        }
    }

    // Top Heading Compass Tape
    Rectangle {
        anchors.top: parent.top
        anchors.topMargin: 96
        anchors.horizontalCenter: parent.horizontalCenter
        width: 320
        height: 28
        color: Qt.rgba(0.02, 0.05, 0.10, 0.75)
        border.color: Qt.rgba(0, 0.94, 1, 0.4)
        border.width: 1

        Text {
            anchors.centerIn: parent
            text: "◄ " + String((root.headingDeg - 20 + 360) % 360).padStart(3, '0') + " ··· " +
                  String(root.headingDeg).padStart(3, '0') + "° ··· " +
                  String((root.headingDeg + 20) % 360).padStart(3, '0') + " ►"
            font.family: "JetBrains Mono"
            font.pixelSize: 12
            font.bold: true
            color: "#00f0ff"
        }
    }

    // Left Speed Tape (Airspeed in Knots)
    Rectangle {
        anchors.left: parent.left
        anchors.leftMargin: 80
        anchors.verticalCenter: parent.verticalCenter
        width: 84
        height: 220
        color: Qt.rgba(0.02, 0.05, 0.10, 0.75)
        border.color: Qt.rgba(0, 0.94, 1, 0.5)
        border.width: 1

        Column {
            anchors.fill: parent
            anchors.margins: 8
            spacing: 12

            Text {
                text: "AIRSPEED"
                font.family: "JetBrains Mono"
                font.pixelSize: 9
                color: "#64748b"
                font.bold: true
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: (root.speedKnots + 40).toString()
                font.family: "JetBrains Mono"
                font.pixelSize: 11
                color: Qt.rgba(0, 0.94, 1, 0.5)
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Rectangle {
                width: parent.width
                height: 28
                color: Qt.rgba(0, 0.94, 1, 0.2)
                border.color: "#00f0ff"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: root.speedKnots + " KT"
                    font.family: "JetBrains Mono"
                    font.pixelSize: 13
                    font.bold: true
                    color: "#ffffff"
                }
            }

            Text {
                text: Math.max(0, root.speedKnots - 40).toString()
                font.family: "JetBrains Mono"
                font.pixelSize: 11
                color: Qt.rgba(0, 0.94, 1, 0.5)
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }

    // Right Altitude Tape (Altitude in Feet)
    Rectangle {
        anchors.right: parent.right
        anchors.rightMargin: 80
        anchors.verticalCenter: parent.verticalCenter
        width: 96
        height: 220
        color: Qt.rgba(0.02, 0.05, 0.10, 0.75)
        border.color: Qt.rgba(0, 0.94, 1, 0.5)
        border.width: 1

        Column {
            anchors.fill: parent
            anchors.margins: 8
            spacing: 12

            Text {
                text: "ALTITUDE"
                font.family: "JetBrains Mono"
                font.pixelSize: 9
                color: "#64748b"
                font.bold: true
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Text {
                text: (root.altitudeFt + 1000).toLocaleString()
                font.family: "JetBrains Mono"
                font.pixelSize: 11
                color: Qt.rgba(0, 0.94, 1, 0.5)
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Rectangle {
                width: parent.width
                height: 28
                color: Qt.rgba(0, 0.94, 1, 0.2)
                border.color: "#00f0ff"
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: root.altitudeFt.toLocaleString() + " FT"
                    font.family: "JetBrains Mono"
                    font.pixelSize: 12
                    font.bold: true
                    color: "#ffffff"
                }
            }

            Text {
                text: Math.max(0, root.altitudeFt - 1000).toLocaleString()
                font.family: "JetBrains Mono"
                font.pixelSize: 11
                color: Qt.rgba(0, 0.94, 1, 0.5)
                anchors.horizontalCenter: parent.horizontalCenter
            }
        }
    }

    // Center Tactical Target Reticle & Pitch Crosshair
    Item {
        anchors.centerIn: parent
        width: 180
        height: 120

        // Center reticle circle
        Rectangle {
            anchors.centerIn: parent
            width: 32
            height: 32
            radius: 16
            color: "transparent"
            border.color: "#00f0ff"
            border.width: 1.5

            Rectangle {
                anchors.centerIn: parent
                width: 4
                height: 4
                radius: 2
                color: "#00f0ff"
            }
        }

        // Horizontal pitch crosshair wings
        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            width: 45
            height: 2
            color: "#00f0ff"
        }

        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            width: 45
            height: 2
            color: "#00f0ff"
        }
    }

    // Exit Cockpit Button
    Button {
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
        anchors.horizontalCenter: parent.horizontalCenter
        width: 180
        height: 36

        background: Rectangle {
            color: parent.hovered ? "#ff0055" : Qt.rgba(0.8, 0, 0.2, 0.8)
            border.color: "#ffffff"
            border.width: 1
            radius: 4
        }

        contentItem: Text {
            text: "DISENGAGE COCKPIT [ESC]"
            font.family: "JetBrains Mono"
            font.pixelSize: 11
            font.bold: true
            color: "#ffffff"
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }

        onClicked: {
            root.exitRequested();
        }
    }
}
