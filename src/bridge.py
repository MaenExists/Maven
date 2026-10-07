"""
Qt & WebChannel Bridge
Facilitates bi-directional communication between PySide6, QML HUD, and CesiumJS WebGL globe.
"""

import json
import logging
from typing import Any, Dict

from PySide6.QtCore import QObject, Signal, Slot

logger = logging.getLogger(__name__)


class MavenBridge(QObject):
    """Bridge object exposed to both QML and JavaScript."""

    # Outgoing signals to QML / JS
    entitySelected = Signal(str, str, str)  # entity_type, entity_id, json_payload
    alertTriggered = Signal(str, str, str)  # alert_id, alert_title, json_payload
    cameraFocusRequested = Signal(float, float, float)  # lon, lat, altitude
    cameraModalOpened = Signal(str, str, str, str)  # cam_id, name, image_url, stream_url
    layerToggled = Signal(str, bool)  # layer_id, state
    statsUpdated = Signal(int, int, int, int, int)  # flights, vessels, fires, quakes, cams
    changeDetectionTriggered = Signal(str)  # preset_id
    measureModeActivated = Signal(str)  # mode: "distance", "area", "off"

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._active_entity: Dict[str, Any] = {}

    @Slot(str, str, str)
    def notifyEntitySelected(self, entity_type: str, entity_id: str, json_str: str) -> None:
        """Called from Cesium globe when user clicks an entity."""
        logger.info("Entity selected on globe: %s - %s", entity_type, entity_id)
        try:
            self._active_entity = json.loads(json_str)
        except Exception:
            self._active_entity = {"id": entity_id, "type": entity_type}
        self.entitySelected.emit(entity_type, entity_id, json_str)

    @Slot(str, str, str, str)
    def openCameraFeed(self, cam_id: str, name: str, img_url: str, stream_url: str) -> None:
        """Called when user selects a live surveillance camera."""
        logger.info("Opening surveillance camera feed: %s (%s)", name, cam_id)
        self.cameraModalOpened.emit(cam_id, name, img_url, stream_url)

    @Slot(float, float, float)
    def flyToLocation(self, lon: float, lat: float, height: float = 150000.0) -> None:
        """Called from QML HUD to position the 3D globe camera."""
        logger.info("FlyTo command: lon=%.4f lat=%.4f h=%.1f", lon, lat, height)
        self.cameraFocusRequested.emit(lon, lat, height)

    @Slot(str, bool)
    def toggleLayer(self, layer_id: str, enabled: bool) -> None:
        """Called from QML layer panel to show/hide layers."""
        logger.info("Toggle layer: %s -> %s", layer_id, enabled)
        self.layerToggled.emit(layer_id, enabled)

    @Slot(str)
    def runChangeDetection(self, preset_id: str) -> None:
        """Called to trigger satellite change detection sequence."""
        logger.info("Run satellite change detection: %s", preset_id)
        self.changeDetectionTriggered.emit(preset_id)

    @Slot(str)
    def setMeasurementMode(self, mode: str) -> None:
        """Called to activate interactive ruler (distance/area/none)."""
        logger.info("Set measurement mode: %s", mode)
        self.measureModeActivated.emit(mode)
