from __future__ import annotations

import os
from typing import Optional

import pytesseract
from PIL import Image

from app.paths import TESSERACT_EXE

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
        print(f"[OCR] ERROR: tesseract.exe not found at {TESSERACT_EXE}")
        return

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
    _initialized = True
    print(f"[OCR] Using tesseract at: {TESSERACT_EXE}")


def image_file_to_text(path: str, lang: str = "eng+pol") -> Optional[str]:
    """
    Wykonuje OCR na pliku obrazka (PNG/JPG) i zwraca tekst.
    Zwraca None, jeśli coś pójdzie nie tak lub tekst jest pusty.
    """
    init_tesseract()

    if not os.path.exists(path):
        print(f"[OCR] ERROR: image file not found: {path}")
        return None

    try:
        img = Image.open(path)
    except Exception as e:
        print(f"[OCR] ERROR: failed to open image: {e}")
        return None

    try:
        text = pytesseract.image_to_string(img, lang=lang)
    except Exception as e:
        print(f"[OCR] ERROR: tesseract error: {e}")
        return None

    cleaned = text.strip()
    print("[OCR] RAW TEXT:")
    print(text)
    print("[OCR] CLEANED:")
    print(cleaned)

    return cleaned or None
