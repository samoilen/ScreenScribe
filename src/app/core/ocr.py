from __future__ import annotations

import os
import logging
from typing import Optional

import pytesseract
from PIL import Image

from app.paths import TESSERACT_EXE

logger = logging.getLogger("screenscribe.ocr")

_initialized = False


def init_tesseract():
    """
    Jednorazowa konfiguracja pytesseract:
    - sprawdza, czy tesseract.exe istnieje
    - ustawia ścieżkę w pytesseract
    """
    global _initialized

    if _initialized:
        return

    if not os.path.exists(TESSERACT_EXE):
        logger.error("tesseract.exe not found at %s", TESSERACT_EXE)
        return

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
    _initialized = True
    logger.info("Using tesseract at: %s", TESSERACT_EXE)


def image_file_to_text(path: str, lang: str = "eng+pol") -> Optional[str]:
    """
    Wykonuje OCR na pliku obrazka (PNG/JPG) i zwraca tekst.
    Zwraca None, jeśli coś pójdzie nie tak lub tekst jest pusty.
    """
    init_tesseract()

    if not os.path.exists(path):
        logger.error("Image file not found: %s", path)
        return None

    try:
        img = Image.open(path)
    except Exception as e:
        logger.exception("Failed to open image: %s", e)
        return None

    try:
        text = pytesseract.image_to_string(img, lang=lang)
    except Exception as e:
        logger.exception("Tesseract error: %s", e)
        return None

    cleaned = text.strip()
    logger.info("OCR raw length=%d cleaned length=%d", len(text), len(cleaned))

    return cleaned or None
