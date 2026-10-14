from backend.app.services.provenance import append_event, inclusion_for_event, consistency
from backend.app.services.repository import init_db
from backend.app.services.merkle import root_from_leaf_hashes, verify_inclusion, verify_consistency


def test_event_ids_are_unique_and_proofs_work(tmp_path, monkeypatch):
    db = tmp_path / "provenance.sqlite3"
    monkeypatch.setattr("backend.app.core.config.DB_PATH", db)
    init_db()
    first = append_event({"Event_Type": "TEST", "Payload": {"n": 1}})
    second = append_event({"Event_Type": "TEST", "Payload": {"n": 2}})
    assert first["Event_ID"] != second["Event_ID"]
    proof = inclusion_for_event(first["Event_ID"])
    hashes = [e["Event_Hash"] for e in [first, second]]
    root = root_from_leaf_hashes(hashes)
    assert verify_inclusion(bytes.fromhex(proof["leaf_hash"]), proof, root)
    cp = consistency(1, 2)
    assert verify_consistency(cp["old_size"], cp["new_size"], cp["old_root"], cp["new_root"], cp["proof"])
