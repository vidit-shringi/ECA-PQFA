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
    if not p.is_file(): raise FileNotFoundError(str(p))
    return p.read_bytes()


def run_verification(claim: Dict[str, Any], evidence_path: str = "", verifier_id: str = "deterministic-v1") -> Dict[str, Any]:
    form = str(claim.get("Claim_Form", claim.get("claim_form", ""))).upper()
    algorithm = str(claim.get("Algorithm", claim.get("algorithm", ""))).strip()
    statement = str(claim.get("Claim_Statement", claim.get("claim_statement", "")))
    if form == "ID":
        data = _read(evidence_path)
        hits = detect_algorithms(data)
        normalized = {x.lower().replace("-", "") for x in hits}
        target = algorithm.lower().replace("-", "")
        ok = bool(target and target in normalized) or (not target and bool(hits))
        return _result(form, ok, verifier_id, {"detected_algorithms": hits, "requested_algorithm": algorithm}, "Static/OID/string identification")
    if form == "EX":
        data = _read(evidence_path)
        digest = hashlib.sha256(data).hexdigest()
        expected = str(claim.get("Expected_SHA256", "")).lower().strip()
        ok = bool(expected) and digest == expected
        return _result(form, ok, verifier_id, {"sha256": digest, "expected_sha256": expected}, "Executable evidence integrity / deterministic vector")
    if form == "ST":
        return _verify_statistical(claim, evidence_path, verifier_id)
    if form == "NG":
        required = ["sample_size", "smallest_detectable_effect"]
        missing = [k for k in required if k not in claim]
        ok = not missing and float(claim.get("sample_size", 0)) > 0 and float(claim.get("smallest_detectable_effect", 0)) >= 0
        return _result(form, ok, verifier_id, {"missing": missing, "sample_size": claim.get("sample_size"), "smallest_detectable_effect": claim.get("smallest_detectable_effect")}, "Negative-result reporting check; not a security proof")
    if form == "IM":
        data = _read(evidence_path)
        hits = detect_algorithms(data)
        ok = bool(algorithm) and algorithm.lower().replace("-", "") in {x.lower().replace("-", "") for x in hits}
        return _result(form, ok, verifier_id, {"detected_algorithms": hits}, "Implementation identity consistency check")
    if form == "PR":
        text = _read(evidence_path).decode("utf-8", "ignore")
        bad = [x for x in ("TLSv1", "SSLv3", "fallback", "downgrade") if x.lower() in text.lower()]
        return _result(form, not any(x in text.lower() for x in ("downgrade", "insecure_fallback")), verifier_id, {"warning_tokens": bad}, "Protocol configuration review")
    if form in {"CX", "PD"}:
        ok = bool(evidence_path and Path(evidence_path).is_file()) and len(statement) > 20
        return _result(form, ok, verifier_id, {"note": "Structural evidence presence check only; formal/proof claims require an external proof checker."}, "Evidence-presence gate")
    return _result(form, False, verifier_id, {}, "Unsupported claim form")


def _verify_statistical(claim: Dict[str, Any], path: str, verifier_id: str) -> Dict[str, Any]:
    if not path: return _result("ST", False, verifier_id, {"error":"CSV evidence path required"}, "CSV statistical check")
    rows = list(csv.DictReader(_read(path).decode("utf-8", "ignore").splitlines()))
    metric = claim.get("metric", "")
    values = []
    if metric and rows and metric in rows[0]:
        for r in rows:
            try: values.append(float(r[metric]))
            except (TypeError, ValueError): pass
    threshold = float(claim.get("minimum_mean", 0))
    mean = sum(values)/len(values) if values else 0.0
    ok = bool(values) and mean >= threshold
    return _result("ST", ok, verifier_id, {"n":len(values),"metric":metric,"mean":mean,"minimum_mean":threshold}, "Deterministic descriptive-statistics check")


def _result(form: str, ok: bool, verifier_id: str, details: Dict[str, Any], method: str) -> Dict[str, Any]:
    return {"claim_form":form,"result":"PASS" if ok else "FAIL","verifier_id":verifier_id,"verifier_type":"DETERMINISTIC","method":method,"details":details,"security_statement":"A PASS establishes only the tested proposition within the declared scope; it is not a proof of scheme security."}
