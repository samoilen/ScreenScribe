from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt

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
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        )

        self.history = history

        layout = QVBoxLayout(self)

        self.info_label = QLabel("Double-click an entry to copy it to clipboard.")
        layout.addWidget(self.info_label)

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

        # początkowe odświeżenie
        self.refresh()

    def refresh(self):
        """Przeładowuje listę wpisów z HistoryManagera."""
        self.list_widget.clear()
        entries = self.history.get_entries()
        for entry in entries:
            # pokazujemy timestamp + skrócony początek tekstu
            preview = entry.text.replace("\n", " ")
            if len(preview) > 100:
                preview = preview[:100] + "..."
            item = QListWidgetItem(f"[{entry.timestamp}]  {preview}")
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
