from __future__ import annotations

from datetime import date
import math
from typing import Any, Dict

SENSITIVITY = {"LOW": 0.25, "MEDIUM": 0.5, "HIGH": 0.75, "CRITICAL": 1.0}


def years_between(a: date, b: date) -> float:
    return max(0.0, (b - a).days / 365.25)


def break_cdf(t_years: float, optimistic: float, median: float, pessimistic: float) -> float:
    """Illustrative piecewise CDF from three stated quantiles (0.1, 0.5, 0.9).

    This interpolation is a transparent scenario approximation, not a calibrated
    distribution. Inputs are sorted by time only to keep the curve monotone.
    """
    qs = sorted([(max(0.0, optimistic), 0.1), (max(0.0, median), 0.5), (max(0.0, pessimistic), 0.9)])
    if t_years < qs[0][0]:
        return 0.0
    for (x1, p1), (x2, p2) in zip(qs, qs[1:]):
        if t_years < x2:
            return p2 if x2 == x1 else p1 + (p2 - p1) * (t_years - x1) / (x2 - x1)
    return 1.0 if t_years >= qs[-1][0] else 0.0


def _finite_nonnegative(name: str, value: Any) -> float:
    try:
        result = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be finite and non-negative")
    return result


def hndl_assessment(
    sensitivity: str,
    exposure_type: str,
    capture_date: str,
    current_date: str,
    confidentiality_lifetime_years: float,
    migration_date: str,
    optimistic_crqc_years: float,
    median_crqc_years: float,
    pessimistic_crqc_years: float,
    data_generation_rate: float = 1.0,
    exposure_probability: float = 1.0,
) -> Dict[str, object]:
    """Illustrative HNDL scenario model, not calibrated risk prediction.

    Retrospective risk: sensitivity * exposure probability * P[break by capture age + L].
    Prospective risk integrates future exposure only from now to the migration date.
    The default quantile curve is explicitly a scenario approximation.
    """
    sensitivity_key = str(sensitivity).strip().upper()
    exposure_key = str(exposure_type).strip().upper()
    if sensitivity_key not in SENSITIVITY:
        raise ValueError(f"Unknown sensitivity: {sensitivity}")
    if exposure_key not in {"RETROSPECTIVE", "PROSPECTIVE", "BOTH"}:
        raise ValueError(f"Unknown exposure_type: {exposure_type}")

    cap = date.fromisoformat(capture_date)
    cur = date.fromisoformat(current_date)
    mig = date.fromisoformat(migration_date)
    if cap > cur:
        raise ValueError("capture_date cannot be after current_date")
    if mig < cur:
        raise ValueError("migration_date cannot be before current_date")

    lifetime = _finite_nonnegative("confidentiality_lifetime_years", confidentiality_lifetime_years)
    optimistic = _finite_nonnegative("optimistic_crqc_years", optimistic_crqc_years)
    median = _finite_nonnegative("median_crqc_years", median_crqc_years)
    pessimistic = _finite_nonnegative("pessimistic_crqc_years", pessimistic_crqc_years)
    rate = _finite_nonnegative("data_generation_rate", data_generation_rate)
    probability = _finite_nonnegative("exposure_probability", exposure_probability)
    if probability > 1:
        raise ValueError("exposure_probability must be between 0 and 1")
    if not optimistic <= median <= pessimistic:
        raise ValueError("CRQC scenario years must satisfy optimistic <= median <= pessimistic")

    s = SENSITIVITY[sensitivity_key]
    age = years_between(cap, cur)
    horizon = age + lifetime
    scenarios = {"optimistic": optimistic, "median": median, "pessimistic": pessimistic}
    # Keep the three named scenarios deterministic; the separate interpolated CDF
    # is exposed for sensitivity analysis and is explicitly uncalibrated.
    retrospective = {
        name: round(s * probability * (1.0 if horizon >= break_year else 0.0), 6)
        for name, break_year in scenarios.items()
    }
    distributional_retrospective = round(
        s * probability * break_cdf(horizon, optimistic, median, pessimistic), 6
    )
    migration_years = years_between(cur, mig)
    steps = 120
    prospective = {name: 0.0 for name in scenarios}
    if exposure_key in {"PROSPECTIVE", "BOTH"} and migration_years > 0:
        dt = migration_years / steps
        for name, break_year in scenarios.items():
            total = 0.0
            for j in range(steps):
                t_from_now = (j + 0.5) * dt
                # Future generated data starts now, so its protected lifetime is L,
                # not the already-captured artifact's current age plus L.
                probability_broken = 1.0 if (t_from_now + lifetime) >= break_year else 0.0
                total += rate * probability * probability_broken * dt
            prospective[name] = round(s * total, 6)

    retrospective_component = retrospective["median"] if exposure_key in {"RETROSPECTIVE", "BOTH"} else 0.0
    prospective_component = prospective["median"] if exposure_key in {"PROSPECTIVE", "BOTH"} else 0.0
    combined = round(retrospective_component + prospective_component, 6)
    band = "CRITICAL" if combined >= 1.5 else "HIGH" if combined >= 0.75 else "MEDIUM" if combined >= 0.25 else "LOW"

    return {
        "method": "ECA-PQFA HNDL scenario implementation v3.2",
        "interpretation": "Illustrative sensitivity-weighted exposure quantity; not a probability or calibrated security guarantee.",
        "retrospective_risk": round(retrospective_component, 6),
        "prospective_risk": round(prospective_component, 6),
        "combined_score": combined,
        "risk_band": band,
        "sensitivity_weight": s,
        "exposure_probability": probability,
        "capture_age_years": round(age, 4),
        "confidentiality_horizon_years": round(horizon, 4),
        "migration_window_years": round(migration_years, 4),
        "retrospective_scenarios": retrospective,
        "prospective_scenarios": prospective,
        "distributional_retrospective_sensitivity_weighted": distributional_retrospective,
        "cdf_quantile_convention": {"optimistic": 0.1, "median": 0.5, "pessimistic": 0.9},
        "warning": "The quantile interpolation is uncalibrated and must not be presented as validated CRQC probability. Calibrate the distribution and exposure-rate assumptions before scientific or operational use.",
    }
