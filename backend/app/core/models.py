from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator


class RecordRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sheet: str
    record: Dict[str, Any] = Field(default_factory=dict)


class UpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    sheet: str
    id_field: Optional[str] = None
    id_value: str
    patch: Dict[str, Any] = Field(default_factory=dict)


class ClaimRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
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

    @field_validator("case_id", "claim_statement", "claim_form", "claimed_scope")
    @classmethod
    def non_empty_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be empty")
        return value

    @field_validator("claim_form")
    @classmethod
    def normalize_claim_form(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("claimed_scope", "verified_scope")
    @classmethod
    def normalize_scope(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("origin")
    @classmethod
    def normalize_origin(cls, value: str) -> str:
        return value.strip().upper()


class EvidenceFileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str


class InventoryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    path: str
    recursive: bool = True


class RelationshipRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
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
    model_config = ConfigDict(extra="forbid")
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
