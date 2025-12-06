from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QLineEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QGuiApplication

from app.paths import APP_ICON
from app.core.history import HistoryManager


class HistoryWindow(QDialog):
    """
    Proste okno historii:
    - lista wpisów
    - double-click: skopiuj tekst do schowka
    - przycisk na dole: Clear history
    - X zamyka tylko to okno (aplikacja dalej działa w trayu)
    - jest też przycisk minimalizacji "_"
    """

    def __init__(self, history: HistoryManager, parent=None):
        super().__init__(parent)

        # Okno z przyciskiem minimalizacji i zamknięcia
        self.setWindowTitle("ScreenScribe - History")
        self.resize(600, 400)
        icon = QIcon(APP_ICON)
        if icon.isNull():
            icon = QGuiApplication.windowIcon()
        self.setWindowIcon(icon)
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowMinimizeButtonHint
            | Qt.WindowCloseButtonHint
            | Qt.WindowMaximizeButtonHint
        )

        self.history = history
        self._filter_text: str = ""

        layout = QVBoxLayout(self)

        self.info_label = QLabel("Double-click an entry to copy it to clipboard.")
        layout.addWidget(self.info_label)

        filter_layout = QHBoxLayout()
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search history...")
        filter_layout.addWidget(self.filter_edit)
        layout.addLayout(filter_layout)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        buttons_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Clear history")
        buttons_layout.addWidget(self.btn_clear)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # sygnały
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.btn_clear.clicked.connect(self.on_clear_clicked)
        self.filter_edit.textChanged.connect(self.on_filter_changed)

        # początkowe odświeżenie
        self.refresh()

    def refresh(self):
        """Przeładowuje listę wpisów z HistoryManagera z filtrowaniem."""
        self.list_widget.clear()
        entries = self.history.get_entries()
        if self._filter_text:
            term = self._filter_text.lower()
            entries = [e for e in entries if term in e.text.lower()]
        for idx, entry in enumerate(entries, start=1):
            # pokazujemy numer + skrócony początek tekstu
            preview = entry.text.replace("\n", " ")
            if len(preview) > 100:
                preview = preview[:100] + "..."
            item = QListWidgetItem(f"[{idx}]  {preview}")
            # pełny tekst w data
            item.setData(Qt.UserRole, entry.text)
            self.list_widget.addItem(item)

    def on_item_double_clicked(self, item: QListWidgetItem):
        """Kopiujemy pełny tekst wpisu do schowka."""
        text = item.data(Qt.UserRole)
        if not text:
            return

        from PySide6.QtGui import QGuiApplication

        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        print(
            f"[HistoryWindow] Copied {len(text)} characters to clipboard from history."
        )

    def on_clear_clicked(self):
        self.history.clear()
        self.refresh()

    def on_filter_changed(self, text: str):
        self._filter_text = text or ""
        self.refresh()
