from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from app.paths import HISTORY_FILE, CONFIG_DIR


@dataclass
class HistoryEntry:
    timestamp: str
    text: str


class HistoryManager:
    """
    Prosta historia wyników OCR:
    - trzyma w pamięci listę wpisów
    - zapisuje/ładuje je z pliku JSON
    - dba o max_entries (np. 50)
    """

    def __init__(self, max_entries: int = 50):
        self.max_entries = max_entries
        self.entries: List[HistoryEntry] = []
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self._load()

    # --- API publiczne ---

    def add_entry(self, text: str) -> None:
        """Dodaje nowy wpis na początek historii."""
        if not text.strip():
            return

        entry = HistoryEntry(
            timestamp=datetime.now().isoformat(timespec="seconds"), text=text.strip()
        )
        # najnowsze na górze
        self.entries.insert(0, entry)
        # przycinamy do max_entries
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[: self.max_entries]
        self._save()

    def get_entries(self) -> List[HistoryEntry]:
        return list(self.entries)

    def clear(self) -> None:
        self.entries.clear()
        self._save()

    # --- I/O z plikiem JSON ---

    def _load(self) -> None:
        if not os.path.exists(HISTORY_FILE):
            return
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            print(f"[History] ERROR loading history: {e}")
            return

        entries: List[HistoryEntry] = []
        for item in raw:
            ts = item.get("timestamp") or ""
            text = item.get("text") or ""
            if not text:
                continue
            entries.append(HistoryEntry(timestamp=ts, text=text))

        self.entries = entries

    def _save(self) -> None:
        data = [asdict(e) for e in self.entries]
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[History] ERROR saving history: {e}")
