from __future__ import annotations

import keyboard
from PySide6.QtCore import QObject, Signal


class HotkeyController(QObject):
    """
    Zarządza globalnym skrótem klawiaturowym przy użyciu biblioteki `keyboard`.

    - combination: np. "ctrl+shift+s"
    - trigger_capture: sygnał Qt emitowany z callbacka keyboard
      (slot po stronie Qt uruchomi np. overlay.start_capture()).
    """

    trigger_capture = Signal()

    def __init__(self, combination: str = "ctrl+shift+s", parent=None):
        super().__init__(parent)
        self._combination = combination
        self._hotkey_id = None

    @property
    def combination(self) -> str:
        return self._combination

    def start(self):
        """Rejestruje globalny skrót."""
        if self._hotkey_id is not None:
            return

        def _callback():
            # Uwaga: to wywołuje się w wątku keyboard.
            # Emisja sygnału jest thread-safe – slot w Qt wykona się w wątku GUI.
            print(f"[Hotkey] Hotkey pressed: {self._combination}")
            self.trigger_capture.emit()

        self._hotkey_id = keyboard.add_hotkey(self._combination, _callback)
        print(f"[Hotkey] Registered global hotkey: {self._combination}")

    def stop(self):
        """Wyrejestrowuje globalny skrót (np. przy zamykaniu aplikacji)."""
        if self._hotkey_id is None:
            return
        try:
            keyboard.remove_hotkey(self._hotkey_id)
            print(f"[Hotkey] Unregistered global hotkey: {self._combination}")
        except Exception as e:
            print(f"[Hotkey] ERROR while unregistering hotkey: {e}")
        self._hotkey_id = None
