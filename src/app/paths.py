import os
import sys


def get_base_dir() -> str:
    """
    Zwraca katalog bazowy aplikacji:
    - w trybie EXE (PyInstaller) -> folder z ScreenScribe.exe
    - w trybie dev (python -m app.main) -> katalog projektu (ScreenScribe)
    """
    if getattr(sys, "frozen", False):  # uruchomione jako EXE
        return os.path.dirname(sys.executable)

    # uruchomione jako skrypt z src/app/
    current_file = os.path.abspath(__file__)
    app_dir = os.path.dirname(current_file)  # .../src/app
    project_dir = os.path.dirname(os.path.dirname(app_dir))  # .../ScreenScribe
    return project_dir


BASE_DIR = get_base_dir()

# Folder z Tesseractem (u mnei: ScreenScribe/tesseract_bundle/tesseract.exe)
TESSERACT_EXE = os.path.join(BASE_DIR, "tesseract_bundle", "tesseract.exe")

# Folder z zasobami (ikony itd.)
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
ICONS_DIR = os.path.join(RESOURCES_DIR, "icons")
APP_ICON = os.path.join(ICONS_DIR, "screenscribe.ico")

# Foldery na config i logi (będziemy używać później)
CONFIG_DIR = os.path.join(BASE_DIR, "config")
HISTORY_FILE = os.path.join(CONFIG_DIR, "history.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
LOGS_DIR = os.path.join(BASE_DIR, "logs")


def ensure_runtime_dirs():
    """Tworzy katalogi config/logs jeśli nie istnieją."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
