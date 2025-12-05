from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QStyle
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot

from app.paths import APP_ICON
from app.gui.overlay import SelectionOverlay
from app.gui.history_window import HistoryWindow
from app.core.capture import capture_region
from app.core.ocr import image_file_to_text
from app.core.history import HistoryManager


class ScreenScribeTray(QSystemTrayIcon):
    def __init__(
        self,
        app: QApplication,
        overlay: SelectionOverlay,
        history_manager: HistoryManager,
        parent=None,
    ):
        icon = QIcon(APP_ICON)
        if icon.isNull():
            icon = app.style().standardIcon(QStyle.SP_ComputerIcon)

        super().__init__(icon, parent)

        self.app = app
        self.overlay = overlay
        self.history_manager = history_manager
        self.history_window: HistoryWindow | None = None

        self.setToolTip("ScreenScribe - Snap text from screen")

        menu = QMenu()
        self.action_capture = menu.addAction("Capture text now")
        self.action_history = menu.addAction("History...")
        menu.addSeparator()
        self.action_exit = menu.addAction("Exit")

        self.action_capture.triggered.connect(self.on_capture_clicked)
        self.action_history.triggered.connect(self.on_history_clicked)
        self.action_exit.triggered.connect(self.on_exit_clicked)

        self.setContextMenu(menu)

        # Sygnał z overlayu (gdy użytkownik zakończy zaznaczenie)
        self.overlay.selection_made.connect(self.on_selection_made)

    @Slot()
    def on_capture_clicked(self):
        self.overlay.start_capture()

    @Slot()
    def on_history_clicked(self):
        if self.history_window is None:
            self.history_window = HistoryWindow(self.history_manager)
        else:
            self.history_window.refresh()

        self.history_window.show()
        self.history_window.raise_()
        self.history_window.activateWindow()

    @Slot()
    def on_exit_clicked(self):
        self.hide()
        self.app.quit()

    @Slot(object)
    def on_selection_made(self, rect):
        # Debug – informacje o prostokącie
        print(
            f"[ScreenScribe] Selection rectangle: "
            f"x={rect.x()}, y={rect.y()}, w={rect.width()}, h={rect.height()}"
        )

        # 1) Screenshot zaznaczonego obszaru
        path = capture_region(rect, debug_save=True)
        if not path:
            print("[ScreenScribe] Capture failed.")
            return

        # 2) OCR na zapisanym obrazku
        text = image_file_to_text(path, lang="eng+pol")
        if not text:
            print("[ScreenScribe] No text recognized.")
            return

        # 3) Wrzucamy tekst do schowka
        clipboard = self.app.clipboard()
        clipboard.setText(text)
        print(f"[ScreenScribe] Copied {len(text)} characters to clipboard.")

        # 4) Dodajemy do historii
        self.history_manager.add_entry(text)
