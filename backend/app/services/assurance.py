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


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).strip().casefold() in {"true", "1", "yes", "y"}


def independence_check(claim_form: str, first: Dict[str, Any], second: Dict[str, Any]) -> Dict[str, Any]:
    dims = ERROR_PROPAGATION.get(claim_form.upper(), set())
    differences = {d: first.get(d) != second.get(d) for d in dims}
    ok = bool(dims) and all(differences.values())
    return {
        "claim_form": claim_form,
        "required_dimensions": sorted(dims),
        "differences": differences,
        "independent": ok,
    }


def promotion_check(
    claim: Dict[str, Any],
    verifications: list[Dict[str, Any]],
    formal: Any = False,
    human_review: Any = False,
) -> Dict[str, Any]:
    # Only explicit PASS results with distinct verifier identities are eligible.
    passed = [
        v for v in verifications
        if str(v.get("Result", v.get("result", ""))).strip().upper() == "PASS"
    ]
    l1 = len(passed) >= 1
    l2 = False
    independence = None
    if len(passed) >= 2:
        independence = independence_check(str(claim.get("Claim_Form", "")).upper(), passed[0], passed[1])
        l2 = independence["independent"]

    # A boolean flag alone cannot establish that a proof is valid. This function is
    # a gate only: caller must provide a verified artifact reference/result and review record.
    formal_valid = isinstance(formal, dict) and _as_bool(formal.get("verified")) and bool(formal.get("artifact_id"))
    review_valid = isinstance(human_review, dict) and _as_bool(human_review.get("approved")) and bool(human_review.get("reviewer_id"))
    l3 = formal_valid and review_valid

    return {
        "L0": True,
        "L1": l1,
        "L2": l2,
        "L3": l3,
        "assurance_state": "L3" if l3 else "L2" if l2 else "L1" if l1 else "L0",
        "promotion_reasons": {
            "L1": "accepted verifier" if l1 else "requires PASS verification",
            "L2": "phi-independent second acceptance" if l2 else "requires phi-independent second acceptance",
            "L3": "verified proof artifact + attributable human adequacy review" if l3 else "requires verified proof artifact and review record",
        },
        "independence": independence,
    }
