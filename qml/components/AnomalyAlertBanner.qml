import QtQuick
import QtQuick.Controls

Rectangle {
    id: root
    width: 420
    height: 48
    color: "#f20a0f18"
    border.color: "#ff0055"
    border.width: 1
    radius: 3
    visible: true

    property string alertTitle: "OPERATIONAL THREAT DETECTED"
    property string alertDetails: "Monitoring global airspace and nautical choke corridors."

    signal alertClicked()

    Row {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 12

        Rectangle {
            width: 10
            height: 10
            radius: 5
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
            width: parent.width - 40

            Text {
                text: root.alertTitle
                color: "#ff0055"
                font.bold: true
                font.pixelSize: 11
                elide: Text.ElideRight
                width: parent.width
            }

            Text {
                text: root.alertDetails
                color: "#94a3b8"
                font.pixelSize: 9
                elide: Text.ElideRight
                width: parent.width
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: root.alertClicked()
    }
}
