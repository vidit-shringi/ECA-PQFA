from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from backend.app.core.schema import SHEETS


PREFIXES = {
    "01_CASES": "CASE",
    "02_EVIDENCE": "EVD",
    "03_CLAIMS": "CLM",
    "04_VERIFICATIONS": "VER",
    "05_PROVENANCE": "EVT",
    "06_ASSETS": "AST",
    "07_ALGORITHMS": "ALG",
    "08_IMPLEMENTATIONS": "IMP",
    "09_PROTOCOLS": "PRT",
    "10_DIGITAL_TWIN": "REL",
    "11_HNDL_RISK": "RSK",
    "12_MIGRATION": "MIG",
    "13_EXPERIMENTS": "EXP",
    "14_AUDIT_LOG": "AUD",
}

ID_FIELDS = {
    "01_CASES": "Case_ID",
    "02_EVIDENCE": "Evidence_ID",
    "03_CLAIMS": "Claim_ID",
    "04_VERIFICATIONS": "Verification_ID",
    "05_PROVENANCE": "Event_ID",
    "06_ASSETS": "Asset_ID",
    "07_ALGORITHMS": "Algorithm_ID",
    "08_IMPLEMENTATIONS": "Implementation_ID",
    "09_PROTOCOLS": "Protocol_ID",
    "10_DIGITAL_TWIN": "Relationship_ID",
    "11_HNDL_RISK": "Risk_ID",
    "12_MIGRATION": "Migration_ID",
    "13_EXPERIMENTS": "Experiment_ID",
    "14_AUDIT_LOG": "Audit_ID",
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha3_256_bytes(data: bytes) -> str:
    return hashlib.sha3_256(data).hexdigest()


def canonical_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(obj: Dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def generate_id(sheet: str, next_number: int) -> str:
    prefix = PREFIXES[sheet]
    year = datetime.now(timezone.utc).year
    width = 5 if prefix == "EVT" else 4
    return f"{prefix}-{year}-{next_number:0{width}d}"


def id_field(sheet: str) -> str:
    return ID_FIELDS[sheet]


def default_record(sheet: str, record: Dict[str, Any]) -> Dict[str, Any]:
    r = dict(record)
    rid_field = ID_FIELDS.get(sheet)
    if rid_field and not r.get(rid_field):
        # Temporary ID is assigned by service before insertion.
        pass
    if sheet == "03_CLAIMS":
        r.setdefault("Verified_Scope", "NOT_VERIFIED")
        r.setdefault("Origin", "HUMAN")
        r.setdefault("Novelty_Status", "NOT_ASSESSED")
        r.setdefault("Assurance_State", "L0")
        r.setdefault("Claim_Status", "DRAFT")
        for x in ("L0","L1","L2","L3"):
            r.setdefault(x, "FALSE")
        r.setdefault("Refuted", "FALSE")
    if sheet == "02_EVIDENCE":
        r.setdefault("Evidence_Status", "REGISTERED")
        r.setdefault("Integrity_Status", "NOT_CHECKED")
    if sheet == "04_VERIFICATIONS":
        r.setdefault("Result", "NOT_RUN")
        r.setdefault("Independence_Status", "PENDING")
    return r
