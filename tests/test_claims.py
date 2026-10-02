from backend.app.services.claims import scope_status, validate_claim


def test_scope_match():
    assert scope_status("B", "B") == "SCOPE_MATCH"


def test_verified_scope_narrower():
    assert scope_status("A", "B") == "VERIFIED_SCOPE_NARROWER"


def test_scope_inflation():
    assert scope_status("B", "A") == "SCOPE_INFLATION"


def test_missing_verified_scope():
    assert scope_status("C", "NOT_VERIFIED") == "MISSING_VERIFIED_SCOPE"


def test_claim_validation_rejects_inflation():
    result = validate_claim({
        "case_id": "CASE-2026-0001",
        "claim_form": "ID",
        "claim_statement": "Synthetic identification claim.",
        "claimed_scope": "B",
        "verified_scope": "A",
        "origin": "HUMAN",
    })
    assert not result["valid"]
    assert result["scope_status"] == "SCOPE_INFLATION"
