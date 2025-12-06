import sys
import os
import logging
import ctypes
from PySide6.QtWidgets import QApplication, QStyle
from PySide6.QtGui import QIcon

from app.paths import ensure_runtime_dirs, APP_ICON, LOGS_DIR
from app.gui.tray import ScreenScribeTray
from app.gui.overlay import SelectionOverlay
from app.core.history import HistoryManager
from app.core.hotkey import HotkeyManager
from app.core.settings import load_settings


def _setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, "screenscribe.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )
    logging.getLogger("pytesseract").setLevel(logging.INFO)


def main():
    ensure_runtime_dirs()
    _setup_logging()
    logger = logging.getLogger("screenscribe.main")

    # Windows: ustaw AppUserModelID, aby ikony okien korzystały z własnej ikony zamiast python.exe
    if sys.platform.startswith("win"):
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "ScreenScribe"
            )
            logger.info("Set AppUserModelID for Windows taskbar icon.")
        except Exception as e:
            logger.warning("Failed to set AppUserModelID: %s", e)

    app = QApplication(sys.argv)
    app.setApplicationName("ScreenScribe")

    # KLUCZ: nie zamykaj całej aplikacji, gdy ostatnie okno zostanie zamknięte
    app.setQuitOnLastWindowClosed(False)

    app_icon = QIcon(APP_ICON)
    if app_icon.isNull():
        app_icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
    app.setWindowIcon(app_icon)

    history_manager = HistoryManager(max_entries=50)
    settings = load_settings()
    overlay = SelectionOverlay()
    hotkeys = HotkeyManager(capture_hotkey=settings.capture_hotkey)
    tray = ScreenScribeTray(app, overlay, history_manager, settings, hotkeys)
    tray.show()
    logger.info("ScreenScribe started with hotkey=%s", settings.capture_hotkey)

    # --- NOWE: globalny skrót klawiaturowy do "Capture text now" ---
    # UWAGA: jeśli metoda nazywa się inaczej niż capture_text_now,
    # wpisz tu tę samą, którą podpinasz pod menu "Capture text now"
    hotkeys.capture_requested.connect(tray.on_capture_clicked)
    hotkeys.start()

    # trzymamy referencję, żeby GC nie sprzątnął hotkey managera
    tray._hotkeys = hotkeys

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
