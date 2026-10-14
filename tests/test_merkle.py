from backend.app.services.merkle import inclusion_proof, verify_inclusion, consistency_proof, verify_consistency


def test_inclusion():
    leaves = [f"event-{i}" for i in range(9)]
    for i, value in enumerate(leaves):
        proof = inclusion_proof(leaves, i)
        assert verify_inclusion(value, proof, proof["root"])


def test_inclusion_rejects_tampered_leaf_or_path():
    values = ["a", "b", "c", "d"]
    proof = inclusion_proof(values, 1)
    assert not verify_inclusion("tampered", proof, proof["root"])
    altered = {**proof, "audit_path": [{**proof["audit_path"][0], "hash": "00" * 32}] + proof["audit_path"][1:]}
    assert not verify_inclusion("b", altered, proof["root"])


def test_consistency():
    leaves = [f"event-{i}" for i in range(9)]
    for m in range(1, 9):
        proof = consistency_proof(leaves, m)
        assert verify_consistency(proof["old_size"], proof["new_size"], proof["old_root"], proof["new_root"], proof["proof"]), (m, proof)


def test_consistency_empty_prefix():
    proof = consistency_proof(["x"], 0)
    assert proof["old_size"] == 0
    assert proof["new_size"] == 1
    assert verify_consistency(0, 1, proof["old_root"], proof["new_root"], proof["proof"])


def test_consistency_equal_size_requires_equal_roots_and_no_proof():
    proof = consistency_proof(["same"], 1)
    assert verify_consistency(1, 1, proof["old_root"], proof["new_root"], [])
    assert not verify_consistency(1, 1, "0" * 64, "1" * 64, [])
