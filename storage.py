"""JSON storage for the inventory application."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class StorageError(Exception):
    """Raised when inventory data cannot be read or written safely."""


class JsonStorage:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> list[dict[str, str]]:
        if not self.path.exists():
            return []
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data: Any = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Не удалось прочитать файл данных: {exc}") from exc
        if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
            raise StorageError("Файл данных имеет неверный формат: ожидался список записей.")
        return data

    def save(self, records: list[dict[str, str]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=self.path.parent, delete=False
            ) as file:
                temporary_path = Path(file.name)
                json.dump(records, file, ensure_ascii=False, indent=2)
                file.write("\n")
            os.replace(temporary_path, self.path)
        except OSError as exc:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise StorageError(f"Не удалось сохранить файл данных: {exc}") from exc
