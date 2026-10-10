#!/usr/bin/env python3
"""
MAVEN: Open-Source Geospatial Intelligence & Planetary Monitoring Platform
Main Application Entry Point.
"""

import argparse
import logging
import os
import signal
import sys
import time

from src.bridge import MavenBridge
from src.config import CONFIG
from src.server.local_server import TacticalServer

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("maven")


def run_server_only(host: str, port: int) -> None:
    """Run local tactical REST server and headless web console."""
    server = TacticalServer(host=host, port=port)
    server.start()
    logger.info("=" * 60)
    logger.info("MAVEN HEADLESS SERVER STARTED")
    logger.info("Access Tactical 3D Globe at: http://%s:%d/", host, port)
    logger.info("=" * 60)

    def shutdown(signum, frame):
        logger.info("Received termination signal. Shutting down...")
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while True:
        time.sleep(1)


def run_gui_app(host: str, port: int) -> None:
    """Launch PySide6 QML Desktop Operations Center."""
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QGuiApplication, QIcon
    from PySide6.QtQml import QQmlApplicationEngine
    from PySide6.QtWebEngineQuick import QtWebEngineQuick

    # Configure GPU hardware acceleration and WebGL flags
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--enable-gpu-rasterization "
        "--enable-zero-copy "
        "--ignore-gpu-blocklist "
        "--enable-webgl "
        "--enable-accelerated-video-decode "
        "--enable-accelerated-2d-canvas "
        "--disable-background-timer-throttling "
        "--num-raster-threads=4"
    )

    # Initialize QtWebEngine runtime
    QtWebEngineQuick.initialize()

    # Start local background tactical content server
    server = TacticalServer(host=host, port=port)
    server.start()

    app = QGuiApplication(sys.argv)
    app.setApplicationName("Maven")
    app.setOrganizationName("MavenOps")

    # Bridge setup
    bridge = MavenBridge()

    # QML Engine setup
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("mavenBridge", bridge)

    qml_file = os.path.join(os.path.dirname(__file__), "qml", "Main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        logger.error("Failed to load QML interface. Falling back to browser view.")
        server.stop()
        sys.exit(1)

    logger.info("Maven QML Operations Center running.")

    def cleanup():
        server.stop()

    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec())


def main() -> None:
    parser = argparse.ArgumentParser(description="MAVEN: Planetary Reconnaissance & OSINT Platform")
    parser.add_argument("--host", default=CONFIG.HOST, help="Host address to bind HTTP server")
    parser.add_argument("--port", type=int, default=CONFIG.PORT, help="Port to bind HTTP server")
    parser.add_argument("--server-only", action="store_true", help="Run HTTP server only without desktop QML GUI")
    args = parser.parse_args()

    # Auto-detect display availability (e.g. headless server vs X11/Wayland display)
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    if args.server_only or not has_display:
        if not has_display and not args.server_only:
            logger.info("No active display detected. Auto-switching to server mode.")
        run_server_only(args.host, args.port)
    else:
        try:
            run_gui_app(args.host, args.port)
        except Exception as e:
            logger.warning("GUI launch failed (%s). Falling back to headless server mode.", e)
            run_server_only(args.host, args.port)


if __name__ == "__main__":
    main()
