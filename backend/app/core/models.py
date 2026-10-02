from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RecordRequest(BaseModel):
    sheet: str
    record: Dict[str, Any] = Field(default_factory=dict)


class UpdateRequest(BaseModel):
    sheet: str
    id_field: Optional[str] = None
    id_value: str
    patch: Dict[str, Any] = Field(default_factory=dict)


class ClaimRequest(BaseModel):
    case_id: str
    claim_form: str
    claim_statement: str
    target: str = ""
    algorithm: str = ""
    parameter_set: str = ""
    attack_model: str = ""
    claimed_scope: str
    verified_scope: str = "NOT_VERIFIED"
    origin: str = "HUMAN"
    novelty_status: str = "NOT_ASSESSED"
    evidence_id: str = ""
    witness_id: str = ""
    verification_id: str = ""


class EvidenceFileRequest(BaseModel):
    path: str


class InventoryRequest(BaseModel):
    path: str
    recursive: bool = True


class RelationshipRequest(BaseModel):
    case_id: str
    source_id: str
    source_type: str
    relationship: str
    target_id: str
    target_type: str
    assurance_level: str = "L0"
    evidence_id: str = ""
    claim_id: str = ""
    status: str = "ACTIVE"
    notes: str = ""


class HNDLRequest(BaseModel):
    sensitivity: str = "MEDIUM"
    exposure_type: str = "RETROSPECTIVE"
    capture_date: str
    current_date: str
    confidentiality_lifetime_years: float
    migration_date: str
    optimistic_crqc_years: float
    median_crqc_years: float
    pessimistic_crqc_years: float
    data_generation_rate: float = 1.0
    exposure_probability: float = 1.0
