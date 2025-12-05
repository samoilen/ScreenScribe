from __future__ import annotations

import os
from typing import Optional

from PySide6.QtCore import QRect
from PySide6.QtGui import QGuiApplication

from app.paths import BASE_DIR


def capture_region(rect: QRect, debug_save: bool = True) -> Optional[str]:
    """
    Robi screenshot wskazanego prostokąta ekranu.
    Zwraca ścieżkę do pliku PNG, jeśli debug_save=True (na razie do testów).

    Docelowo:
    - zamiast zawsze zapisywać do pliku, będziemy zwracać QImage / bytes
      prosto do OCR.
    """
    screen = QGuiApplication.primaryScreen()
    if screen is None:
        print("[Capture] ERROR: No primary screen found.")
        return None

    # grabWindow(0) = całe okno pulpitu, z offsetami i rozmiarem prostokąta
    pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())

    if pixmap.isNull():
        print("[Capture] ERROR: Grabbed pixmap is null.")
        return None

    if not debug_save:
        # Na razie nic nie zwracamy – jak zaczniemy używać OCR, możemy
        # tu zwrócić pixmap / QImage / bytes.
        return None

    # Ścieżka do pliku debugowego
    output_path = os.path.join(BASE_DIR, "last_capture.png")

    ok = pixmap.save(output_path, "PNG")
    if not ok:
        print(f"[Capture] ERROR: Failed to save screenshot to {output_path}")
        return None

    print(f"[Capture] Saved screenshot to {output_path}")
    return output_path
