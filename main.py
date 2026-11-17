"""Command-line interface for computer-class inventory tracking."""

from __future__ import annotations

from pathlib import Path

from inventory import FIELDS, Inventory, InventoryError
from storage import JsonStorage, StorageError


DATA_PATH = Path(__file__).resolve().parent / "data" / "inventory.json"


def _ask_fields(existing: dict[str, str] | None = None) -> dict[str, str]:
    values: dict[str, str] = {}
    for key, label in FIELDS.items():
        current = existing.get(key, "") if existing else ""
        hint = f" [{current}]" if current else ""
        answer = input(f"{label}{hint}: ").strip()
        values[key] = answer or current
    return values


def _show_record(record: dict[str, str]) -> None:
    print(f"\nИнвентарный номер: {record['inventory_number']}")
    for key, label in FIELDS.items():
        print(f"{label}: {record.get(key, '') or '—'}")


def _show_records(records: list[dict[str, str]]) -> None:
    if not records:
        print("Записи не найдены.")
        return
    print("\n№ | Инвентарный номер | Тип и наименование | Кабинет | Состояние")
    print("-" * 78)
    for index, record in enumerate(records, start=1):
        item = f"{record['type']} — {record['name']}"
        print(
            f"{index} | {record['inventory_number']} | {item} | "
            f"{record['room']} | {record['condition']}"
        )


def run(data_path: Path = DATA_PATH) -> None:
    storage = JsonStorage(data_path)
    try:
        inventory = Inventory(storage.load())
    except (StorageError, InventoryError) as exc:
        print(f"Ошибка загрузки данных: {exc}")
        return

    actions = {
        "1": "Показать всё оборудование",
        "2": "Добавить запись",
        "3": "Найти по номеру или кабинету",
        "4": "Изменить запись",
        "5": "Удалить запись",
        "0": "Выход",
    }
    while True:
        print("\n=== Учёт инвентаря компьютерных классов ===")
        for key, title in actions.items():
            print(f"{key}. {title}")
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            print("Работа завершена.")
            return
        try:
            if choice == "1":
                _show_records(inventory.all())
            elif choice == "2":
                number = input("Инвентарный номер: ")
                inventory.add(number, **_ask_fields())
                storage.save(inventory.records)
                print("Запись добавлена и сохранена.")
            elif choice == "3":
                query = input("Введите номер или кабинет: ")
                _show_records(inventory.search(query))
            elif choice == "4":
                number = input("Инвентарный номер записи: ")
                current = inventory.get(number)
                if current is None:
                    print("Запись не найдена.")
                    continue
                inventory.update(number, **_ask_fields(current))
                storage.save(inventory.records)
                print("Запись обновлена и сохранена.")
            elif choice == "5":
                number = input("Инвентарный номер записи: ")
                current = inventory.get(number)
                if current is None:
                    print("Запись не найдена.")
                    continue
                _show_record(current)
                if input("Удалить эту запись? (д/н): ").strip().casefold() in {"д", "да", "y", "yes"}:
                    inventory.delete(number)
                    storage.save(inventory.records)
                    print("Запись удалена.")
                else:
                    print("Удаление отменено.")
            else:
                print("Такого пункта нет. Выберите действие из меню.")
        except (InventoryError, StorageError) as exc:
            print(f"Не удалось выполнить действие: {exc}")


if __name__ == "__main__":
    try:
        run()
    except (EOFError, KeyboardInterrupt):
        print("\nРабота завершена.")
