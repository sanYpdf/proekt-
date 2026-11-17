"""Inventory operations and input validation."""

from __future__ import annotations

from datetime import date
from typing import Iterable


FIELDS = {
    "type": "Тип",
    "name": "Наименование",
    "room": "Кабинет",
    "condition": "Состояние",
    "acquisition_date": "Дата поступления",
    "responsible_person": "Ответственный",
}
CONDITIONS = ("исправно", "требует ремонта", "списано")


class InventoryError(ValueError):
    """Raised when a requested inventory operation is invalid."""


class Inventory:
    def __init__(self, records: Iterable[dict[str, str]] = ()) -> None:
        self.records = [dict(record) for record in records]
        self._validate_existing_records()

    def _validate_existing_records(self) -> None:
        numbers = [record.get("inventory_number", "") for record in self.records]
        if any(not number for number in numbers) or len(numbers) != len(set(numbers)):
            raise InventoryError("В данных есть пустые или повторяющиеся инвентарные номера.")

    def all(self) -> list[dict[str, str]]:
        return sorted(self.records, key=lambda record: record["inventory_number"].casefold())

    def add(self, inventory_number: str, **fields: str) -> dict[str, str]:
        number = inventory_number.strip()
        if not number:
            raise InventoryError("Инвентарный номер не может быть пустым.")
        if self.get(number) is not None:
            raise InventoryError(f"Номер {number} уже используется.")
        record = self._validated_fields(fields)
        record["inventory_number"] = number
        self.records.append(record)
        return record

    def get(self, inventory_number: str) -> dict[str, str] | None:
        number = inventory_number.strip().casefold()
        return next(
            (record for record in self.records if record["inventory_number"].casefold() == number),
            None,
        )

    def search(self, query: str) -> list[dict[str, str]]:
        term = query.strip().casefold()
        if not term:
            return []
        return [
            record
            for record in self.all()
            if term in record["inventory_number"].casefold()
            or term in record["room"].casefold()
        ]

    def update(self, inventory_number: str, **changes: str) -> dict[str, str]:
        record = self.get(inventory_number)
        if record is None:
            raise InventoryError(f"Запись с номером {inventory_number} не найдена.")
        current_fields = {key: record[key] for key in FIELDS}
        validated = self._validated_fields({**current_fields, **changes})
        record.update(validated)
        return record

    def delete(self, inventory_number: str) -> dict[str, str]:
        record = self.get(inventory_number)
        if record is None:
            raise InventoryError(f"Запись с номером {inventory_number} не найдена.")
        self.records.remove(record)
        return record

    @staticmethod
    def _validated_fields(fields: dict[str, str]) -> dict[str, str]:
        unknown = set(fields) - set(FIELDS)
        if unknown:
            raise InventoryError("Переданы неизвестные поля записи.")
        cleaned: dict[str, str] = {}
        for key, label in FIELDS.items():
            value = str(fields.get(key, "")).strip()
            if key not in ("acquisition_date", "responsible_person") and not value:
                raise InventoryError(f"Поле «{label}» обязательно для заполнения.")
            cleaned[key] = value
        condition = cleaned["condition"].casefold()
        if condition not in CONDITIONS:
            options = ", ".join(CONDITIONS)
            raise InventoryError(f"Состояние должно быть одним из вариантов: {options}.")
        if cleaned["acquisition_date"]:
            try:
                date.fromisoformat(cleaned["acquisition_date"])
            except ValueError as exc:
                raise InventoryError("Дата поступления должна быть в формате ГГГГ-ММ-ДД.") from exc
        cleaned["condition"] = condition
        return cleaned
