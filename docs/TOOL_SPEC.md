# ECA-PQFA Tool Specification

## One-line description

ECA-PQFA is a complete research tool that converts controlled cryptographic evidence into scoped, verifiable claims with auditable provenance, cryptographic inventory, HNDL assessment, and PQC migration evidence.

## Quick mental model

```text
INPUT
  Evidence / configuration / experiment
        |
        v
INTEGRITY
  SHA-256 + SHA3-256
        |
        v
RECONNAISSANCE
  Algorithm / implementation / protocol observations
        |
        v
CLAIM
  Form + target + attack model + scope
        |
        v
VERIFICATION
  Claim-form-specific deterministic checks
        |
        v
ASSURANCE
  L0 -> L1 -> L2 -> L3
        |
        v
PROVENANCE
  Hash chain -> Merkle tree -> signed tree head
        |
        +----> DIGITAL TWIN / CBOM
        |
        +----> HNDL / MIGRATION
        |
        v
AUDITABLE OUTPUT
```

## What the tool can do now

| Capability | Status |
|---|---|
| Evidence hashing | Implemented |
| Claim validation | Implemented |
| Scope inflation detection | Implemented |
| Claim-form verification | Implemented for supported deterministic checks |
| L0-L3 assurance logic | Implemented |
| Independence checking | Implemented |
| Append-only provenance protection | Implemented |
| Merkle inclusion proofs | Implemented |
| Merkle consistency proofs | Implemented |
| Signed tree head | Implemented |
| Ed25519 | Implemented |
| ML-DSA-65 via OpenSSL | Optional when local OpenSSL supports it |
| Algorithm inventory | Implemented |
| CBOM export | Implemented |
| Digital twin relationships | Implemented |
| HNDL calculation | Implemented according to the current tool model |
| Experiment metrics scaffold | Implemented |
| Google Sheets bridge | Implemented |
| Browser dashboard | Implemented |
| CLI | Implemented |

## CLI

Install locally:

```bash
pip install -e .
```

Commands:

```bash
eca-pqfa health
eca-pqfa serve
eca-pqfa demo
eca-pqfa test
eca-pqfa hash data/synthetic/tls_config.txt
eca-pqfa inventory data/synthetic
eca-pqfa cbom data/synthetic --output data/demo/synthetic-cbom.json
eca-pqfa audit
eca-pqfa tree-head
```

## REST API

The FastAPI service is available at `/docs` when the server is running.

Primary endpoints:

```text
GET  /api/health
GET  /api/dashboard
GET  /api/sheets
GET  /api/records/{sheet}
GET  /api/records/{sheet}/{record_id}
POST /api/records
PATCH /api/records
DELETE /api/records/{sheet}/{record_id}
POST /api/claims/validate
POST /api/claims
POST /api/evidence/hash
POST /api/inventory/scan
POST /api/inventory/cbom
POST /api/verification/run
POST /api/verification/promote
POST /api/experiments/evaluate
POST /api/hndl/calculate
POST /api/provenance/event
GET  /api/provenance/audit
POST /api/provenance/tree-head
GET  /api/provenance/inclusion/{event_id}
GET  /api/provenance/consistency
GET  /api/provenance/verify-inclusion
GET  /api/graph
POST /api/relationship
POST /api/sheets/health
POST /api/sheets/sync
```

## Persistence

The computation authority is the local Python/SQLite layer. Google Sheets is a structured synchronisation/persistence option. Evidence bytes should remain in controlled file storage or Google Drive; the sheet stores identifiers, metadata and hashes.

## Security boundary

The tool protects against several accidental or application-level integrity failures, but it assumes trustworthy execution, trusted key custody, correct cryptographic libraries and an authorised operator. For high-assurance use, add identity, RBAC, HSM/KMS-backed keys, external time anchoring, secure deployment, encrypted storage and multi-party audit controls.

## Agent/coding-assistant rule

When modifying this project:

1. Read `AGENTS.md` and `docs/TRP_CONTEXT.md` first.
2. Preserve the distinction between proposed framework, experimental result and software-validation result.
3. Never promote an AI-origin claim directly to assurance.
4. Do not broaden verified scope beyond evidence.
5. Do not invent experimental measurements.
6. Update tests and documentation for every semantic change.
7. Keep synthetic data clearly labelled.
