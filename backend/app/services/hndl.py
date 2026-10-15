from __future__ import annotations

from datetime import date
from math import isfinite
from typing import Dict

SENSITIVITY = {"LOW": 0.25, "MEDIUM": 0.5, "HIGH": 0.75, "CRITICAL": 1.0}


def years_between(a: date, b: date) -> float:
    return max(0.0, (b - a).days / 365.25)


def break_cdf(t_years: float, optimistic: float, median: float, pessimistic: float) -> float:
    """Piecewise-linear CDF approximation using the three declared quantiles (10/50/90%)."""
    values = [float(optimistic), float(median), float(pessimistic)]
    if not all(isfinite(x) and x >= 0 for x in values):
        raise ValueError("CRQC quantiles must be finite non-negative years")
    if not values[0] <= values[1] <= values[2]:
        raise ValueError("CRQC quantiles must satisfy optimistic <= median <= pessimistic")
    qs = [(values[0], 0.1), (values[1], 0.5), (values[2], 0.9)]
    if t_years < qs[0][0]:
        return 0.0
    for (x1, p1), (x2, p2) in zip(qs, qs[1:]):
        if t_years <= x2:
            if x2 == x1:
                return p2
            return p1 + (p2 - p1) * (t_years - x1) / (x2 - x1)
    return 1.0


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
    """Scenario-based HNDL assessment; outputs are scores, not probabilities or guarantees."""
    sensitivity_key = str(sensitivity).upper()
    exposure_key = str(exposure_type).upper()
    if sensitivity_key not in SENSITIVITY:
        raise ValueError("sensitivity must be LOW, MEDIUM, HIGH or CRITICAL")
    if exposure_key not in {"RETROSPECTIVE", "PROSPECTIVE", "BOTH"}:
        raise ValueError("exposure_type must be RETROSPECTIVE, PROSPECTIVE or BOTH")
    lifetime = float(confidentiality_lifetime_years)
    rate = float(data_generation_rate)
    probability = float(exposure_probability)
    quantiles = [float(optimistic_crqc_years), float(median_crqc_years), float(pessimistic_crqc_years)]
    if not isfinite(lifetime) or lifetime < 0:
        raise ValueError("confidentiality_lifetime_years must be finite and non-negative")
    if not isfinite(rate) or rate < 0:
        raise ValueError("data_generation_rate must be finite and non-negative")
    if not isfinite(probability) or not 0 <= probability <= 1:
        raise ValueError("exposure_probability must be between 0 and 1")
    optimistic, median, pessimistic = quantiles
    # Validate quantile ordering and values.
    break_cdf(0.0, optimistic, median, pessimistic)

    cap = date.fromisoformat(capture_date)
    cur = date.fromisoformat(current_date)
    mig = date.fromisoformat(migration_date)
    if mig < cur:
        raise ValueError("migration_date must not precede current_date")
    sensitivity_weight = SENSITIVITY[sensitivity_key]
    capture_age = years_between(cap, cur)
    retrospective_horizon = capture_age + lifetime
    scenarios = {"optimistic": optimistic, "median": median, "pessimistic": pessimistic}
    retrospective_scenarios = {
        label: round(sensitivity_weight * probability * (1.0 if retrospective_horizon >= q else 0.0), 6)
        for label, q in scenarios.items()
    }
    distributional_retrospective = round(
        sensitivity_weight * probability * break_cdf(retrospective_horizon, optimistic, median, pessimistic), 6
    )

    migration_years = years_between(cur, mig)
    steps = 120
    prospective_scenarios: Dict[str, float] = {}
    if exposure_key not in {"PROSPECTIVE", "BOTH"}:
        prospective_scenarios = {key: 0.0 for key in scenarios}
    else:
        dt = migration_years / steps if migration_years > 0 else 0.0
        for label, break_year in scenarios.items():
            integral = 0.0
            for j in range(steps):
                t = (j + 0.5) * dt
                # Future data starts at current time; do not add the age of previously
                # captured data to the future-flow confidentiality horizon.
                cdf = 1.0 if (t + lifetime) >= break_year else 0.0
                integral += rate * probability * cdf * dt
            prospective_scenarios[label] = round(sensitivity_weight * integral, 6)

    retrospective_component = retrospective_scenarios["median"] if exposure_key in {"RETROSPECTIVE", "BOTH"} else 0.0
    prospective_component = prospective_scenarios["median"] if exposure_key in {"PROSPECTIVE", "BOTH"} else 0.0
    combined = round(retrospective_component + prospective_component, 6)
    band = "CRITICAL" if combined >= 1.5 else "HIGH" if combined >= 0.75 else "MEDIUM" if combined >= 0.25 else "LOW"
    return {
        "method": "ECA-PQFA HNDL two-component implementation v3.2",
        "interpretation": "Scenario-weighted exposure score; not a probability and not a security guarantee.",
        "retrospective_risk": round(retrospective_component, 6),
        "prospective_risk": round(prospective_component, 6),
        "combined_score": combined,
        "risk_band": band,
        "sensitivity_weight": sensitivity_weight,
        "exposure_probability": probability,
        "capture_age_years": round(capture_age, 4),
        "confidentiality_horizon_years": round(retrospective_horizon, 4),
        "migration_window_years": round(migration_years, 4),
        "retrospective_scenarios": retrospective_scenarios,
        "prospective_scenarios": prospective_scenarios,
        "distributional_retrospective_median_curve": distributional_retrospective,
        "cdf_quantile_convention": {"optimistic": 0.1, "median": 0.5, "pessimistic": 0.9},
        "warning": "The CRQC quantiles and sensitivity/exposure parameters require empirical calibration before scientific or operational risk decisions.",
    }
