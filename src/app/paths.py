from __future__ import annotations

import os
import sys


def get_base_dir() -> str:
    """
    Katalog bazowy dla danych użytkownika (config, logi):
    - w dev: katalog projektu (ScreenScribe)
    - w EXE: katalog z ScreenScribe.exe
    """
    if getattr(sys, "frozen", False):
        # PyInstaller: katalog z exe
        return os.path.dirname(sys.executable)

    # Dev: wyliczamy katalog projektu na podstawie położenia pliku
    current_file = os.path.abspath(__file__)
    app_dir = os.path.dirname(current_file)  # ...\src\app
    src_dir = os.path.dirname(app_dir)  # ...\src
    project_dir = os.path.dirname(src_dir)  # ...\ScreenScribe
    return project_dir


def get_bundle_dir() -> str:
    """
    Katalog z zasobami spakowanymi przez PyInstaller (resources, tesseract_bundle):
    - w EXE: sys._MEIPASS (w PyInstaller 6.17+ to będzie zazwyczaj ...\_internal)
    - w dev: taki sam jak BASE_DIR
    """
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return meipass
        # Fallback: katalog exe
        return os.path.dirname(sys.executable)

    return get_base_dir()


BASE_DIR = get_base_dir()  # tutaj trzymamy config, logi
BUNDLE_DIR = get_bundle_dir()  # tutaj szukamy zasobów spakowanych przez PyInstaller

# Katalogi runtime
CONFIG_DIR = os.path.join(BASE_DIR, "config")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ścieżki do zasobów (z paczki)
APP_ICON = os.path.join(BUNDLE_DIR, "resources", "icons", "screenscribe.ico")
TESSERACT_EXE = os.path.join(BUNDLE_DIR, "tesseract_bundle", "tesseract.exe")

# Pliki konfiguracyjne
HISTORY_FILE = os.path.join(CONFIG_DIR, "history.json")


def ensure_runtime_dirs() -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
