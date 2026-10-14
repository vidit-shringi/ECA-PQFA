from __future__ import annotations

from typing import Any, Dict

from backend.app.core.schema import SHEETS
from backend.app.services.repository import (
    next_sequence, get_record, insert_record, list_records, update_record, delete_record,
)
from backend.app.services.utilities import ID_FIELDS, default_record, generate_id, now


def create(sheet: str, record: Dict[str, Any]) -> Dict[str, Any]:
    if sheet not in SHEETS:
        raise ValueError(f"Unsupported sheet: {sheet}")
    r = default_record(sheet, record)
    id_field = ID_FIELDS[sheet]
    if not r.get(id_field):
        r[id_field] = generate_id(sheet, next_sequence(sheet))
    r.setdefault("Created_At", now())
    r.setdefault("Last_Updated", now())
    return insert_record(sheet, str(r[id_field]), r, r.get("Case_ID", ""))


def update(sheet: str, record_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
    if sheet not in SHEETS:
        raise ValueError(f"Unsupported sheet: {sheet}")
    if not isinstance(patch, dict):
        raise ValueError("patch must be an object")
    if ID_FIELDS[sheet] in patch and str(patch[ID_FIELDS[sheet]]) != str(record_id):
        raise ValueError("record ID cannot be changed by patch")
    updated = update_record(sheet, record_id, patch)
    if updated is None:
        raise KeyError(record_id)
    return updated


def get(sheet: str, record_id: str) -> Dict[str, Any]:
    if sheet not in SHEETS:
        raise ValueError(f"Unsupported sheet: {sheet}")
    item = get_record(sheet, record_id)
    if item is None:
        raise KeyError(record_id)
    return item


def delete(sheet: str, record_id: str) -> None:
    if sheet not in SHEETS:
        raise ValueError(f"Unsupported sheet: {sheet}")
    if not delete_record(sheet, record_id):
        raise KeyError(record_id)


def list_(sheet: str, limit: int = 100, offset: int = 0):
    if sheet not in SHEETS:
        raise ValueError(f"Unsupported sheet: {sheet}")
    return list_records(sheet, limit, offset)
