import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    height: collapsed ? 24 : 40
    color: "#e6080c14"
    border.color: "#4d00f0ff"
    border.width: 1
    radius: 3
    clip: true

    property string currentBasemap: "SATELLITE"
    property bool collapsed: false
    property bool streetViewActive: false
    property bool bordersActive: true

    Behavior on height {
        NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
    }

    signal basemapClicked()
    signal sunClicked()
    signal buildingsClicked()
    signal streetViewClicked()
    signal bordersClicked()
    signal tiltClicked()
    signal northClicked()
    signal zoomInClicked()
    signal zoomOutClicked()
    signal drawZoneClicked()
    signal rulerClicked()
    signal areaClicked()
    signal satDiffClicked()
    signal chokepointClicked()
    signal clearClicked()

    // Mini Collapsed Pill
    Item {
        anchors.fill: parent
        visible: root.collapsed

        Row {
            anchors.centerIn: parent
            spacing: 6
            Text { text: "⚙"; font.pixelSize: 10; color: "#00f0ff"; anchors.verticalCenter: parent.verticalCenter }
            Text {
                text: "COMMAND DOCK ▾"
                color: "#94a3b8"
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

    RowLayout {
        anchors.fill: parent
        anchors.margins: 3
        spacing: 3
        visible: !root.collapsed

        // Left Navigation Scroll Chevron
        Button {
            id: btnScrollLeft
            Layout.preferredWidth: 20
            Layout.fillHeight: true
            visible: flickable.contentWidth > flickable.width
            opacity: flickable.contentX > 4 ? 1.0 : 0.35
            contentItem: Text {
                anchors.centerIn: parent
                text: "◀"
                color: "#00f0ff"
                font.pixelSize: 9
                font.bold: true
            }
            background: Rectangle {
                color: btnScrollLeft.hovered ? "#4000f0ff" : "#1a00f0ff"
                border.color: "#3300f0ff"
                border.width: 1
                radius: 2
            }
            onClicked: {
                scrollAnim.to = Math.max(0, flickable.contentX - 220);
                scrollAnim.restart();
            }
        }

        Flickable {
            id: flickable
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentWidth: buttonRow.implicitWidth
            contentHeight: height
            flickableDirection: Flickable.HorizontalFlick
            clip: true
            pressDelay: 120
            boundsBehavior: Flickable.DragAndOvershootBounds
            flickDeceleration: 1800

            NumberAnimation {
                id: scrollAnim
                target: flickable
                property: "contentX"
                duration: 220
                easing.type: Easing.OutCubic
            }

            WheelHandler {
                acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                onWheel: function(event) {
                    var delta = event.angleDelta.y !== 0 ? event.angleDelta.y : event.angleDelta.x;
                    var maxScroll = Math.max(0, flickable.contentWidth - flickable.width);
                    flickable.contentX = Math.max(0, Math.min(maxScroll, flickable.contentX - (delta * 1.5)));
                }
            }

            RowLayout {
                id: buttonRow
                height: parent.height - 4
                spacing: 5
                anchors.top: parent.top
                anchors.topMargin: 1

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

                // Street View Mode
                Button {
                    id: btnStreetView
                    Layout.fillHeight: true
                    contentItem: Row {
                        spacing: 5
                        anchors.centerIn: parent
                        Text { text: "🚶"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                        Text {
                            text: root.streetViewActive ? "STREET [ON]" : "STREET VIEW"
                            color: root.streetViewActive ? "#10b981" : "#e2e8f0"
                            font.bold: true
                            font.pixelSize: 10
                            font.family: "Monospace"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                    background: Rectangle {
                        color: root.streetViewActive ? "#3310b981" : (btnStreetView.hovered ? "#33ffffff" : "#0dffffff")
                        border.color: root.streetViewActive ? "#10b981" : "#4000f0ff"
                        border.width: 1
                        radius: 2
                    }
                    onClicked: root.streetViewClicked()
                }

                // Country Borders Toggle
                Button {
                    id: btnBorders
                    Layout.fillHeight: true
                    contentItem: Row {
                        spacing: 5
                        anchors.centerIn: parent
                        Text { text: "🌐"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                        Text {
                            text: root.bordersActive ? "BORDERS [ON]" : "BORDERS [OFF]"
                            color: root.bordersActive ? "#00f0ff" : "#64748b"
                            font.bold: true
                            font.pixelSize: 10
                            font.family: "Monospace"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                    background: Rectangle {
                        color: root.bordersActive ? "#2600f0ff" : (btnBorders.hovered ? "#33ffffff" : "#0dffffff")
                        border.color: root.bordersActive ? "#00f0ff" : "#334155"
                        border.width: 1
                        radius: 2
                    }
                    onClicked: root.bordersClicked()
                }

                // 3D Perspective Tilt
                Button {
                    id: btnTilt
                    Layout.fillHeight: true
                    contentItem: Row {
                        spacing: 5
                        anchors.centerIn: parent
                        Text { text: "📐"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                        Text {
                            text: "3D TILT"
                            color: "#e2e8f0"
                            font.bold: true
                            font.pixelSize: 10
                            font.family: "Monospace"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                    background: Rectangle {
                        color: btnTilt.hovered ? "#33ffffff" : "#0dffffff"
                        border.color: "#4000f0ff"
                        border.width: 1
                        radius: 2
                    }
                    onClicked: root.tiltClicked()
                }

                // North Reset
                Button {
                    id: btnNorth
                    Layout.fillHeight: true
                    contentItem: Row {
                        spacing: 5
                        anchors.centerIn: parent
                        Text { text: "🧭"; font.pixelSize: 11; anchors.verticalCenter: parent.verticalCenter }
                        Text {
                            text: "NORTH"
                            color: "#00f0ff"
                            font.bold: true
                            font.pixelSize: 10
                            font.family: "Monospace"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                    background: Rectangle {
                        color: btnNorth.hovered ? "#33ffffff" : "#0dffffff"
                        border.color: "#4000f0ff"
                        border.width: 1
                        radius: 2
                    }
                    onClicked: root.northClicked()
                }

                // Zoom In
                Button {
                    id: btnZoomIn
                    Layout.fillHeight: true
                    contentItem: Text {
                        anchors.centerIn: parent
                        text: "＋"
                        color: "#00f0ff"
                        font.bold: true
                        font.pixelSize: 11
                    }
                    background: Rectangle {
                        color: btnZoomIn.hovered ? "#33ffffff" : "#0dffffff"
                        border.color: "#4000f0ff"
                        border.width: 1
                        radius: 2
                    }
                    onClicked: root.zoomInClicked()
                }

                // Zoom Out
                Button {
                    id: btnZoomOut
                    Layout.fillHeight: true
                    contentItem: Text {
                        anchors.centerIn: parent
                        text: "－"
                        color: "#00f0ff"
                        font.bold: true
                        font.pixelSize: 11
                    }
                    background: Rectangle {
                        color: btnZoomOut.hovered ? "#33ffffff" : "#0dffffff"
                        border.color: "#4000f0ff"
                        border.width: 1
                        radius: 2
                    }
                    onClicked: root.zoomOutClicked()
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

            ScrollBar.horizontal: ScrollBar {
                id: hScrollBar
                height: 3
                anchors.bottom: parent.bottom
                policy: flickable.contentWidth > flickable.width ? ScrollBar.AlwaysOn : ScrollBar.AlwaysOff
                contentItem: Rectangle {
                    implicitHeight: 3
                    radius: 1.5
                    color: hScrollBar.hovered || hScrollBar.pressed ? "#00f0ff" : "#4d00f0ff"
                }
                background: Rectangle {
                    color: "#1a00f0ff"
                    radius: 1.5
                }
            }
        }

        // Right Navigation Scroll Chevron
        Button {
            id: btnScrollRight
            Layout.preferredWidth: 20
            Layout.fillHeight: true
            visible: flickable.contentWidth > flickable.width
            opacity: flickable.contentX < (flickable.contentWidth - flickable.width - 4) ? 1.0 : 0.35
            contentItem: Text {
                anchors.centerIn: parent
                text: "▶"
                color: "#00f0ff"
                font.pixelSize: 9
                font.bold: true
            }
            background: Rectangle {
                color: btnScrollRight.hovered ? "#4000f0ff" : "#1a00f0ff"
                border.color: "#3300f0ff"
                border.width: 1
                radius: 2
            }
            onClicked: {
                scrollAnim.to = Math.min(flickable.contentWidth - flickable.width, flickable.contentX + 220);
                scrollAnim.restart();
            }
        }

        // Collapse Button pinned right
        Button {
            id: btnDockCollapse
            Layout.fillHeight: true
            Layout.preferredWidth: 20
            contentItem: Text {
                anchors.centerIn: parent
                text: "▲"
                color: "#64748b"
                font.bold: true
                font.pixelSize: 8
            }
            background: Rectangle {
                color: btnDockCollapse.hovered ? "#33ffffff" : "#08ffffff"
                border.color: "#334155"
                border.width: 1
                radius: 2
            }
            onClicked: root.collapsed = true
        }
    }
}
