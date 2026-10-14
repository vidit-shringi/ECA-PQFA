from __future__ import annotations

from math import isfinite, log2
from typing import Any, Dict, Iterable, List


def _rate(num: int, den: int):
    return None if den == 0 else num / den


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).strip().casefold() in {"true", "1", "yes", "y"}


def ndcg_at_k(predicted: List[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        return 0.0
    top = predicted[:k]
    dcg = sum((1 if x in relevant else 0) / log2(i + 2) for i, x in enumerate(top))
    ideal = sum(1 / log2(i + 2) for i in range(min(k, len(relevant))))
    return dcg / ideal if ideal else 0.0


def evaluate(records: Iterable[Dict[str, Any]], generated_count: int | None = None) -> Dict[str, Any]:
    rows = list(records)
    generated = len(rows) if generated_count is None else generated_count
    if not isinstance(generated, int) or generated < 0:
        raise ValueError("generated_count must be a non-negative integer")

    assessed = [r for r in rows if _as_bool(r.get("assessed", True))]
    l1 = [r for r in rows if str(r.get("assurance_state", r.get("Assurance_State", ""))).upper() in {"L1", "L2", "L3"}]
    l2 = [r for r in rows if str(r.get("assurance_state", r.get("Assurance_State", ""))).upper() in {"L2", "L3"}]
    refuted = sum(_as_bool(r.get("refuted", r.get("Refuted", False))) for r in assessed)
    scope_defined = [r for r in rows if r.get("verified_scope", r.get("Verified_Scope", "")) not in ("", None, "NOT_VERIFIED")]
    inflated = sum(str(r.get("scope_status", r.get("Scope_Status", ""))).upper() == "SCOPE_INFLATION" for r in scope_defined)
    complete = sum(_as_bool(r.get("provenance_complete", r.get("Provenance_Complete", False))) for r in rows)

    return {
        "VCR_1": _rate(len(l1), generated),
        "VCR_2": _rate(len(l2), generated),
        "VCR_3": _rate(sum(str(r.get("assurance_state", r.get("Assurance_State", ""))).upper() == "L3" for r in rows), generated),
        "FCCR": _rate(refuted, len(assessed)),
        "SIR": _rate(inflated, len(scope_defined)),
        "IRR": _rate(len(l2), len(l1)),
        "EPC": _rate(complete, len(rows)),
        "CTR": None, "AER": None, "CDG": None, "ATT": None, "VC": None, "HPP_at_k": None, "MVA": None,
        "notes": [
            "Null values mean required timing/device/effort/ground-truth fields were not supplied.",
            "Metrics are computed from supplied records; no experimental result is fabricated.",
            "Boolean-like string fields are parsed explicitly; non-empty strings such as 'FALSE' are false.",
        ],
    }
