from __future__ import annotations

from PySide6.QtCore import QObject, Signal
import keyboard


class HotkeyManager(QObject):
    """
    Prosty menedżer globalnych skrótów.

    Na razie obsługujemy tylko jeden skrót:
    - capture: domyślnie 'ctrl+shift+s'
    """

    capture_requested = Signal()

    def __init__(self, capture_hotkey: str = "ctrl+shift+s", parent=None):
        super().__init__(parent)
        self._capture_hotkey = capture_hotkey
        self._registered = False

    def start(self):
        """Rejestruje globalny skrót (jeśli jeszcze nie jest zarejestrowany)."""
        if self._registered:
            return

        keyboard.add_hotkey(self._capture_hotkey, self._on_capture_hotkey)
        self._registered = True
        print(f"[Hotkey] Registered global hotkey for capture: {self._capture_hotkey}")

    def _on_capture_hotkey(self):
        # Wywoływane w wątku keyboarda – sygnał Qt jest kolejkujący, więc OK.
        print("[Hotkey] Capture hotkey pressed.")
        self.capture_requested.emit()

    def stop(self):
        """Wyrejestrowuje skrót (na wyjściu aplikacji)."""
        if not self._registered:
            return
        try:
            keyboard.clear_hotkey(self._capture_hotkey)
        except KeyError:
            # Jeśli z jakiegoś powodu nie ma już tego hotkeya – ignorujemy.
            pass
        self._registered = False
        print("[Hotkey] Unregistered global hotkey.")

    def set_hotkey(self, hotkey: str):
        """Aktualizuje skrót i rejestruje ponownie, jeśli już działa."""
        hotkey = hotkey.strip()
        if not hotkey:
            return
        if hotkey == self._capture_hotkey:
            return

        was_registered = self._registered
        if self._registered:
            try:
                keyboard.clear_hotkey(self._capture_hotkey)
            except KeyError:
                pass
            self._registered = False
            print(f"[Hotkey] Cleared previous hotkey: {self._capture_hotkey}")

        self._capture_hotkey = hotkey

        if was_registered:
            keyboard.add_hotkey(self._capture_hotkey, self._on_capture_hotkey)
            self._registered = True
            print(f"[Hotkey] Registered new hotkey: {self._capture_hotkey}")

    @property
    def capture_hotkey(self) -> str:
        return self._capture_hotkey
