# ScreenScribe – Detailed Documentation (EN)

## Overview
ScreenScribe is a Windows tray application that lets users select a screen region, perform OCR, copy the result to the clipboard, and browse/search a history of recognized text. It bundles Tesseract and resources, needs no external installs for end users, and enforces a single running instance.

## Architecture
- Entry: `src/app/main.py` – logging, single-instance guard, QApplication, tray wiring, hotkeys.
- GUI:
  - `gui/tray.py` – tray menu, capture flow, OCR worker thread, settings/hotkeys, history invocation.
  - `gui/overlay.py` – full-screen selection overlay (per monitor).
  - `gui/history_window.py` – history list with search, numbering, double-click copy, clear.
  - `gui/settings_dialog.py` – edit capture/history hotkeys.
- Core:
  - `core/capture.py` – per-screen grab; saves to `last_capture.png`.
  - `core/ocr.py` – initializes bundled Tesseract, runs OCR.
  - `core/history.py` – in-memory list + JSON persistence with max entries.
  - `core/hotkey.py` – global hotkeys (capture/history) via `keyboard`.
  - `core/settings.py` – load/save settings JSON.
- Paths/resources: `app/paths.py` determines base/bundle dirs, resource locations, config/log paths. `resources/` holds icons; `tesseract_bundle/` ships Tesseract exe and language data.
- Packaging: `ScreenScribe.spec` for PyInstaller; adds resources and Tesseract bundle.

## Runtime Behavior
- Hotkeys: capture (default `ctrl+shift+s`), history (default `ctrl+shift+h`), configurable in Settings dialog; stored in `config/settings.json`.
- Capture flow: overlay selection → capture to `last_capture.png` (per monitor) → OCR in worker thread → clipboard set → history entry added.
- History: JSON at `config/history.json`, capped at 50 entries; UI shows numbered entries (newest=1), search filters live; double-click copies text.
- Logging: `logs/screenscribe.log` with stdout mirror; log file is deleted if older than 7 days on startup; recreated afterward.
- Single instance: shared-memory guard blocks second launch and shows warning.

## Files and Persistence
- `config/settings.json` – capture/history hotkeys.
- `config/history.json` – recent OCR entries (timestamp + text), trimmed to max entries.
- `last_capture.png` – overwritten with the last screenshot.
- `logs/screenscribe.log` – recreated if older than 7 days.

## Hotkey Management
- Two global hotkeys registered via `keyboard` in `HotkeyManager`.
- Settings dialog updates both; changes apply immediately and persist to settings JSON.
- Tray connects `history_requested` to open the history window; `capture_requested` starts overlay capture.

## Build and Distribution
- Build: `pyinstaller ScreenScribe.spec` (bundles resources and Tesseract).
- Output: `dist/ScreenScribe/ScreenScribe.exe` plus `resources/` and `tesseract_bundle/`.
- Distribution: zip the entire `dist/ScreenScribe` folder; users unzip and run `ScreenScribe.exe` (no Python/pip needed). Windows may ask for keyboard hook permission for global hotkeys.

## Usage Tips
- If a hotkey conflicts, pick another combination in Settings.
- For OCR issues, ensure `tesseract_bundle/tesseract.exe` and `tessdata` are present next to the EXE.
- History search is substring, case-insensitive; entries are numbered for compact display.
- Only one `last_capture.png` is kept; storage footprint stays minimal.

## Future Notes
- Autostart can be added via HKCU Run or Startup folder if desired.
- Log rotation is age-based (7 days); can be extended to size-based if needed.
