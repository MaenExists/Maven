import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    height: 38
    color: "#e6080c14"
    border.color: searchInput.activeFocus ? "#00f0ff" : "#4d00f0ff"
    border.width: searchInput.activeFocus ? 2 : 1
    radius: 3
    z: 100

    property bool isSearching: false
    signal placeSelected(string name, real lat, real lon, string displayName, string category)

    ListModel {
        id: resultsModel
    }

    // Debounce timer for smooth typing without network hammering
    Timer {
        id: debounceTimer
        interval: 250
        repeat: false
        onTriggered: {
            var q = searchInput.text.trim();
            if (q.length < 2) {
                resultsModel.clear();
                popupDropdown.visible = false;
                root.isSearching = false;
                return;
            }
            fetchSearchResults(q);
        }
    }

    function fetchSearchResults(query) {
        root.isSearching = true;
        var xhr = new XMLHttpRequest();
        var url = "http://127.0.0.1:8765/api/search?q=" + encodeURIComponent(query);
        xhr.open("GET", url);
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                root.isSearching = false;
                if (xhr.status === 200) {
                    try {
                        var response = JSON.parse(xhr.responseText);
                        resultsModel.clear();
                        var items = response.results || [];
                        for (var i = 0; i < items.length; i++) {
                            resultsModel.append({
                                name: items[i].name || "",
                                display_name: items[i].display_name || "",
                                lat: Number(items[i].lat) || 0.0,
                                lon: Number(items[i].lon) || 0.0,
                                type: items[i].type || "place",
                                category: items[i].category || "SECTOR"
                            });
                        }
                        popupDropdown.visible = resultsModel.count > 0;
                    } catch (e) {
                        console.error("Error parsing search results:", e);
                    }
                }
            }
        };
        xhr.send();
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        spacing: 8

        // Tactical Search Icon
        Text {
            text: "⌕"
            color: root.isSearching ? "#ff0055" : (searchInput.activeFocus ? "#00f0ff" : "#64748b")
            font.bold: true
            font.pixelSize: 18
            Layout.alignment: Qt.AlignVCenter
        }

        // Input Field
        TextField {
            id: searchInput
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#ffffff"
            placeholderText: "SEARCH PLANETARY RECON // GLOBAL PLACES & SENSORS..."
            placeholderTextColor: "#475569"
            font.pixelSize: 11
            font.family: "Monospace"
            verticalAlignment: TextInput.AlignVCenter
            background: Item {}

            onTextChanged: {
                debounceTimer.restart();
            }

            Keys.onEscapePressed: {
                popupDropdown.visible = false;
                searchInput.focus = false;
            }

            Keys.onReturnPressed: {
                if (resultsModel.count > 0) {
                    var top = resultsModel.get(0);
                    selectPlace(top);
                }
            }
        }

        // Searching Spinner or Clear Button
        Rectangle {
            width: 18
            height: 18
            color: "transparent"
            Layout.alignment: Qt.AlignVCenter
            visible: root.isSearching

            Rectangle {
                anchors.centerIn: parent
                width: 6
                height: 6
                radius: 3
                color: "#ff0055"
                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    PropertyAnimation { to: 0.2; duration: 300 }
                    PropertyAnimation { to: 1.0; duration: 300 }
                }
            }
        }

        Text {
            text: "×"
            color: "#94a3b8"
            font.pixelSize: 16
            visible: searchInput.text.length > 0 && !root.isSearching
            Layout.alignment: Qt.AlignVCenter

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    searchInput.text = "";
                    resultsModel.clear();
                    popupDropdown.visible = false;
                }
            }
        }
    }

    function selectPlace(item) {
        popupDropdown.visible = false;
        searchInput.focus = false;
        root.placeSelected(item.name, item.lat, item.lon, item.display_name, item.category);
    }

    // Autocomplete Dropdown List
    Rectangle {
        id: popupDropdown
        anchors.top: root.bottom
        anchors.topMargin: 4
        anchors.left: root.left
        anchors.right: root.right
        height: Math.min(resultsModel.count * 46 + 4, 280)
        color: "#f206090f"
        border.color: "#00f0ff"
        border.width: 1
        radius: 3
        visible: false
        clip: true

        ListView {
            id: resultsList
            anchors.fill: parent
            anchors.margins: 2
            model: resultsModel
            spacing: 2
            clip: true

            delegate: Rectangle {
                id: itemRect
                width: resultsList.width
                height: 42
                color: itemMouse.containsMouse ? "#2600f0ff" : "transparent"
                border.color: itemMouse.containsMouse ? "#4d00f0ff" : "transparent"
                border.width: 1
                radius: 2

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 8
                    anchors.rightMargin: 8
                    spacing: 8

                    // Category Badge
                    Rectangle {
                        width: 72
                        height: 20
                        color: "#1a00f0ff"
                        border.color: "#00f0ff"
                        border.width: 1
                        radius: 2
                        Layout.alignment: Qt.AlignVCenter

                        Text {
                            anchors.centerIn: parent
                            text: model.category.length > 9 ? model.category.substring(0, 9) : model.category
                            color: "#00f0ff"
                            font.pixelSize: 8
                            font.bold: true
                            font.family: "Monospace"
                        }
                    }

                    // Place Details
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignVCenter
                        spacing: 1

                        Text {
                            text: model.name
                            color: "#ffffff"
                            font.bold: true
                            font.pixelSize: 11
                            font.family: "Monospace"
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }

                        Text {
                            text: model.display_name
                            color: "#64748b"
                            font.pixelSize: 9
                            font.family: "Monospace"
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                    }

                    // Coordinates Badge
                    Text {
                        text: model.lat.toFixed(2) + "°, " + model.lon.toFixed(2) + "°"
                        color: "#10b981"
                        font.pixelSize: 9
                        font.family: "Monospace"
                        Layout.alignment: Qt.AlignVCenter
                    }
                }

                MouseArea {
                    id: itemMouse
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        selectPlace(model);
                    }
                }
            }
        }
    }
}
