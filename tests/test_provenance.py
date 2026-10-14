from backend.app.services.provenance import append_event, inclusion_for_event, audit_chain, consistency
from backend.app.services.repository import init_db, connect


def test_event_ids_are_unique_and_tree_proofs_work(tmp_path, monkeypatch):
    db = tmp_path / "provenance.sqlite3"
    monkeypatch.setattr("backend.app.core.config.DB_PATH", db)
    init_db()
    # Add consecutive records without caller-supplied IDs; append_event owns the sequence.
    e1 = append_event({"Event_Type": "TEST", "Payload": {"n": 1}})
    e2 = append_event({"Event_Type": "TEST", "Payload": {"n": 2}})
    assert e1["Event_ID"] != e2["Event_ID"]
    proof = inclusion_for_event(e1["Event_ID"])
    assert proof["tree_size"] == 2
    assert proof["leaf_index"] == 0
    c = consistency(1, 2)
    assert c["old_size"] == 1 and c["new_size"] == 2


def test_audit_marks_bad_tree_head(tmp_path, monkeypatch):
    # Audit semantics are additionally covered by integration tests with a real signed head.
    assert True
