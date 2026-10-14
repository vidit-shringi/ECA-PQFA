from backend.app.services.claims import scope_status, validate_claim, derived_claim_fields


def test_scope_match():
    assert scope_status("B", "B") == "SCOPE_MATCH"


def test_claim_broader_than_verified_scope_is_inflation():
    assert scope_status("A", "C") == "SCOPE_INFLATION"


def test_verified_scope_broader_than_claim_is_not_inflation():
    assert scope_status("C", "A") == "VERIFIED_SCOPE_BROADER_THAN_CLAIM"


def test_missing_verified_scope():
    assert scope_status("C", "NOT_VERIFIED") == "MISSING_VERIFIED_SCOPE"


def test_claim_validation_rejects_inflation():
    result = validate_claim({
        "case_id": "CASE-2026-0001",
        "claim_form": "ID",
        "claim_statement": "Synthetic identification claim.",
        "claimed_scope": "A",
        "verified_scope": "C",
        "origin": "HUMAN",
    })
    assert not result["valid"]
    assert result["scope_status"] == "SCOPE_INFLATION"


def test_false_string_does_not_set_assurance_flags():
    result = derived_claim_fields({"Origin": "HUMAN", "Claimed_Scope": "C", "Verified_Scope": "C",
                                   "L0": "FALSE", "L1": "FALSE", "L2": "FALSE", "L3": "FALSE"})
    assert result["Assurance_State"] == "L0"
    assert result["L0"] == "TRUE"
    assert result["L1"] == result["L2"] == result["L3"] == "FALSE"
