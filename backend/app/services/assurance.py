from __future__ import annotations

from itertools import combinations
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


def independence_check(claim_form: str, first: Dict[str, Any], second: Dict[str, Any]) -> Dict[str, Any]:
    dims = ERROR_PROPAGATION.get(claim_form.upper(), set())
    # Missing dimension values are not evidence of independence, even if both records
    # omit the same field; every declared dimension must be present and differ.
    differences = {
        d: d in first and d in second and first[d] is not None and second[d] is not None and first[d] != second[d]
        for d in dims
    }
    ok = bool(dims) and all(differences.values())
    return {"claim_form": claim_form, "required_dimensions": sorted(dims),
            "differences": differences, "independent": ok}


def promotion_check(claim: Dict[str, Any], verifications: list[Dict[str, Any]],
                    formal: Any = False, human_review: Any = False) -> Dict[str, Any]:
    passed = [v for v in verifications
              if str(v.get("Result", v.get("result", ""))).strip().upper() == "PASS"]
    l1 = len(passed) >= 1
    l2 = False
    independence = None
    # A failed pair must not hide a later independent reproduction pair.
    for first, second in combinations(passed, 2):
        candidate = independence_check(str(claim.get("Claim_Form", "")).upper(), first, second)
        if candidate["independent"]:
            l2, independence = True, candidate
            break
        if independence is None:
            independence = candidate

    # No registered proof-checker exists in this prototype. Caller-controlled booleans
    # or metadata cannot establish L3; fail closed until a trusted checker is integrated.
    l3 = False
    return {
        "L0": True,
        "L1": l1,
        "L2": l2,
        "L3": l3,
        "assurance_state": "L2" if l2 else "L1" if l1 else "L0",
        "promotion_reasons": {
            "L1": "accepted verifier" if l1 else "requires PASS verification",
            "L2": "phi-independent second acceptance" if l2 else "requires phi-independent second acceptance",
            "L3": "not available: no trusted formal-proof checker is configured",
        },
        "independence": independence,
    }
