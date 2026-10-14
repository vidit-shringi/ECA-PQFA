from backend.app.services.assurance import independence_check, promotion_check


def test_independence():
    a = {"verifier_implementation": "a", "hardware": "x"}
    b = {"verifier_implementation": "b", "hardware": "y"}
    assert independence_check("EX", a, b)["independent"]


def test_promotion_l2():
    claim = {"Claim_Form": "ID"}
    verifications = [
        {"Result": "PASS", "verifier_implementation": "a"},
        {"Result": "PASS", "verifier_implementation": "b"},
    ]
    assert promotion_check(claim, verifications)["L2"]


def test_string_false_cannot_promote_l3():
    result = promotion_check({"Claim_Form": "ID"}, [], "false", "false")
    assert result["L3"] is False


def test_l3_fails_closed_until_trusted_checker_exists():
    claim = {"Claim_Form": "ID"}
    result = promotion_check(
        claim, [],
        {"verified": True, "artifact_id": "proof-1"},
        {"approved": True, "reviewer_id": "reviewer-1"},
    )
    assert result["L3"] is False
    assert "no trusted formal-proof checker" in result["promotion_reasons"]["L3"]


def test_independence_checks_later_pairs_and_requires_complete_dimensions():
    claim = {"Claim_Form": "EX"}
    first = {"Result": "PASS", "verifier_implementation": "a", "hardware": "same"}
    second = {"Result": "PASS", "verifier_implementation": "a", "hardware": "same"}
    third = {"Result": "PASS", "verifier_implementation": "b", "hardware": "different"}
    assert promotion_check(claim, [first, second, third])["L2"] is True
    assert promotion_check(claim, [first, {"Result": "PASS"}])["L2"] is False
