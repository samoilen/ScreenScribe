from __future__ import annotations

import json
import os
import logging
from dataclasses import dataclass, asdict

from app.paths import SETTINGS_FILE, CONFIG_DIR

logger = logging.getLogger("screenscribe.settings")


@dataclass
class Settings:
    capture_hotkey: str = "ctrl+shift+s"
    history_hotkey: str = "ctrl+shift+h"
    barcode_enabled: bool = True
    barcode_mode: str = "prefer_barcodes"  # prefer_barcodes | ocr_only


def load_settings() -> Settings:
    """Reads settings.json if present, otherwise returns defaults."""
    if not os.path.exists(SETTINGS_FILE):
        logger.info("Settings file not found, using defaults.")
        return Settings()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        logger.error("Failed to load settings: %s", e)
        return Settings()

    defaults = Settings()
    capture_hotkey = raw.get("capture_hotkey") or defaults.capture_hotkey
    history_hotkey = raw.get("history_hotkey") or defaults.history_hotkey
    barcode_enabled = raw.get("barcode_enabled")
    if barcode_enabled is None:
        barcode_enabled = defaults.barcode_enabled
    barcode_mode = raw.get("barcode_mode") or defaults.barcode_mode
    logger.info(
        "Loaded settings; capture_hotkey=%s history_hotkey=%s barcode_enabled=%s barcode_mode=%s",
        capture_hotkey,
        history_hotkey,
        barcode_enabled,
        barcode_mode,
    )
    return Settings(
        capture_hotkey=capture_hotkey,
        history_hotkey=history_hotkey,
        barcode_enabled=bool(barcode_enabled),
        barcode_mode=barcode_mode,
    )


def save_settings(settings: Settings) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(settings), f, ensure_ascii=False, indent=2)
    logger.info(
        "Saved settings to %s (capture_hotkey=%s, history_hotkey=%s, barcode_enabled=%s, barcode_mode=%s)",
        SETTINGS_FILE,
        settings.capture_hotkey,
        settings.history_hotkey,
        settings.barcode_enabled,
        settings.barcode_mode,
    )
