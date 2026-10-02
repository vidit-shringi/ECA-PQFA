# API Usage

Start the service:

```bash
eca-pqfa serve
```

Open Swagger UI:

`http://127.0.0.1:8000/docs`

## Health

```bash
curl http://127.0.0.1:8000/api/health
```

## Validate a claim

```bash
curl -X POST http://127.0.0.1:8000/api/claims/validate \
  -H 'Content-Type: application/json' \
  -d '{
    "case_id":"CASE-2026-0001",
    "claim_form":"ID",
    "claim_statement":"The controlled artifact contains ML-KEM.",
    "target":"synthetic-artifact",
    "algorithm":"ML-KEM",
    "parameter_set":"ML-KEM-768",
    "attack_model":"IDENTIFICATION",
    "claimed_scope":"C",
    "verified_scope":"C",
    "origin":"HUMAN"
  }'
```

## Hash evidence

```bash
curl -X POST http://127.0.0.1:8000/api/evidence/hash \
  -H 'Content-Type: application/json' \
  -d '{"path":"data/synthetic/tls_config.txt"}'
```

## Inventory

```bash
curl -X POST http://127.0.0.1:8000/api/inventory/scan \
  -H 'Content-Type: application/json' \
  -d '{"path":"data/synthetic","recursive":true}'
```

## CBOM

```bash
curl -X POST http://127.0.0.1:8000/api/inventory/cbom \
  -H 'Content-Type: application/json' \
  -d '{"path":"data/synthetic","recursive":true}'
```

Mutation routes require `X-ECA-API-Key` when `ECA_PQFA_REQUIRE_API_KEY=true`.
