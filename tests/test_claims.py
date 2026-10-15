from backend.app.services.claims import scope_status, validate_claim


def test_scope_match():
    assert scope_status("B", "B") == "SCOPE_MATCH"


def test_claim_scope_broader_than_evidence_is_inflation():
    assert scope_status("A", "B") == "SCOPE_INFLATION"


def test_verified_scope_broader_than_claim_is_not_inflation():
    assert scope_status("B", "A") == "VERIFIED_SCOPE_BROADER"


def test_missing_verified_scope():
    assert scope_status("C", "NOT_VERIFIED") == "MISSING_VERIFIED_SCOPE"


def test_claim_validation_rejects_inflation():
    result = validate_claim({
        "case_id": "CASE-2026-0001",
        "claim_form": "ID",
        "claim_statement": "Synthetic identification claim.",
        "claimed_scope": "A",
        "verified_scope": "B",
        "origin": "HUMAN",
    })
    assert not result["valid"]
    assert result["scope_status"] == "SCOPE_INFLATION"


def test_claim_validation_does_not_call_narrow_claim_inflation():
    result = validate_claim({
        "case_id": "CASE-2026-0001",
        "claim_form": "ID",
        "claim_statement": "Synthetic identification claim.",
        "claimed_scope": "B",
        "verified_scope": "A",
        "origin": "HUMAN",
    })
    assert not result["valid"]
    assert result["scope_status"] == "VERIFIED_SCOPE_BROADER"


def test_caller_cannot_self_assign_assurance_or_refutation():
    from backend.app.services.claims import derived_claim_fields

    record = derived_claim_fields({
        "Case_ID": "CASE-2026-0001",
        "Claim_Form": "ID",
        "Claim_Statement": "A synthetic identification claim.",
        "Claimed_Scope": "C",
        "Verified_Scope": "NOT_VERIFIED",
        "L0": "FALSE",
        "L1": "TRUE",
        "L2": "TRUE",
        "L3": "TRUE",
        "Refuted": "TRUE",
        "Assurance_State": "L3",
    })
    assert record["Assurance_State"] == "L0"
    assert record["L0"] == "TRUE"
    assert record["L1"] == record["L2"] == record["L3"] == "FALSE"
    assert record["Refuted"] == "FALSE"
