import sys
from PySide6.QtWidgets import QApplication, QStyle
from PySide6.QtGui import QIcon

from app.paths import ensure_runtime_dirs, APP_ICON
from app.gui.tray import ScreenScribeTray
from app.gui.overlay import SelectionOverlay
from app.core.history import HistoryManager


def main():
    ensure_runtime_dirs()

    app = QApplication(sys.argv)
    app.setApplicationName("ScreenScribe")

    # KLUCZ: nie zamykaj całej aplikacji, gdy ostatnie okno zostanie zamknięte
    app.setQuitOnLastWindowClosed(False)

    app_icon = QIcon(APP_ICON)
    if app_icon.isNull():
        app_icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
    app.setWindowIcon(app_icon)

    history_manager = HistoryManager(max_entries=50)
    overlay = SelectionOverlay()
    tray = ScreenScribeTray(app, overlay, history_manager)
    tray.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
