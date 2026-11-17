import json

from storage import JsonStorage


def test_missing_file_loads_empty_list(tmp_path):
    assert JsonStorage(tmp_path / "missing.json").load() == []


def test_save_and_load_round_trip(tmp_path):
    storage = JsonStorage(tmp_path / "nested" / "inventory.json")
    records = [{"inventory_number": "PC-1", "name": "Компьютер"}]
    storage.save(records)
    assert storage.load() == records


def test_saved_json_is_utf8_and_readable(tmp_path):
    path = tmp_path / "inventory.json"
    JsonStorage(path).save([{"name": "Компьютер"}])
    assert json.loads(path.read_text(encoding="utf-8"))[0]["name"] == "Компьютер"
