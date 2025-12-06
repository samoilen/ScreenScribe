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
    def __init__(self, current_hotkey: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ScreenScribe - Settings")
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        )
        self.resize(400, 160)

        self._result_hotkey: str | None = None

        layout = QVBoxLayout(self)

        info = QLabel(
            "Capture hotkey (example: ctrl+shift+s, ctrl+alt+c, print screen)\n"
            "Changes apply immediately after saving."
        )
        layout.addWidget(info)

        self.hotkey_edit = QLineEdit(current_hotkey)
        layout.addWidget(self.hotkey_edit)

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
        self._result_hotkey = self.hotkey_edit.text().strip()
        super().accept()

    def get_result(self) -> str | None:
        return self._result_hotkey
