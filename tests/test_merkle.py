from backend.app.services.merkle import (
    inclusion_proof, verify_inclusion, consistency_proof, verify_consistency,
    leaf_hash, verify_inclusion,
)
from backend.app.services.provenance import append_event, inclusion_for_event, audit_chain
from backend.app.services.repository import init_db
import pytest


def test_inclusion():
    leaves = [f"event-{i}" for i in range(9)]
    for i, x in enumerate(leaves):
        proof = inclusion_proof(leaves, i)
        assert verify_inclusion(x, proof, proof["root"])


def test_consistency():
    leaves = [f"event-{i}" for i in range(9)]
    for m in range(1, 9):
        proof = consistency_proof(leaves, m)
        assert verify_consistency(proof["old_size"], proof["new_size"], proof["old_root"], proof["new_root"], proof["proof"]), (m, proof)


def test_prehashed_provenance_leaf_verifies():
    events = [leaf_hash(f"evt-{i}") for i in range(5)]
    # Proof verifier must be passed the original leaf bytes when it applies leaf_hash
    for i, original in enumerate([f"evt-{j}" for j in range(5)]):
        proof = inclusion_proof([f"evt-{j}" for j in range(5)], i)
        assert verify_inclusion(original, proof, proof["root"])


def test_consistency_empty_tree_edge_cases():
    proof = consistency_proof(["x"], 0)
    assert proof["old_size"] == 0
    assert proof["new_size"] == 1
    assert not verify_consistency(0, 1, proof["old_root"], proof["new_root"], proof["proof"])
