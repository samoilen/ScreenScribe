# ScreenScribe – Dokumentacja szczegolowa (PL)

## Opis
ScreenScribe to aplikacja tray na Windows, ktora pozwala zaznaczyc fragment ekranu, wykryc kody kreskowe/QR offline (zxing-cpp), wykonac OCR (Tesseract), skopiowac wynik do schowka oraz przegladac/wyszukiwac historie tekstow. Tesseract i zasoby sa dolaczone, aplikacja wymusza pojedyncza instancje.

## Architektura
- Wejscie: `src/app/main.py` – logowanie, straznik pojedynczej instancji, QApplication, tray, hotkeys.
- GUI:
  - `gui/tray.py` – menu traya, przebieg capture, watek OCR/barcode, ustawienia/hotkeys, wywolanie historii.
  - `gui/overlay.py` – pelnoekranowy overlay do zaznaczania (per monitor).
  - `gui/history_window.py` – historia z wyszukiwaniem, numeracja, kopiowanie (double-click/Ctrl+C), przycisk Clear.
  - `gui/settings_dialog.py` – edycja skrotow capture/history oraz opcji barcode.
- Core:
  - `core/capture.py` – zrzut ekranu per monitor, zapis do `last_capture.png`.
  - `core/ocr.py` – pipeline barcode-first (zxing-cpp) z fallbackiem OCR (Tesseract).
  - `core/barcode.py` – wrapper zxing-cpp i dataclass z wynikiem.
  - `core/history.py` – lista w pamieci + zapis/odczyt JSON, limit wpisow.
  - `core/hotkey.py` – globalne skroty (capture/history) przez `keyboard`.
  - `core/settings.py` – odczyt/zapis ustawien.
- Sciezki/zasoby: `app/paths.py` wylicza katalogi bazowe/bundle, sciezki do ikon, config i logow. `resources/` zawiera ikone; `tesseract_bundle/` zawiera Tesseract i dane jezykowe.
- Pakowanie: `ScreenScribe.spec` dla PyInstaller; dodaje zasoby, bundle Tesseract, hiddenimports dla `keyboard` i `zxingcpp`.

## Zachowanie w czasie dzialania
- Skroty: capture (domyslnie `ctrl+shift+s`), history (domyslnie `ctrl+shift+h`), konfigurowalne w Settings; zapis w `config/settings.json`.
- Barcode pipeline: przy ustawieniu `prefer_barcodes` najpierw zxing-cpp, jesli znajdzie kody, zwraca linie `[FORMAT] tekst`; jesli nie ma kodow, fallback do OCR. Tryb `ocr_only` pomija barcode.
- Capture: zaznaczenie -> zapis do `last_capture.png` -> barcode/OCR w watku -> schowek -> wpis do historii.
- Historia: `config/history.json`, max 50 wpisow; numeracja (1 = najnowszy), szukanie substring, pelny tekst zawijany; double-click lub Ctrl+C kopiuje.
- Logowanie: `logs/screenscribe.log` + stdout; log kasowany, gdy starszy niz 7 dni, przy starcie tworzony na nowo.
- Pojedyncza instancja: straznik shared-memory blokuje drugie uruchomienie i pokazuje ostrzezenie.

## Pliki i trwalosc
- `config/settings.json` – skroty capture/history i ustawienia barcode (enabled, mode).
- `config/history.json` – wpisy (timestamp + text), przyciete do limitu.
- `last_capture.png` – nadpisywany ostatni zrzut.
- `logs/screenscribe.log` – czyszczony po 7 dniach.

## Zarzadzanie skrotami
- Dwa globalne skroty rejestrowane przez `HotkeyManager` (biblioteka `keyboard`).
- Settings aktualizuje skroty i barcode; zmiany dzialaja od razu, zapis do JSON.
- `history_requested` otwiera okno historii; `capture_requested` startuje overlay.

## Budowa i dystrybucja
- Budowa: `pyinstaller ScreenScribe.spec` (pakuje zasoby, Tesseract, hiddenimports).
- Wynik: `dist/ScreenScribe/ScreenScribe.exe` z katalogami `resources/` i `tesseract_bundle/`.
- Dystrybucja: spakuj caly `dist/ScreenScribe` do zip; uzytkownik rozpakowuje i uruchamia `ScreenScribe.exe` (bez Python/pip). Windows moze pytac o pozwolenie na globalne skroty (hook klawiatury).

## Wskazowki
- Kolizja skrotow: ustaw inna kombinacje w Settings.
- Problemy z OCR: sprawdz `tesseract_bundle/tesseract.exe` i pliki jezykowe w `tesseract_bundle/tessdata`.
- Barcode: dziala offline; tekst traktowany zwykle (brak wykonywania).
- Historia: wyszukiwanie po fragmencie, numeracja dla oszczedzenia miejsca.
- Zuzycie miejsca: jeden `last_capture.png`; log czyszczony po 7 dniach.

## Uwagi na przyszlosc
- Autostart mozna dodac wpisem w HKCU Run lub przez skrot w Autostarcie.
- Mozliwa rotacja logu po rozmiarze, jesli bedzie potrzebne.
