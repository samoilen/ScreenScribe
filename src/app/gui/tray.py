import logging
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QStyle, QDialog
from PySide6.QtGui import QIcon
from PySide6.QtCore import Slot, QObject, Signal, QThread, QTimer, QRect

from app.paths import APP_ICON
from app.gui.overlay import SelectionOverlay
from app.gui.history_window import HistoryWindow
from app.gui.settings_dialog import SettingsDialog
from app.core.capture import capture_region
from app.core.ocr import image_file_to_text
from app.core.history import HistoryManager
from app.core.hotkey import HotkeyManager
from app.core.settings import Settings, save_settings


class _OcrWorker(QObject):
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, path: str, lang: str = "eng+pol"):
        super().__init__()
        self.path = path
        self.lang = lang
        self.logger = logging.getLogger("screenscribe.ocrworker")

    @Slot()
    def run(self):
        self.logger.info("OCR start on %s", self.path)
        text = image_file_to_text(self.path, lang=self.lang)
        if not text:
            self.logger.warning("OCR returned empty text.")
            self.failed.emit("ocr_empty")
            return

        self.logger.info("OCR finished, length=%d", len(text))
        self.finished.emit(text)


class ScreenScribeTray(QSystemTrayIcon):
    def __init__(
        self,
        app: QApplication,
        overlay: SelectionOverlay,
        history_manager: HistoryManager,
        settings: Settings,
        hotkeys: HotkeyManager,
        parent=None,
    ):
        icon = QIcon(APP_ICON)
        if icon.isNull():
            icon = app.style().standardIcon(QStyle.SP_ComputerIcon)

        super().__init__(icon, parent)

        self.app = app
        self.overlay = overlay
        self.history_manager = history_manager
        self.settings = settings
        self.hotkeys = hotkeys
        self.history_window: HistoryWindow | None = None
        self._capture_thread: QThread | None = None
        self._ocr_worker: _OcrWorker | None = None
        self.logger = logging.getLogger("screenscribe.tray")

        self.setToolTip("ScreenScribe - Snap text from screen")

        menu = QMenu()
        self.action_capture = menu.addAction("Capture text now")
        self.action_history = menu.addAction("History...")
        self.action_settings = menu.addAction("Settings...")
        menu.addSeparator()
        self.action_exit = menu.addAction("Exit")

        self.action_capture.triggered.connect(self.on_capture_clicked)
        self.action_history.triggered.connect(self.on_history_clicked)
        self.action_settings.triggered.connect(self.on_settings_clicked)
        self.action_exit.triggered.connect(self.on_exit_clicked)

        self.setContextMenu(menu)

        # Sygnały
        self.overlay.selection_made.connect(self.on_selection_made)
        self.hotkeys.history_requested.connect(self.on_history_clicked)

    @Slot()
    def on_capture_clicked(self):
        self.logger.info("Capture requested (menu/hotkey). Starting overlay.")
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

    @Slot()
    def on_settings_clicked(self):
        dlg = SettingsDialog(
            self.hotkeys.capture_hotkey, self.hotkeys.history_hotkey, parent=None
        )
        if dlg.exec() == QDialog.Accepted:
            new_capture = dlg.get_capture_result() or self.hotkeys.capture_hotkey
            new_history = dlg.get_history_result() or self.hotkeys.history_hotkey
            changed = False
            if new_capture != self.hotkeys.capture_hotkey:
                self.logger.info("Updating capture hotkey to %s", new_capture)
                self.hotkeys.set_capture_hotkey(new_capture)
                self.settings.capture_hotkey = new_capture
                changed = True
            if new_history != self.hotkeys.history_hotkey:
                self.logger.info("Updating history hotkey to %s", new_history)
                self.hotkeys.set_history_hotkey(new_history)
                self.settings.history_hotkey = new_history
                changed = True
            if changed:
                save_settings(self.settings)
                self.logger.info("Hotkeys updated and saved.")

    @Slot(object)
    def on_selection_made(self, rect):
        self.logger.info(
            "Selection rectangle x=%s y=%s w=%s h=%s",
            rect.x(),
            rect.y(),
            rect.width(),
            rect.height(),
        )

        if self._capture_thread and self._capture_thread.isRunning():
            self.logger.warning(
                "Capture already in progress, ignoring new selection."
            )
            return
        rect_copy = QRect(rect)  # kopiujemy, ‘•eby uniknŽ•‘' problemÆˆw z referencjŽ
        self.logger.info("Queueing capture via singleShot.")
        # Od‘'aduj start capture do nastŽpnego cyklu zdarze‘" (overlay zd‘>‘y siŽt schowa‘")
        QTimer.singleShot(0, lambda: self._start_capture(rect_copy))

    def _start_capture(self, rect):
        self.logger.info("Capture timer fired, starting capture.")
        # Capture must stay in GUI thread (QScreen.grabWindow is not thread-safe)
        path = capture_region(rect, debug_save=True)
        if not path:
            self.logger.error("Capture failed.")
            return
        self.logger.info("Capture saved to %s", path)

        worker = _OcrWorker(path, lang="eng+pol")
        thread = QThread()
        self._capture_thread = thread
        self._ocr_worker = worker
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(self._on_capture_finished)
        worker.failed.connect(self._on_capture_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(self._clear_capture_thread)

        thread.start()

    @Slot()
    def _clear_capture_thread(self):
        self._capture_thread = None
        self._ocr_worker = None
        self.logger.debug("Capture/OCR thread cleaned up.")

    @Slot(str)
    def _on_capture_finished(self, text: str):
        clipboard = self.app.clipboard()
        clipboard.setText(text)
        self.logger.info("Copied %d characters to clipboard.", len(text))
        self.history_manager.add_entry(text)
        self.logger.info("History entry added.")

    @Slot(str)
    def _on_capture_failed(self, reason: str):
        self.logger.error("Capture/OCR failed: %s", reason)
