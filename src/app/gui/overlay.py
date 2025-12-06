from __future__ import annotations

import logging
from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QGuiApplication, QCursor
from PySide6.QtWidgets import QWidget

logger = logging.getLogger("screenscribe.overlay")


class SelectionOverlay(QWidget):
    """
    Półprzezroczysty overlay do zaznaczania obszaru ekranu.

    Najważniejsze cechy:
    - Pokrywa CAŁY ekran, na którym znajdował się kursor
      w momencie uruchomienia trybu zaznaczania.
    - Użytkownik przeciąga myszką, żeby narysować prostokąt.
    - Po puszczeniu przycisku emitujemy sygnał `selection_made`
      z prostokątem w GLOBALNYCH współrzędnych.
    - ESC anuluje wybór.
    """

    selection_made = Signal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Flagi okna: bez ramki, zawsze na wierzchu, bez ikony na pasku zadań.
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        # Przezroczyste tło, żeby półprzezroczysty overlay działał.
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        self._dragging = False
        self._start_pos: QPoint | None = None
        self._current_pos: QPoint | None = None
        self._selection_rect: QRect = QRect()

    # --- API publiczne ---

    def start_capture(self):
        """
        Uruchamia tryb zaznaczania:

        - Wybiera ekran na podstawie aktualnej pozycji kursora,
        - dopasowuje okno do geometrii TEGO ekranu,
        - resetuje poprzedni wybór i pokazuje overlay.
        """
        logger.info("Overlay start_capture triggered.")
        cursor_pos = QCursor.pos()
        screen = QGuiApplication.screenAt(cursor_pos)
        if screen is None:
            screen = QGuiApplication.primaryScreen()

        if screen is not None:
            geo = screen.geometry()
        else:
            # awaryjnie, gdyby nie było żadnych ekranów (praktycznie nierealne)
            geo = QRect(0, 0, 1920, 1080)

        self.setGeometry(geo)
        logger.info("Overlay geometry set to %s", geo)

        self._dragging = False
        self._start_pos = None
        self._current_pos = None
        self._selection_rect = QRect()

        self.show()
        self.raise_()
        self.activateWindow()
        logger.info("Overlay shown/raised/activated.")

    # --- Obsługa wejścia ---

    def keyPressEvent(self, event):
        # ESC -> anulowanie zaznaczenia
        if event.key() == Qt.Key_Escape:
            self._cancel_selection()
            return
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            # Pozycja lokalna w overlayu
            self._start_pos = event.position().toPoint()
            self._current_pos = self._start_pos
            self._update_selection_rect()
            self.update()
            logger.info("Overlay drag started at %s", self._start_pos)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self._start_pos is not None:
            self._current_pos = event.position().toPoint()
            self._update_selection_rect()
            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            if self._start_pos is not None:
                self._current_pos = event.position().toPoint()
                self._update_selection_rect()

            # Jeśli prostokąt jest "zbyt mały" traktujemy to jako anulowanie
            if self._selection_rect.width() < 5 or self._selection_rect.height() < 5:
                logger.info("Overlay selection too small; cancelling.")
                self._cancel_selection()
                return

            # Konwersja: lokalne współrzędne overlayu -> GLOBALNE współrzędne pulpitu
            local_rect = self._selection_rect.normalized()
            offset = self.geometry().topLeft()  # globalne położenie overlayu
            global_rect = QRect(
                local_rect.x() + offset.x(),
                local_rect.y() + offset.y(),
                local_rect.width(),
                local_rect.height(),
            )

            # Emitujemy prostokąt w GLOBALNYCH współrzędnych
            logger.info("Overlay emit selection_made: %s", global_rect)
            self.selection_made.emit(global_rect)

            self.hide()
            logger.info("Overlay hidden after selection.")
        else:
            super().mouseReleaseEvent(event)

    # --- Rysowanie ---

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Ciemne półprzezroczyste tło na cały obszar overlayu
        overlay_color = QColor(0, 0, 0, 120)
        painter.fillRect(self.rect(), overlay_color)

        # Prostokąt zaznaczenia
        if not self._selection_rect.isNull():
            rect = self._selection_rect.normalized()
            pen = QPen(QColor(0, 180, 255), 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rect)

    # --- Logika pomocnicza ---

    def _update_selection_rect(self):
        if self._start_pos is None or self._current_pos is None:
            self._selection_rect = QRect()
            return

        self._selection_rect = QRect(self._start_pos, self._current_pos).normalized()

    def _cancel_selection(self):
        self._dragging = False
        self._start_pos = None
        self._current_pos = None
        self._selection_rect = QRect()
        self.hide()
