# ScreenScribe
![alt text](ScreenScribe-2.ico)

Lightweight Windows tray app to grab a screen region, run OCR (bundled Tesseract), and copy the result to the clipboard with a searchable history and configurable global hotkeys.

## Features
- Global hotkeys (defaults): capture `ctrl+shift+s`, history `ctrl+shift+h` (configurable in Settings).
- Region selection overlay with per-monitor capture and OCR (English+Polish trained data bundled).
- Clipboard copy and history list (double-click to copy); search box; entries numbered newest-first.
- Settings stored locally (`config/settings.json`); single-instance guard; auto-rotating log (7 days).
- Bundled Tesseract (`tesseract_bundle`) and resources; no external installs required for end users.

## Quick Start (dev)
1) Requirements: Python 3.11+, virtualenv.  
2) Install deps: `pip install -r requirements.txt` (includes PySide6, pillow, pytesseract, keyboard).  
3) Run from repo root: `python -m app.main` (cwd `src/`).  
4) Use tray menu:
   - `Capture text now` – draw a rectangle, text goes to clipboard/history.
   - `History...` – view/search previous results; double-click copies.
   - `Settings...` – change global hotkeys.
   - `Exit` – quit.

## Hotkeys
- Capture: default `ctrl+shift+s`.
- History: default `ctrl+shift+h`.
- Change via tray → `Settings...`. Saved to `config/settings.json`; applied immediately.

## Runtime Files
- `config/history.json` – latest entries (capped at 50).
- `config/settings.json` – hotkeys.
- `last_capture.png` – overwritten with the last screenshot.
- `logs/screenscribe.log` – rotates by age (7 days; recreated on next start).

## Single Instance
The app uses a shared-memory guard; if already running, a warning is shown and the second instance exits.

## Build (PyInstaller)
Spec file: `ScreenScribe.spec` (includes resources and tesseract bundle).
Steps:
1) `pip install pyinstaller`.
2) `pyinstaller ScreenScribe.spec`
3) Output: `dist/ScreenScribe/ScreenScribe.exe` plus `resources/` and `tesseract_bundle/`.

## Distributing to another user
- Zip the whole `dist/ScreenScribe` folder and share.  
- The user unzips and runs `ScreenScribe.exe`; no Python/pip needed.  
- First run may prompt for permission to register a global hotkey (keyboard hook).

## Project Layout (key paths)
- `src/app/main.py` – entrypoint, single-instance guard, logging, wiring.
- `src/app/gui/` – tray, overlay, history window, settings dialog.
- `src/app/core/` – capture, OCR, history storage, hotkeys, settings.
- `resources/` – icons; `tesseract_bundle/` – Tesseract exe + data.

## Known Tips
- If a hotkey conflicts, pick a different combo in Settings.
- If OCR fails, verify `tesseract_bundle/tesseract.exe` and language files are present next to the EXE.


## To do
- wyłączenie aplikacji po 11 zaznaczeniach pustej prstrzeni 