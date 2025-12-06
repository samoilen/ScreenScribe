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

    default_hotkey = Settings().capture_hotkey
    capture_hotkey = raw.get("capture_hotkey") or default_hotkey
    logger.info("Loaded settings; hotkey=%s", capture_hotkey)
    return Settings(capture_hotkey=capture_hotkey)


def save_settings(settings: Settings) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(asdict(settings), f, ensure_ascii=False, indent=2)
    logger.info("Saved settings to %s (hotkey=%s)", SETTINGS_FILE, settings.capture_hotkey)
