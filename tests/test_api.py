from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app


def test_root_and_health():
    with TestClient(app) as client:
        root = client.get("/")
        health = client.get("/api/health")
        assert root.status_code == 200
        assert "ECA-PQFA" in root.text
        assert health.status_code == 200
        assert health.json()["ok"] is True


def test_claim_validation_endpoint():
    payload = {
        "case_id": "CASE-2026-0001",
        "claim_form": "ID",
        "claim_statement": "The controlled synthetic artifact contains ML-KEM.",
        "target": "synthetic-artifact",
        "algorithm": "ML-KEM",
        "parameter_set": "ML-KEM-768",
        "attack_model": "IDENTIFICATION",
        "claimed_scope": "C",
        "verified_scope": "C",
        "origin": "HUMAN",
    }
    with TestClient(app) as client:
        response = client.post("/api/claims/validate", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["valid"] is True
        assert body["scope_status"] == "SCOPE_MATCH"


def test_scope_inflation_is_rejected():
    payload = {
        "case_id": "CASE-2026-0001",
        "claim_form": "ID",
        "claim_statement": "The implementation-level observation applies at design level.",
        "claimed_scope": "A",
        "verified_scope": "C",
        "origin": "AI",
    }
    with TestClient(app) as client:
        response = client.post("/api/claims/validate", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["valid"] is False
        assert body["scope_status"] == "VERIFIED_SCOPE_NARROWER"
