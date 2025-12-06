from __future__ import annotations

import logging
from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QRect, QPoint

from app.paths import LAST_CAPTURE_FILE

logger = logging.getLogger("screenscribe.capture")


def capture_region(rect: QRect, debug_save: bool = True) -> str | None:
    """
    Robi zrzut ekranu z TEGO monitora, na którym leży zaznaczenie.

    rect: prostokąt w GLOBALNYCH współrzędnych (z SelectionOverlay).
    Zwraca ścieżkę do pliku PNG albo None, jeśli coś poszło nie tak.
    """
    app = QGuiApplication.instance()
    if app is None:
        logger.error("No QGuiApplication instance.")
        return None

    screens = QGuiApplication.screens()
    if not screens:
        logger.error("No screens available.")
        return None

    # 1) Szukamy ekranu, na którym leży środek prostokąta
    center: QPoint = rect.center()
    screen = QGuiApplication.screenAt(center)

    # Fallback: jeśli z jakiegoś powodu screenAt() zwróci None,
    # wybieramy pierwszy ekran, który przecina się z rect
    if screen is None:
        for s in screens:
            if rect.intersects(s.geometry()):
                screen = s
                break

    # Ostateczny fallback: primary screen
    if screen is None:
        screen = QGuiApplication.primaryScreen()

    if screen is None:
        logger.error("Could not determine target screen.")
        return None

    screen_geo = screen.geometry()
    logger.info("Using screen: %s geo=%s rect=%s", screen.name(), screen_geo, rect)

    # 2) Liczymy lokalne współrzędne prostokąta względem tego ekranu
    local_rect = QRect(
        rect.x() - screen_geo.x(),
        rect.y() - screen_geo.y(),
        rect.width(),
        rect.height(),
    ).normalized()

    # Ograniczamy do rozmiaru ekranu (współrzędne lokalne)
    screen_rect = QRect(0, 0, screen_geo.width(), screen_geo.height())
    local_rect = local_rect.intersected(screen_rect)

    if local_rect.isEmpty():
        logger.error("Local crop rect empty after intersection: %s", local_rect)
        return None

    logger.info("Local crop rect on screen: %s", local_rect)

    # 3) Zrzut fragmentu ekranu (tylko z tego monitora)
    pixmap = screen.grabWindow(
        0,
        local_rect.x(),
        local_rect.y(),
        local_rect.width(),
        local_rect.height(),
    )

    if pixmap.isNull():
        logger.error("Screenshot pixmap is null.")
        return None

    path = LAST_CAPTURE_FILE
    ok = pixmap.save(path)
    if not ok:
        logger.error("Failed to save screenshot to %s", path)
        return None

    if debug_save:
        logger.info("Saved screenshot to %s", path)

    return path
