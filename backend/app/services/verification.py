from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict

from backend.app.services.inventory import detect_algorithms


def _read(path: str) -> bytes:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(str(p))
    return p.read_bytes()


def run_verification(
    claim: Dict[str, Any],
    evidence_path: str = "",
    verifier_id: str = "deterministic-v1",
) -> Dict[str, Any]:
    form = str(claim.get("Claim_Form", claim.get("claim_form", ""))).upper()
    algorithm = str(claim.get("Algorithm", claim.get("algorithm", ""))).strip()
    statement = str(claim.get("Claim_Statement", claim.get("claim_statement", "")))
    if form == "ID":
        data = _read(evidence_path)
        hits = detect_algorithms(data)
        normalized = {x.lower().replace("-", "") for x in hits}
        target = algorithm.lower().replace("-", "")
        ok = bool(target and target in normalized) or (not target and bool(hits))
        return _result(form, "PASS" if ok else "FAIL", verifier_id, {"detected_algorithms": hits, "requested_algorithm": algorithm, "evidence_sha256": hashlib.sha256(data).hexdigest()}, "Static/OID/string identification")
    if form == "EX":
        data = _read(evidence_path)
        digest = hashlib.sha256(data).hexdigest()
        expected = str(claim.get("Expected_SHA256", claim.get("expected_sha256", ""))).lower().strip()
        ok = bool(expected) and digest == expected
        return _result(form, "PASS" if ok else "FAIL", verifier_id, {"sha256": digest, "expected_sha256": expected}, "Evidence hash equality check; not an exploit/security proof")
    if form == "ST":
        return _verify_statistical(claim, evidence_path, verifier_id)
    if form == "NG":
        try:
            sample_size = int(claim.get("sample_size", 0))
            effect = float(claim.get("smallest_detectable_effect", -1))
            ok = sample_size > 0 and effect >= 0
        except (TypeError, ValueError):
            sample_size, effect, ok = 0, -1.0, False
        return _result(form, "PASS" if ok else "FAIL", verifier_id, {"sample_size": sample_size, "smallest_detectable_effect": effect}, "Negative-result reporting metadata check; not a security proof")
    if form == "IM":
        data = _read(evidence_path)
        hits = detect_algorithms(data)
        ok = bool(algorithm) and algorithm.lower().replace("-", "") in {x.lower().replace("-", "") for x in hits}
        return _result(form, "PASS" if ok else "FAIL", verifier_id, {"detected_algorithms": hits, "evidence_sha256": hashlib.sha256(data).hexdigest()}, "Implementation identity consistency check")
    if form == "PR":
        data = _read(evidence_path)
        text = data.decode("utf-8", "ignore")
        insecure_patterns = [
            r"\bSSL\s*v?3(?:\.0)?\b",
            r"\bTLS\s*v?1\.[01]\b",
            r"\binsecure_fallback\b",
            r"\bdowngrade\s*[:=]\s*(?:true|enabled|yes)\b",
        ]
        matches = [pattern for pattern in insecure_patterns if re.search(pattern, text, flags=re.IGNORECASE)]
        return _result(form, "FAIL" if matches else "PASS", verifier_id, {"insecure_configuration_patterns": matches, "evidence_sha256": hashlib.sha256(data).hexdigest(), "limitations": "Text-pattern scan only; not a protocol conformance or penetration test"}, "Protocol configuration pattern check")
    if form in {"CX", "PD"}:
        # File existence and statement length are not proof/cryptanalysis verification.
        return _result(form, "INCONCLUSIVE", verifier_id, {
            "note": "No claim-form-specific verifier is implemented. Evidence presence alone cannot establish this claim.",
            "evidence_path_supplied": bool(evidence_path),
            "statement_length": len(statement),
        }, "Unsupported claim form; manual/external verifier required")
    return _result(form, "INCONCLUSIVE", verifier_id, {"unsupported_claim_form": form}, "No verifier registered")


def _verify_statistical(claim: Dict[str, Any], path: str, verifier_id: str) -> Dict[str, Any]:
    if not path:
        return _result("ST", "INCONCLUSIVE", verifier_id, {"error": "CSV evidence path required"}, "CSV descriptive-statistics check")
    data = _read(path)
    rows = list(csv.DictReader(data.decode("utf-8", "ignore").splitlines()))
    metric = claim.get("metric", "")
    values = []
    if metric and rows and metric in rows[0]:
        for row in rows:
            try:
                value = float(row[metric])
                if value == value and abs(value) != float("inf"):
                    values.append(value)
            except (TypeError, ValueError):
                continue
    try:
        threshold = float(claim.get("minimum_mean", 0))
    except (TypeError, ValueError):
        threshold = float("inf")
    mean = sum(values) / len(values) if values else 0.0
    ok = bool(values) and mean >= threshold
    return _result("ST", "PASS" if ok else "FAIL", verifier_id, {"n": len(values), "metric": metric, "mean": mean, "minimum_mean": threshold, "evidence_sha256": hashlib.sha256(data).hexdigest()}, "Deterministic descriptive-statistics check; not statistical significance testing")


def _result(form: str, result: str, verifier_id: str, details: Dict[str, Any], method: str) -> Dict[str, Any]:
    artifact = hashlib.sha256(json.dumps(
        {"form": form, "result": result, "verifier_id": verifier_id, "details": details, "method": method},
        sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")).hexdigest()
    return {
        "claim_form": form,
        "result": result,
        "verifier_id": verifier_id,
        "verifier_type": "DETERMINISTIC",
        "method": method,
        "details": details,
        "verification_artifact_hash": artifact,
        "security_statement": "PASS establishes only the tested proposition within the declared scope; it is not a proof of scheme security.",
    }
