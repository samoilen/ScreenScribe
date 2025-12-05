from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QPoint, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont


class SelectionOverlay(QWidget):
    """
    Pełnoekranowy overlay do zaznaczania prostokąta na ekranie.
    - LPM: zacznij zaznaczenie
    - przeciągnij: prostokąt
    - puść LPM: potwierdź
    - ESC: anuluj
    """

    selection_made = Signal(QRect)  # sygnał: użytkownik zakończył zaznaczenie

    def __init__(self, parent=None):
        super().__init__(parent)

        # Okno bez ramek, zawsze na wierzchu, bez ikony na pasku zadań
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)

        # Pozwala używać kanału alfa (przezroczystość)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # To jest KLUCZ do działania ESC – okno będzie przyjmować focus z klawiatury
        self.setFocusPolicy(Qt.StrongFocus)

        self._start_point: QPoint | None = None
        self._end_point: QPoint | None = None
        self._active = False

    # --- Publiczny start ---

    def start_capture(self):
        """
        Wywołaj to, żeby zacząć zaznaczanie.
        Czyścimy stan i pokazujemy overlay na pełnym ekranie.
        """
        self._start_point = None
        self._end_point = None
        self._active = True

        # Pełny ekran, na wierzchu
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self.setFocus()

    def _current_rect(self) -> QRect | None:
        if not self._start_point or not self._end_point:
            return None
        return QRect(self._start_point, self._end_point).normalized()

    def _cancel(self):
        """Anulowanie zaznaczenia (ESC lub zbyt mały prostokąt)."""
        self._active = False
        self._start_point = None
        self._end_point = None
        self.hide()

    # --- Obsługa myszy i klawiatury ---

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_point = event.position().toPoint()
            self._end_point = self._start_point
            self.update()

    def mouseMoveEvent(self, event):
        if self._start_point:
            self._end_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._start_point:
            self._end_point = event.position().toPoint()
            rect = self._current_rect()

            if rect and rect.width() > 5 and rect.height() > 5:
                # poprawne zaznaczenie
                self._active = False
                self.hide()
                print(
                    f"[Overlay] Emitting selection: x={rect.x()}, "
                    f"y={rect.y()}, w={rect.width()}, h={rect.height()}"
                )
                self.selection_made.emit(rect)
            else:
                # prostokąt za mały – traktujemy jak anulowanie
                print("[Overlay] Selection too small, cancelling")
                self._cancel()

    def keyPressEvent(self, event):
        print("[Overlay] keyPress:", event.key())
        if event.key() == Qt.Key_Escape:
            print("[Overlay] ESC pressed – cancelling selection")
            self._cancel()

    # --- Rysowanie overlayu ---

    def paintEvent(self, event):
        if not self._active:
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)

        # 1) PRZEŹROCZYSTOŚĆ: 40 zamiast 70/100 – ekran powinien być TYLKO delikatnie przyciemniony
        overlay_color = QColor(0, 0, 0, 50)  # im mniejsza alfa, tym jaśniej
        painter.fillRect(self.rect(), overlay_color)

        rect = self._current_rect()
        if rect:
            # 2) Wycinamy prostokąt (okno „jasności”)
            clear_color = QColor(0, 0, 0, 0)
            painter.fillRect(rect, clear_color)

            # 3) Ramka prostokąta – biała linia
            pen = QPen(QColor(255, 255, 255), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(rect)

        # 4) Tekst z instrukcją w lewym górnym rogu
        painter.setPen(QColor(255, 255, 255, 220))
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        hint_text = "Drag to select area, press ESC to cancel"
        margin = 20
        painter.drawText(margin, margin + 20, hint_text)
