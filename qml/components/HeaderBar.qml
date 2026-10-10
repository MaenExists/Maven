import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    height: 48
    color: "#080c14"
    border.color: "#4d00f0ff"
    border.width: 1

    property string threatLevel: "ELEVATED"
    property string utcTime: ""
    property bool allCollapsed: false

    signal toggleHudClicked()

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

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 16
        spacing: 12

        // Left Branding
        Row {
            spacing: 10
            Layout.alignment: Qt.AlignVCenter

            Rectangle {
                width: 24
                height: 24
                color: "transparent"
                border.color: "#00f0ff"
                border.width: 2
                rotation: 45
                anchors.verticalCenter: parent.verticalCenter

                Rectangle {
                    anchors.centerIn: parent
                    width: 8
                    height: 8
                    color: "#ff0055"
                }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                spacing: 1

                Text {
                    text: root.width > 900 ? "MAVEN // PLANETARY RECON" : "MAVEN"
                    color: "#ffffff"
                    font.bold: true
                    font.pixelSize: 13
                    font.letterSpacing: 1.2
                }

                Text {
                    text: "GEOSPATIAL WAR ROOM"
                    color: "#00f0ff"
                    font.pixelSize: 9
                    font.letterSpacing: 1.0
                    visible: root.width > 700
                }
            }
        }

        Item { Layout.fillWidth: true } // Responsive Spring

        // Threat Level Badge (Center-adaptive)
        Rectangle {
            width: root.width > 800 ? 190 : 130
            height: 26
            color: "#1fff0055"
            border.color: "#ff0055"
            border.width: 1
            radius: 3
            Layout.alignment: Qt.AlignVCenter

            Row {
                anchors.centerIn: parent
                spacing: 6

                Rectangle {
                    width: 7
                    height: 7
                    radius: 3.5
                    color: "#ff0055"
                    anchors.verticalCenter: parent.verticalCenter

                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        PropertyAnimation { to: 0.2; duration: 600 }
                        PropertyAnimation { to: 1.0; duration: 600 }
                    }
                }

                Text {
                    text: root.width > 800 ? ("DEFCON: " + root.threatLevel) : root.threatLevel
                    color: "#ff0055"
                    font.bold: true
                    font.pixelSize: 10
                    font.letterSpacing: 0.8
                }
            }
        }

        Item { Layout.fillWidth: true } // Responsive Spring

        // Right Telemetry Clock & State
        Row {
            spacing: 10
            Layout.alignment: Qt.AlignVCenter

            Text {
                text: root.utcTime
                color: "#94a3b8"
                font.pixelSize: 10
                font.family: "Monospace"
                visible: root.width > 650
            }

            Rectangle {
                width: 60
                height: 22
                color: "#2610b981"
                border.color: "#10b981"
                border.width: 1
                radius: 2

                Text {
                    anchors.centerIn: parent
                    text: "ONLINE"
                    color: "#10b981"
                    font.bold: true
                    font.pixelSize: 9
                    font.letterSpacing: 1
                }
            }

            // Master HUD Collapse / Cinematic View Button
            Rectangle {
                width: 95
                height: 22
                color: btnCleanView.containsMouse ? "#3300f0ff" : "#1a00f0ff"
                border.color: "#00f0ff"
                border.width: 1
                radius: 2

                Row {
                    anchors.centerIn: parent
                    spacing: 4
                    Text {
                        text: root.allCollapsed ? "👁️" : "🌐"
                        font.pixelSize: 9
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    Text {
                        text: root.allCollapsed ? "EXPAND HUD" : "CLEAN VIEW"
                        color: "#00f0ff"
                        font.bold: true
                        font.pixelSize: 8
                        font.letterSpacing: 0.8
                        font.family: "Monospace"
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }

                MouseArea {
                    id: btnCleanView
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.toggleHudClicked()
                }
            }
        }
    }
}
