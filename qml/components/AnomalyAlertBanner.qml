import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: collapsed ? 145 : Math.min(380, parent.width * 0.35)
    height: collapsed ? 28 : 48
    color: "#f20a0f18"
    border.color: "#ff0055"
    border.width: 1
    radius: 3
    visible: true
    clip: true

    property string alertTitle: "OPERATIONAL THREAT DETECTED"
    property string alertDetails: "Monitoring global airspace and nautical choke corridors."
    property bool collapsed: false

    signal alertClicked()

    Behavior on width {
        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
    }
    Behavior on height {
        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
    }

    // Collapsed Mode
    Item {
        anchors.fill: parent
        visible: root.collapsed

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
                    PropertyAnimation { to: 0.2; duration: 400 }
                    PropertyAnimation { to: 1.0; duration: 400 }
                }
            }

            Text {
                text: "THREAT ALERT ▾"
                color: "#ff0055"
                font.bold: true
                font.pixelSize: 9
                font.family: "Monospace"
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: root.collapsed = false
        }
    }

    // Expanded Mode
    Item {
        anchors.fill: parent
        anchors.margins: 6
        visible: !root.collapsed

        MouseArea {
            anchors.left: parent.left
            anchors.right: bannerControls.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            cursorShape: Qt.PointingHandCursor
            onClicked: root.alertClicked()
        }

        Row {
            anchors.left: parent.left
            anchors.right: bannerControls.left
            anchors.rightMargin: 6
            anchors.verticalCenter: parent.verticalCenter
            spacing: 8

            Rectangle {
                width: 8
                height: 8
                radius: 4
                color: "#ff0055"
                anchors.verticalCenter: parent.verticalCenter

                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    PropertyAnimation { to: 0.2; duration: 500 }
                    PropertyAnimation { to: 1.0; duration: 500 }
                }
            }

            Column {
                anchors.verticalCenter: parent.verticalCenter
                spacing: 2
                width: parent.width - 20

                Text {
                    text: root.alertTitle
                    color: "#ff0055"
                    font.bold: true
                    font.pixelSize: 10
                    font.family: "Monospace"
                    elide: Text.ElideRight
                    width: parent.width
                }

                Text {
                    text: root.alertDetails
                    color: "#94a3b8"
                    font.pixelSize: 8
                    font.family: "Monospace"
                    elide: Text.ElideRight
                    width: parent.width
                }
            }
        }

        Row {
            id: bannerControls
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            spacing: 4

            // Collapse Button
            Rectangle {
                width: 18
                height: 18
                color: btnBannerCollapse.containsMouse ? "#33ff0055" : "#1aff0055"
                border.color: "#ff0055"
                border.width: 1
                radius: 2

                Text {
                    anchors.centerIn: parent
                    text: "▲"
                    color: "#ff0055"
                    font.pixelSize: 8
                    font.bold: true
                }

                MouseArea {
                    id: btnBannerCollapse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.collapsed = true
                }
            }

            // Dismiss Button
            Rectangle {
                width: 18
                height: 18
                color: btnBannerDismiss.containsMouse ? "#33ffffff" : "#0dffffff"
                border.color: "#334155"
                border.width: 1
                radius: 2

                Text {
                    anchors.centerIn: parent
                    text: "×"
                    color: "#94a3b8"
                    font.pixelSize: 10
                    font.bold: true
                }

                MouseArea {
                    id: btnBannerDismiss
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.visible = false
                }
            }
        }
    }
}
