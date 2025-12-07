from __future__ import annotations

from PySide6.QtCore import QObject, Signal
import keyboard


class HotkeyManager(QObject):
    """
    Prosty menedżer globalnych skrótów.

    Obsługujemy dwa skróty:
    - capture: domyślnie 'ctrl+shift+s'
    - history: domyślnie 'ctrl+shift+h'
    """

    capture_requested = Signal()
    history_requested = Signal()

    def __init__(
        self,
        capture_hotkey: str = "ctrl+shift+s",
        history_hotkey: str = "ctrl+shift+h",
        parent=None,
    ):
        super().__init__(parent)
        self._capture_hotkey = capture_hotkey
        self._history_hotkey = history_hotkey
        self._registered = False

    def start(self):
        """Rejestruje globalne skróty (jeśli jeszcze nie są zarejestrowane)."""
        if self._registered:
            return

        keyboard.add_hotkey(self._capture_hotkey, self._on_capture_hotkey)
        keyboard.add_hotkey(self._history_hotkey, self._on_history_hotkey)
        self._registered = True
        print(f"[Hotkey] Registered global hotkey for capture: {self._capture_hotkey}")
        print(f"[Hotkey] Registered global hotkey for history: {self._history_hotkey}")

    def _on_capture_hotkey(self):
        print("[Hotkey] Capture hotkey pressed.")
        self.capture_requested.emit()

    def _on_history_hotkey(self):
        print("[Hotkey] History hotkey pressed.")
        self.history_requested.emit()

    def stop(self):
        """Wyrejestrowuje skróty (na wyjściu aplikacji)."""
        if not self._registered:
            return
        try:
            keyboard.clear_hotkey(self._capture_hotkey)
        except KeyError:
            pass
        try:
            keyboard.clear_hotkey(self._history_hotkey)
        except KeyError:
            pass
        self._registered = False
        print("[Hotkey] Unregistered global hotkeys.")

    def set_capture_hotkey(self, hotkey: str):
        """Aktualizuje skrót do przechwytywania i rejestruje ponownie, jeśli już działa."""
        hotkey = hotkey.strip()
        if not hotkey or hotkey == self._capture_hotkey:
            return

        was_registered = self._registered
        if self._registered:
            try:
                keyboard.clear_hotkey(self._capture_hotkey)
            except KeyError:
                pass
            self._registered = False
            print(f"[Hotkey] Cleared previous capture hotkey: {self._capture_hotkey}")

        self._capture_hotkey = hotkey

        if was_registered:
            keyboard.add_hotkey(self._capture_hotkey, self._on_capture_hotkey)
            keyboard.add_hotkey(self._history_hotkey, self._on_history_hotkey)
            self._registered = True
            print(f"[Hotkey] Registered new capture hotkey: {self._capture_hotkey}")

    def set_history_hotkey(self, hotkey: str):
        """Aktualizuje skrót do historii i rejestruje ponownie, jeśli już działa."""
        hotkey = hotkey.strip()
        if not hotkey or hotkey == self._history_hotkey:
            return

        was_registered = self._registered
        if self._registered:
            try:
                keyboard.clear_hotkey(self._history_hotkey)
            except KeyError:
                pass
            self._registered = False
            print(f"[Hotkey] Cleared previous history hotkey: {self._history_hotkey}")

        self._history_hotkey = hotkey

        if was_registered:
            keyboard.add_hotkey(self._capture_hotkey, self._on_capture_hotkey)
            keyboard.add_hotkey(self._history_hotkey, self._on_history_hotkey)
            self._registered = True
            print(f"[Hotkey] Registered new history hotkey: {self._history_hotkey}")

    @property
    def capture_hotkey(self) -> str:
        return self._capture_hotkey

    @property
    def history_hotkey(self) -> str:
        return self._history_hotkey

    def set_hotkey(self, hotkey: str):
        """Backward compatibility for capture-only setter."""
        self.set_capture_hotkey(hotkey)
