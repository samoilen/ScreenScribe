# ScreenScribe – Dokumentacja szczegółowa (PL)

## Opis
ScreenScribe to aplikacja tray na Windows, która pozwala zaznaczyć fragment ekranu, wykonać OCR, skopiować wynik do schowka oraz przeglądać/wyszukiwać historię rozpoznanego tekstu. Tesseract i zasoby są dołączone, więc użytkownik końcowy nie musi nic instalować. Aplikacja wymusza pojedynczą instancję.

## Architektura
- Wejście: `src/app/main.py` – logowanie, strażnik pojedynczej instancji, QApplication, tray, hotkeys.
- GUI:
  - `gui/tray.py` – menu traya, przebieg capture, wątek OCR, ustawienia/hotkeys, wywołanie historii.
  - `gui/overlay.py` – pełnoekranowy overlay do zaznaczania (per monitor).
  - `gui/history_window.py` – historia z wyszukiwaniem, numeracją, double-click kopiującym, przyciskiem Clear.
  - `gui/settings_dialog.py` – edycja skrótów capture/history.
- Core:
  - `core/capture.py` – zrzut ekranu per monitor, zapis do `last_capture.png`.
  - `core/ocr.py` – inicjalizacja dołączonego Tesseracta, OCR.
  - `core/history.py` – lista w pamięci + zapis/odczyt JSON, limit wpisów.
  - `core/hotkey.py` – globalne skróty (capture/history) przez `keyboard`.
  - `core/settings.py` – odczyt/zapis ustawień.
- Ścieżki/zasoby: `app/paths.py` wylicza katalogi bazowe/bundle, ścieżki do ikon, config i logów. `resources/` zawiera ikonę; `tesseract_bundle/` zawiera Tesseract i dane językowe.
- Pakowanie: `ScreenScribe.spec` dla PyInstaller, dodaje zasoby i bundle Tesseract.

## Zachowanie w czasie działania
- Skróty: capture (domyślnie `ctrl+shift+s`), history (domyślnie `ctrl+shift+h`), konfigurowalne w Settings; zapis w `config/settings.json`.
  - `history_requested` otwiera okno historii, `capture_requested` startuje overlay.
- Capture: zaznaczenie → zapis do `last_capture.png` (per monitor) → OCR w wątku → schowek → wpis do historii.
- Historia: `config/history.json`, max 50 wpisów; UI numeruje wpisy (1 = najnowszy), wyszukiwanie substring, case-insensitive; double-click kopiuje tekst.
- Logowanie: `logs/screenscribe.log` + stdout; log kasowany, gdy starszy niż 7 dni, przy starcie tworzony na nowo.
- Pojedyncza instancja: strażnik shared-memory blokuje drugie uruchomienie i pokazuje ostrzeżenie.

## Pliki i trwałość
- `config/settings.json` – skróty capture/history.
  - Minimalna struktura: `{"capture_hotkey": "...", "history_hotkey": "..."}`.
- `config/history.json` – wpisy OCR (timestamp + text), przycięte do limitu.
- `last_capture.png` – nadpisywany ostatni zrzut.
- `logs/screenscribe.log` – kasowany po 7 dniach (wiek), potem tworzony od nowa.

## Zarządzanie skrótami
- Dwa globalne skróty rejestrowane przez `HotkeyManager` (biblioteka `keyboard`).
- Ustawienia w dialogu `Settings...`; zapis do JSON, zmiany działają natychmiast.
- Skróty wywołują: capture -> overlay/ocr; history -> okno historii.

## Budowa i dystrybucja
- Budowa: `pyinstaller ScreenScribe.spec` (pakuje zasoby i Tesseract).
- Wynik: `dist/ScreenScribe/ScreenScribe.exe` z katalogami `resources/` i `tesseract_bundle/`.
- Dystrybucja: spakuj cały `dist/ScreenScribe` do zip; użytkownik rozpakowuje i uruchamia `ScreenScribe.exe` (bez Python/pip). Windows może pytać o pozwolenie na globalne skróty (hook klawiatury).

## Wskazówki
- Kolizja skrótów: ustaw inną kombinację w Settings.
- Problemy z OCR: sprawdź obecność `tesseract_bundle/tesseract.exe` i plików językowych w `tesseract_bundle/tessdata`.
- Historia: szukanie po fragmencie tekstu, numeracja dla oszczędzenia miejsca.
- Zużycie miejsca: tylko jeden `last_capture.png`; log czyści się po 7 dniach.

## Uwagi na przyszłość
- Autostart można dodać wpisem w HKCU Run lub przez skrót w Autostarcie.
- Możliwa rotacja logu także po rozmiarze, jeśli będzie potrzebne.
