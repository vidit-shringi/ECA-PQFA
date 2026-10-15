from __future__ import annotations

import hashlib

import pytest

from backend.app.services import repository
from backend.app.services.merkle import inclusion_proof_from_hashes, root_from_leaf_hashes, verify_inclusion
from backend.app.services.provenance import all_events, append_event, audit_chain
from backend.app.services.hndl import hndl_assessment


def test_prehashed_provenance_inclusion_verifies():
    event_hashes = [hashlib.sha256(f"event-{i}".encode()).digest() for i in range(5)]
    proof = inclusion_proof_from_hashes(event_hashes, 3)
    root = root_from_leaf_hashes([item.hex() for item in event_hashes])
    assert verify_inclusion(event_hashes[3], proof, root)


def test_duplicate_event_ids_are_made_unique_and_chain_is_valid(tmp_path, monkeypatch):
    monkeypatch.setattr(repository, "DB_PATH", tmp_path / "test.sqlite3")
    repository.init_db()
    first = append_event({"Event_ID": "EVT-2026-0001", "Event_Type": "FIRST", "Timestamp": "2026-10-15T00:00:00Z"})
    second = append_event({"Event_ID": "EVT-2026-0001", "Event_Type": "SECOND", "Timestamp": "2026-10-15T00:00:01Z"})
    assert first["Event_ID"] != second["Event_ID"]
    assert len(all_events()) == 2
    assert audit_chain()["chain_valid"]


def test_hndl_rejects_invalid_quantile_order():
    with pytest.raises(ValueError):
        hndl_assessment("HIGH", "BOTH", "2026-01-01", "2026-10-01", 10, "2028-01-01", 20, 15, 10)


def test_hndl_rejects_migration_before_current_date():
    with pytest.raises(ValueError):
        hndl_assessment("HIGH", "BOTH", "2026-01-01", "2026-10-01", 10, "2026-09-01", 10, 15, 20)
