from backend.app.services.verification import run_verification


def test_structural_presence_is_not_a_proof(tmp_path):
    evidence = tmp_path / "evidence.txt"
    evidence.write_text("some evidence content", encoding="utf-8")
    for form in ("CX", "PD"):
        result = run_verification({"Claim_Form": form, "Claim_Statement": "A sufficiently long statement for this test."}, str(evidence))
        assert result["result"] == "INCONCLUSIVE"


def test_verification_result_has_stable_artifact_hash(tmp_path):
    evidence = tmp_path / "artifact.txt"
    evidence.write_text("ML-KEM-768 synthetic configuration", encoding="utf-8")
    result = run_verification({"Claim_Form": "ID", "Algorithm": "ML-KEM"}, str(evidence))
    assert len(result["verification_artifact_hash"]) == 64
