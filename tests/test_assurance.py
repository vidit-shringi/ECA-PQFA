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


def test_l3_requires_structured_artifact_and_review():
    claim = {"Claim_Form": "ID"}
    assert not promotion_check(claim, [], {"verified": True, "artifact_id": "proof-1"}, True)["L3"]
    result = promotion_check(
        claim, [],
        {"verified": True, "artifact_id": "proof-1"},
        {"approved": True, "reviewer_id": "reviewer-1"},
    )
    assert result["L3"] is True
