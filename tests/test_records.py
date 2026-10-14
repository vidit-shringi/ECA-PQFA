from backend.app.services.records import create, delete
from backend.app.services.repository import init_db


def test_ids_not_reused_after_delete(tmp_path, monkeypatch):
    db = tmp_path / "records.sqlite3"
    monkeypatch.setattr("backend.app.services.repository.DB_PATH", db)
    init_db()
    first = create("01_CASES", {"Case_Name": "one"})
    delete("01_CASES", first["Case_ID"])
    second = create("01_CASES", {"Case_Name": "two"})
    assert first["Case_ID"] != second["Case_ID"]
