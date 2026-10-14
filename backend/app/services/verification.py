from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path
from typing import Any, Dict

from backend.app.services.inventory import detect_algorithms


def _read(path: str) -> bytes:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(str(p))
    return p.read_bytes()


def _as_number(claim: Dict[str, Any], key: str, *, minimum: float | None = None) -> float:
    try:
        value = float(claim[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"'{key}' must be a numeric field") from exc
    if not math.isfinite(value):
        raise ValueError(f"'{key}' must be finite")
    if minimum is not None and value < minimum:
        raise ValueError(f"'{key}' must be >= {minimum}")
    return value


def run_verification(claim: Dict[str, Any], evidence_path: str = "",
                     verifier_id: str = "deterministic-v1") -> Dict[str, Any]:
    form = str(claim.get("Claim_Form", claim.get("claim_form", ""))).upper()
    algorithm = str(claim.get("Algorithm", claim.get("algorithm", ""))).strip()
    if form == "ID":
        data = _read(evidence_path)
        hits = detect_algorithms(data)
        normalized = {x.lower().replace("-", "").replace("_", "") for x in hits}
        target = algorithm.lower().replace("-", "").replace("_", "")
        ok = bool(target and target in normalized) or (not target and bool(hits))
        return _result(form, ok, verifier_id,
                       {"detected_algorithms": hits, "requested_algorithm": algorithm},
                       "Static/OID/string identification indication only")

    if form == "EX":
        data = _read(evidence_path)
        digest = hashlib.sha256(data).hexdigest()
        expected = str(claim.get("Expected_SHA256", "")).lower().strip()
        ok = len(expected) == 64 and digest == expected and all(c in "0123456789abcdef" for c in expected)
        return _result(form, ok, verifier_id, {"sha256": digest, "expected_sha256": expected},
                       "SHA-256 evidence-integrity check only")

    if form == "ST":
        return _verify_statistical(claim, evidence_path, verifier_id)

    if form == "NG":
        required = ["sample_size", "smallest_detectable_effect"]
        missing = [key for key in required if key not in claim]
        try:
            n = _as_number(claim, "sample_size", minimum=1)
            effect = _as_number(claim, "smallest_detectable_effect", minimum=0)
            valid = not missing and n.is_integer() and effect > 0
        except ValueError:
            n, effect, valid = 0.0, 0.0, False
        return _result(form, valid, verifier_id,
                       {"missing": missing, "sample_size": n, "smallest_detectable_effect": effect},
                       "Negative-result metadata completeness check; not a security proof")

    if form == "IM":
        hits = detect_algorithms(_read(evidence_path))
        normalized = {x.lower().replace("-", "").replace("_", "") for x in hits}
        target = algorithm.lower().replace("-", "").replace("_", "")
        ok = bool(target) and target in normalized
        return _result(form, ok, verifier_id, {"detected_algorithms": hits},
                       "Static string/OID identity indication only")

    if form == "PR":
        text = _read(evidence_path).decode("utf-8", "ignore").lower()
        bad = [marker for marker in
               ("sslv2", "sslv3", "tlsv1", "tls 1.0", "tls 1.1", "insecure_fallback", "downgrade")
               if marker in text]
        fallback = "fallback" in text
        ok = bool(text.strip()) and not bad and not fallback
        return _result(form, ok, verifier_id,
                       {"warning_tokens": bad, "generic_fallback_token": fallback},
                       "Heuristic protocol-configuration screening; absence of markers is not a security proof")

    if form in {"CX", "PD"}:
        exists = bool(evidence_path) and Path(evidence_path).expanduser().resolve().is_file()
        return _result(form, False, verifier_id, {
            "evidence_file_present": exists,
            "note": "No built-in verifier is implemented for this form; external checker and review required.",
        }, "Unsupported without external verifier")

    return _result(form, False, verifier_id, {}, "Unsupported claim form")


def _verify_statistical(claim: Dict[str, Any], path: str, verifier_id: str) -> Dict[str, Any]:
    if not path:
        return _result("ST", False, verifier_id, {"error": "CSV evidence path required"},
                       "Descriptive-statistics threshold check")
    rows = list(csv.DictReader(_read(path).decode("utf-8", "strict").splitlines()))
    metric = str(claim.get("metric", "")).strip()
    values = []
    if metric and rows and metric in rows[0]:
        for row in rows:
            try:
                value = float(row[metric])
            except (TypeError, ValueError):
                continue
            if math.isfinite(value):
                values.append(value)
    try:
        threshold = _as_number(claim, "minimum_mean")
        min_n_value = _as_number(claim, "minimum_n", minimum=1) if "minimum_n" in claim else 1.0
        if not min_n_value.is_integer():
            raise ValueError("'minimum_n' must be an integer")
        minimum_n = int(min_n_value)
    except ValueError as exc:
        return _result("ST", False, verifier_id,
                       {"error": str(exc), "n": len(values), "metric": metric},
                       "Descriptive-statistics threshold check")
    mean = sum(values) / len(values) if values else 0.0
    ok = bool(values) and len(values) >= minimum_n and mean >= threshold
    return _result("ST", ok, verifier_id,
                   {"n": len(values), "minimum_n": minimum_n, "metric": metric,
                    "mean": mean, "minimum_mean": threshold},
                   "Descriptive-statistics threshold check; not a statistical significance test")


def _result(form: str, ok: bool, verifier_id: str, details: Dict[str, Any], method: str) -> Dict[str, Any]:
    return {
        "claim_form": form,
        "result": "PASS" if ok else "FAIL",
        "verifier_id": verifier_id,
        "verifier_type": "DETERMINISTIC",
        "method": method,
        "details": details,
        "security_statement": "A PASS establishes only the tested proposition within the declared scope; it is not a proof of scheme security.",
    }
