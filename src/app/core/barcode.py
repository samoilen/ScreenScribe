from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Tuple

from PIL import Image

logger = logging.getLogger("screenscribe.barcode")

try:
    import zxingcpp  # type: ignore
except Exception as e:  # pragma: no cover - optional dependency
    zxingcpp = None
    logger.error("zxing-cpp not available: %s", e)


@dataclass
class BarcodeResult:
    format: str
    text: str
    position: List[Tuple[int, int]] | None = None


def decode_barcodes(image: Image.Image) -> List[BarcodeResult]:
    """
    Dekoduje kody kreskowe/QR z obrazu PIL przy u‘>yciu zxing-cpp.
    Zwraca listŽt BarcodeResult; pustŽt listŽt w razie b‘'ŽdŽw.
    """
    if zxingcpp is None:
        logger.warning("decode_barcodes called without zxing-cpp installed.")
        return []

    try:
        if image.mode not in ("RGB", "RGBA", "L"):
            image = image.convert("RGB")
        results = zxingcpp.read_barcodes(image)
    except Exception as e:
        logger.exception("Barcode decoding failed: %s", e)
        return []

    decoded: List[BarcodeResult] = []
    for res in results:
        fmt = getattr(res.format, "name", str(res.format))
        text = res.text or ""
        pos = None
        try:
            pts = getattr(res, "position", None)
            if pts:
                pos = [(int(p.x), int(p.y)) for p in pts]
        except Exception:
            pos = None
        decoded.append(BarcodeResult(format=fmt, text=text, position=pos))

    logger.info("Decoded %d barcodes: %s", len(decoded), [r.format for r in decoded])
    return decoded
