import sys
from pathlib import Path

# Dodaj katalog src do sys.path, aby importy app.* działy w testach
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_imports():
    # Sprawdzamy, czy kluczowe moduły dają się zaimportować
    from app.core.ocr import extract_text_from_file, image_file_to_text
    from app.core.settings import Settings, load_settings, save_settings
    from app.core.barcode import decode_barcodes, BarcodeResult
    from app.gui.tray import ScreenScribeTray
    from app.gui.overlay import SelectionOverlay

    assert extract_text_from_file is not None
    assert image_file_to_text is not None
    assert Settings is not None and load_settings is not None and save_settings is not None
    assert decode_barcodes is not None and BarcodeResult is not None
    assert ScreenScribeTray is not None
    assert SelectionOverlay is not None
