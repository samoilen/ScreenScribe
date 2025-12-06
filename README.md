# ScreenScribe

Lekka aplikacja na Windows do wycinania fragmentu ekranu, OCR (Tesseract) i kopiowania tekstu do schowka. Działa z zasobami dołączonymi lokalnie (Tesseract w `tesseract_bundle`), pozwala zmieniać globalny skrót do przechwytywania i trzyma historię wyników.

## Uruchomienie w dev
1. Wymagania: Python 3.11+, środowisko virtualenv.
2. `pip install -r requirements.txt` (pakiety: PySide6, pillow, pytesseract, keyboard).
3. `python -m app.main` z katalogu `src/`.
4. Ikona w zasobniku systemowym → menu:
   - `Capture text now` – zaznacz prostokąt, wynik trafia do schowka i historii.
   - `History...` – lista poprzednich wyników, podwójne kliknięcie kopiuje do schowka.
   - `Settings...` – zmiana globalnego skrótu (domyślnie `ctrl+shift+s`), zapis w `config/settings.json`.
   - `Exit` – wyjście.

## Zmiana skrótu
- Tray → `Settings...` → wpisz np. `ctrl+alt+c` lub `print screen` → `Save`.
- Nowy skrót działa natychmiast i zapisuje się w `config/settings.json`.

## Pliki runtime
- `config/history.json` – historia OCR.
- `config/settings.json` – ustawienia skrótu.
- `last_capture.png` – ostatni zrzut.
- `logs/screenscribe.log` – log aplikacji.

## Budowa EXE (PyInstaller)
W repo jest `ScreenScribe.spec` skonfigurowany na bundling zasobów:
1. Zainstaluj PyInstaller: `pip install pyinstaller`.
2. Uruchom w katalogu głównym: `pyinstaller ScreenScribe.spec`.
3. Artefakty: `dist/ScreenScribe/ScreenScribe.exe` plus dołączone foldery `resources`, `tesseract_bundle`.

## Dystrybucja dla innej osoby
- Przekaż folder `dist/ScreenScribe` (całość razem z `resources` i `tesseract_bundle`). Nic nie trzeba doinstalowywać (Tesseract jest spakowany).
- Uruchomienie: `ScreenScribe.exe`. Przy pierwszym starcie może poprosić o uprawnienia do rejestrowania globalnych skrótów (keyboard hook).
- Wymagania: Windows 10/11 z uprawnieniami do hooków klawiatury; ekranowy overlay działa na aktywnym monitorze.

## Znane wskazówki
- Jeśli globalny skrót nie reaguje, sprawdź, czy nie koliduje z inną aplikacją i spróbuj innej kombinacji w Settings.
- Przy problemach z OCR upewnij się, że `tesseract_bundle/tesseract.exe` istnieje w folderze obok EXE i że pliki językowe (`eng.traineddata`, `pol.traineddata`) są w `tesseract_bundle/tessdata`.
