from __future__ import annotations

from typing import Any, Dict, List

SCOPE_ORDER = {"D": 1, "C": 2, "B": 3, "A": 4}
CLAIM_FORMS = {"EX", "ST", "CX", "PD", "IM", "PR", "NG", "ID"}
ORIGINS = {"AI", "HUMAN", "HYBRID", "SYSTEM"}


def scope_status(claimed: str, verified: str) -> str:
    claimed = (claimed or "").strip().upper()
    verified = (verified or "").strip().upper()

    if not claimed:
        return "MISSING_CLAIMED_SCOPE"
    if not verified or verified == "NOT_VERIFIED":
        return "MISSING_VERIFIED_SCOPE"
    if claimed not in SCOPE_ORDER or verified not in SCOPE_ORDER:
        return "INVALID_SCOPE"
    if claimed == verified:
        return "SCOPE_MATCH"
    # A is the broadest scope; D is the narrowest. A claim is inflated when
    # it claims a broader scope than the evidence actually verifies.
    if SCOPE_ORDER[claimed] > SCOPE_ORDER[verified]:
        return "SCOPE_INFLATION"
    return "VERIFIED_SCOPE_BROADER_THAN_CLAIM"


def validate_claim(c: Dict[str, Any]) -> Dict[str, Any]:
    issues: List[str] = []
    required = {
        "case_id": "Case_ID",
        "claim_statement": "Claim_Statement",
        "claim_form": "Claim_Form",
        "claimed_scope": "Claimed_Scope",
    }
    for key, label in required.items():
        if not str(c.get(key, c.get(label, ""))).strip():
            issues.append(f"{label} is required.")

    form = str(c.get("claim_form", c.get("Claim_Form", ""))).upper().strip()
    claimed = str(c.get("claimed_scope", c.get("Claimed_Scope", ""))).upper().strip()
    verified = str(c.get("verified_scope", c.get("Verified_Scope", "NOT_VERIFIED"))).upper().strip()
    origin = str(c.get("origin", c.get("Origin", "HUMAN"))).upper().strip()

    if form and form not in CLAIM_FORMS:
        issues.append(f"Unsupported Claim_Form: {form}")
    if claimed and claimed not in SCOPE_ORDER:
        issues.append("Claimed_Scope must be A, B, C or D.")
    if verified not in set(SCOPE_ORDER) | {"NOT_VERIFIED"}:
        issues.append("Verified_Scope must be A, B, C, D or NOT_VERIFIED.")

    if origin not in ORIGINS:
        issues.append("Origin must be AI, HUMAN, HYBRID or SYSTEM.")

    ss = scope_status(claimed, verified)
    if ss == "SCOPE_INFLATION":
        issues.append("Scope inflation detected: the claim is broader than the verified evidence.")
    elif ss == "VERIFIED_SCOPE_BROADER_THAN_CLAIM":
        issues.append("Verified scope is broader than the claim; clarify the declared claim scope.")

    return {"valid": not issues, "issues": issues, "scope_status": ss}


def _truth(value: Any) -> bool:
    return str(value).strip().upper() in {"TRUE", "1", "YES"}


def derived_claim_fields(c: Dict[str, Any]) -> Dict[str, Any]:
    r = dict(c)
    claimed = str(r.get("Claimed_Scope", "")).upper()
    verified = str(r.get("Verified_Scope", "NOT_VERIFIED")).upper()
    r["Scope_Status"] = scope_status(claimed, verified)

    l3 = _truth(r.get("L3", "FALSE"))
    l2 = _truth(r.get("L2", "FALSE"))
    l1 = _truth(r.get("L1", "FALSE"))
    r["Assurance_State"] = "L3" if l3 else "L2" if l2 else "L1" if l1 else "L0"
    # Store one categorical assurance state, not overlapping cumulative counters.
    r["L0"] = "TRUE" if not (l1 or l2 or l3) else "FALSE"
    r["L1"] = "TRUE" if l1 and not (l2 or l3) else "FALSE"
    r["L2"] = "TRUE" if l2 and not l3 else "FALSE"
    r["L3"] = "TRUE" if l3 else "FALSE"
    if str(r.get("Origin", "")).upper() == "AI" and r["Assurance_State"] in {"L1", "L2", "L3"}:
        r["Notes"] = (str(r.get("Notes", "")) + " AI output alone does not establish assurance; backend evidence/verification required.").strip()
    return r
