from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PySide6.QtCore import Qt


class SettingsDialog(QDialog):
    def __init__(self, current_capture: str, current_history: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ScreenScribe - Settings")
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        )
        self.resize(400, 160)

        self._result_capture: str | None = None
        self._result_history: str | None = None

        layout = QVBoxLayout(self)

        info = QLabel(
            "Set global shortcuts. Examples: ctrl+shift+s, ctrl+alt+h, print screen.\n"
            "Changes apply immediately after saving."
        )
        layout.addWidget(info)

        self.capture_label = QLabel("Capture hotkey:")
        self.capture_edit = QLineEdit(current_capture)
        self.capture_edit.setPlaceholderText("Capture hotkey (e.g. ctrl+shift+s)")
        layout.addWidget(self.capture_label)
        layout.addWidget(self.capture_edit)

        self.history_label = QLabel("History hotkey:")
        self.history_edit = QLineEdit(current_history)
        self.history_edit.setPlaceholderText("History hotkey (e.g. ctrl+shift+h)")
        layout.addWidget(self.history_label)
        layout.addWidget(self.history_edit)

        btns = QHBoxLayout()
        self.btn_save = QPushButton("Save")
        self.btn_cancel = QPushButton("Cancel")
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)
        btns.addStretch()
        layout.addLayout(btns)

        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def accept(self):
        self._result_capture = self.capture_edit.text().strip()
        self._result_history = self.history_edit.text().strip()
        super().accept()

    def get_capture_result(self) -> str | None:
        return self._result_capture

    def get_history_result(self) -> str | None:
        return self._result_history
