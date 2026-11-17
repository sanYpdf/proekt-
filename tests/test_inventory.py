import pytest

from inventory import Inventory, InventoryError


def sample_fields():
    return {
        "type": "ПК",
        "name": "Тестовый компьютер",
        "room": "101",
        "condition": "исправно",
        "acquisition_date": "2024-01-15",
        "responsible_person": "Иванов И. И.",
    }


def test_add_and_find_record():
    inventory = Inventory()
    inventory.add("PC-1", **sample_fields())
    assert inventory.get("pc-1")["name"] == "Тестовый компьютер"


def test_duplicate_inventory_number_is_rejected():
    inventory = Inventory()
    inventory.add("PC-1", **sample_fields())
    with pytest.raises(InventoryError, match="уже используется"):
        inventory.add("PC-1", **sample_fields())


def test_search_matches_room_and_number():
    inventory = Inventory()
    inventory.add("PC-101", **sample_fields())
    assert len(inventory.search("101")) == 1
    assert len(inventory.search("pc-")) == 1


def test_update_changes_record():
    inventory = Inventory()
    inventory.add("PC-1", **sample_fields())
    inventory.update("PC-1", room="204")
    assert inventory.get("PC-1")["room"] == "204"


def test_delete_removes_record():
    inventory = Inventory()
    inventory.add("PC-1", **sample_fields())
    inventory.delete("PC-1")
    assert inventory.get("PC-1") is None


@pytest.mark.parametrize("fields", [
    {**sample_fields(), "name": ""},
    {**sample_fields(), "condition": "неизвестно"},
    {**sample_fields(), "acquisition_date": "15.01.2024"},
])
def test_invalid_fields_are_rejected(fields):
    with pytest.raises(InventoryError):
        Inventory().add("PC-1", **fields)
