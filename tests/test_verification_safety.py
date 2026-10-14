from backend.app.services.verification import run_verification
from pathlib import Path


def test_cx_and_pd_fail_closed_without_external_verifier(tmp_path: Path):
    evidence = tmp_path / "proof.txt"
    evidence.write_text("a sufficiently long statement-looking piece of evidence", encoding="utf-8")
    for form in ("CX", "PD"):
        result = run_verification({"Claim_Form": form, "Claim_Statement": "x" * 40}, str(evidence))
        assert result["result"] == "FAIL"


def test_protocol_screening_fails_on_legacy_tls_marker(tmp_path: Path):
    evidence = tmp_path / "tls.conf"
    evidence.write_text("protocol=TLSv1", encoding="utf-8")
    result = run_verification({"Claim_Form": "PR"}, str(evidence))
    assert result["result"] == "FAIL"


def test_protocol_screening_never_passes_by_absence_of_known_strings(tmp_path: Path):
    evidence = tmp_path / "tls.conf"
    evidence.write_text("protocol=TLSv1.3; cipher=secure-looking-name", encoding="utf-8")
    result = run_verification({"Claim_Form": "PR"}, str(evidence))
    assert result["result"] == "INCONCLUSIVE"


def test_ng_rejects_zero_effect(tmp_path: Path):
    result = run_verification({"Claim_Form": "NG", "sample_size": 25, "smallest_detectable_effect": 0})
    assert result["result"] == "FAIL"
