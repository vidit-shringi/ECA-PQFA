from backend.app.services.assurance import independence_check, promotion_check


def test_independence():
    a = {"verifier_implementation": "a", "hardware": "x"}
    b = {"verifier_implementation": "b", "hardware": "y"}
    assert independence_check("EX", a, b)["independent"]


def test_promotion_requires_evidence_backed_verifications():
    claim = {"Claim_Form": "EX"}
    vs = [
        {"Result": "PASS", "verification_artifact_hash": "a" * 64, "verifier_implementation": "a", "hardware": "x"},
        {"Result": "PASS", "verification_artifact_hash": "b" * 64, "verifier_implementation": "b", "hardware": "y"},
    ]
    result = promotion_check(claim, vs)
    assert result["L1"]
    assert result["L2"]


def test_promotion_does_not_accept_string_false_or_client_asserted_l3():
    result = promotion_check(
        {"Claim_Form": "ID"},
        [{"Result": "PASS", "verification_artifact_hash": "a" * 64}],
        formal="false",
        human_review="false",
    )
    assert result["L1"]
    assert result["L3"] is False
    assert result["assurance_state"] == "L1"


def test_l2_requires_required_dimensions_to_be_present():
    result = promotion_check(
        {"Claim_Form": "EX"},
        [
            {"Result": "PASS", "verification_artifact_hash": "a" * 64, "verifier_implementation": "a", "hardware": "x"},
            {"Result": "PASS", "verification_artifact_hash": "b" * 64, "verifier_implementation": "b"},
        ],
    )
    assert result["L2"] is False
