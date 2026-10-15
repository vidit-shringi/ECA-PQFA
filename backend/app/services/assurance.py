from __future__ import annotations

from typing import Any, Dict

ERROR_PROPAGATION = {
    "EX": {"verifier_implementation", "hardware"},
    "ST": {"code_base", "data_source", "model_family", "hardware"},
    "CX": {"verifier_implementation", "analyst_organization"},
    "PD": {"verifier_implementation", "analyst_organization"},
    "IM": {"hardware_device", "code_base"},
    "PR": {"verifier_implementation", "analyst_organization"},
    "NG": {"model_family", "data_source"},
    "ID": {"verifier_implementation"},
}


def _passed(value: Any) -> bool:
    return value is True or (isinstance(value, str) and value.strip().upper() in {"PASS", "TRUE"})


def independence_check(claim_form: str, first: Dict[str, Any], second: Dict[str, Any]) -> Dict[str, Any]:
    dims = ERROR_PROPAGATION.get(claim_form.upper(), set())
    differences = {d: bool(first.get(d)) and bool(second.get(d)) and first.get(d) != second.get(d) for d in dims}
    ok = bool(dims) and all(differences.values())
    return {
        "claim_form": claim_form,
        "required_dimensions": sorted(dims),
        "differences": differences,
        "independent": ok,
        "warning": "Different metadata values are only a heuristic; independence requires evidence of distinct failure modes.",
    }


def promotion_check(
    claim: Dict[str, Any],
    verifications: list[Dict[str, Any]],
    formal: Any = None,
    human_review: Any = None,
) -> Dict[str, Any]:
    form = str(claim.get("Claim_Form", claim.get("claim_form", ""))).upper()
    passed = [
        v for v in verifications
        if str(v.get("Result", v.get("result", ""))).upper() == "PASS"
        and v.get("verification_artifact_hash", v.get("output_hash"))
    ]
    l1 = len(passed) >= 1
    l2 = False
    independence = None
    if len(passed) >= 2:
        independence = independence_check(form, passed[0], passed[1])
        l2 = independence["independent"]

    # Deliberately fail closed: this API has no trusted, server-side formal-proof
    # checker yet. User-supplied booleans or filenames cannot establish L3.
    l3 = False
    return {
        "L0": True,
        "L1": l1,
        "L2": l2,
        "L3": l3,
        "assurance_state": "L2" if l2 else "L1" if l1 else "L0",
        "promotion_reasons": {
            "L1": "evidence-backed PASS verification" if l1 else "requires PASS verification with an evidence/output hash",
            "L2": "heuristic independence conditions met; independent reproduction still needs review" if l2 else "requires two evidence-backed PASS verifications meeting configured independence dimensions",
            "L3": "disabled until a trusted server-side formal-proof checker and auditable human-review workflow are integrated",
        },
        "independence": independence,
    }
