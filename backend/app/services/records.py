from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from backend.app.core.schema import SHEETS
from backend.app.services.repository import (
    count_records, get_record, insert_record, list_records, update_record,
    delete_record,
)
from backend.app.services.utilities import ID_FIELDS, default_record, generate_id, now


def next_number(sheet: str) -> int:
    # Count-based identifiers are not safe after deletes or concurrent creates.
    # Generate a candidate, then let the DB primary key detect a collision.
    return count_records(sheet) + 1


def _next_available_id(sheet: str) -> str:
    number = max(1, next_number(sheet))
    while True:
        candidate = generate_id(sheet, number)
        if get_record(sheet, candidate) is None:
            return candidate
        number += 1


def create(sheet: str, record: Dict[str, Any]) -> Dict[str, Any]:
    if sheet not in SHEETS:
        raise ValueError(f"Unsupported sheet: {sheet}")
    r = default_record(sheet, record)
    idf = ID_FIELDS[sheet]
    if not r.get(idf):
        r[idf] = _next_available_id(sheet)
    r.setdefault("Created_At", now())
    r.setdefault("Last_Updated", now())
    case_id = r.get("Case_ID", "")
    return insert_record(sheet, str(r[idf]), r, case_id)


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
