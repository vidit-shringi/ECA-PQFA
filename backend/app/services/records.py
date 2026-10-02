from __future__ import annotations

from typing import Any, Dict

from backend.app.core.schema import SHEETS
from backend.app.services.repository import (
    count_records, get_record, insert_record, list_records, update_record,
    delete_record
)
from backend.app.services.utilities import (
    ID_FIELDS, default_record, generate_id, now
)


def next_number(sheet: str) -> int:
    # Local sequence counter; SQLite is the authoritative local source.
    return count_records(sheet) + 1


def create(sheet: str, record: Dict[str, Any]) -> Dict[str, Any]:
    if sheet not in SHEETS:
        raise ValueError(f"Unsupported sheet: {sheet}")
    r = default_record(sheet, record)
    idf = ID_FIELDS[sheet]
    if not r.get(idf):
        r[idf] = generate_id(sheet, next_number(sheet))
    r.setdefault("Created_At", now())
    r.setdefault("Last_Updated", now())
    case_id = r.get("Case_ID", "")
    return insert_record(sheet, r[idf], r, case_id)


def update(sheet: str, record_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    if sheet not in SHEETS:
        raise ValueError(f"Unsupported sheet: {sheet}")
    updated = update_record(sheet, record_id, patch)
    if updated is None:
        raise KeyError(record_id)
    return updated


def get(sheet: str, record_id: str) -> Dict[str, Any]:
    item = get_record(sheet, record_id)
    if item is None:
        raise KeyError(record_id)
    return item


def delete(sheet: str, record_id: str) -> None:
    if not delete_record(sheet, record_id):
        raise KeyError(record_id)


def list_(sheet: str, limit: int = 100, offset: int = 0):
    if sheet not in SHEETS:
        raise ValueError(f"Unsupported sheet: {sheet}")
    return list_records(sheet, limit, offset)
