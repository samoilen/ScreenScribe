from __future__ import annotations

import os
import logging
from typing import Optional, List

import pytesseract
from PIL import Image

from app.paths import TESSERACT_EXE
from app.core.barcode import decode_barcodes
from app.core.settings import Settings

logger = logging.getLogger("screenscribe.ocr")

_initialized = False
DEFAULT_LANG = "eng+pol"


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


def image_file_to_text(path: str, lang: str = DEFAULT_LANG) -> Optional[str]:
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


def extract_text_from_file(
    path: str, settings: Settings, lang: str = DEFAULT_LANG
) -> Optional[str]:
    """
    Pipeline: opcjonalnie dekoduje kody, potem ewentualnie fallback OCR.
    UwzglŽdniamy ustawienia:
    - barcode_enabled False -> tylko OCR
    - barcode_mode == "ocr_only" -> tylko OCR
    - barcode_mode == "prefer_barcodes" -> najpierw kody, fallback do OCR
    """
    if not os.path.exists(path):
        logger.error("Image file not found: %s", path)
        return None

    try:
        img = Image.open(path)
    except Exception as e:
        logger.exception("Failed to open image: %s", e)
        return None

    # Barcode path
    if settings.barcode_enabled and settings.barcode_mode == "prefer_barcodes":
        logger.info(
            "Wykrywanie kodów włączone, mode=%s. Najpierw próba kodów.",
            settings.barcode_mode,
        )
        barcodes = decode_barcodes(img)
        if barcodes:
            lines = _format_barcodes(barcodes)
            logger.info(
                "Znaleziono kody (%d). Zwracam tekst z kodów zamiast OCR.",
                len(barcodes),
            )
            return "\n".join(lines)
        logger.info("No barcodes detected, falling back to OCR.")

    if settings.barcode_enabled and settings.barcode_mode == "ocr_only":
        logger.info("Barcode detection enabled but mode=ocr_only; pomijam kody.")

    # OCR fallback / only path
    return _ocr_image(img, lang=lang)


def _ocr_image(img: Image.Image, lang: str = DEFAULT_LANG) -> Optional[str]:
    init_tesseract()
    try:
        text = pytesseract.image_to_string(img, lang=lang)
    except Exception as e:
        logger.exception("Tesseract error: %s", e)
        return None

    cleaned = text.strip()
    logger.info("OCR raw length=%d cleaned length=%d", len(text), len(cleaned))
    return cleaned or None


def _format_barcodes(barcodes: List) -> List[str]:
    lines: List[str] = []
    for b in barcodes:
        fmt = b.format or "UNKNOWN"
        txt = b.text or ""
        lines.append(f"[{fmt}] {txt}")
    return lines
