# ECA-PQFA

## Evidence-Carrying AI-Assisted Cryptanalysis and Post-Quantum Forensic Assurance

**Version 3.1.0 — Complete Research Tool / Reference Implementation**

ECA-PQFA is a complete, runnable research tool for turning controlled cryptographic evidence into scoped claims, deterministic verification records, assurance states, auditable provenance, cryptographic inventories, CBOM outputs, digital-twin relationships, HNDL risk assessments, and post-quantum migration evidence.

It is designed so that a student, researcher, reviewer, or coding agent can clone the repository, understand the TRP from the repository itself, run the tool, reproduce the synthetic workflow, inspect the API, extend the verification engine, and run the test suite.

> **Important:** "complete research tool" describes the implemented software scope. It does not mean that the tool is a court-certified forensic platform, an HSM-backed security product, or an empirical proof that any cryptographic scheme is secure or broken.

---

## Research concept

The software operationalises the ECA-PQFA evidence-carrying model:

```text
Evidence
   |
   v
Integrity hashing
   |
   v
Cryptographic reconnaissance
   |
   v
Scoped claim C = (H, W, E, V, P)
   |
   v
Claim-form-specific verification
   |
   v
L0 -> L1 -> L2 -> L3
   |
   v
Append-only provenance
   |
   v
Merkle tree + authenticated tree head
   |
   +--------------------+
   |                    |
   v                    v
Digital Twin          HNDL / Migration
   |                    |
   +---------+----------+
             v
      Auditable research output
```

AI can propose hypotheses, but AI output is never treated as an assurance authority.

---

## What is implemented

### Evidence and integrity

- SHA-256 and SHA3-256 evidence hashing.
- Evidence metadata and case linkage.
- Controlled research filesystem boundaries.
- SQLite-backed structured persistence.

### Claim system

- Claim tuple concepts: `H / W / E / V / P`.
- Claim forms: `EX`, `ST`, `CX`, `PD`, `IM`, `PR`, `NG`, `ID`.
- Scopes: `A` design, `B` reduced-parameter, `C` implementation, `D` protocol.
- Claimed-scope vs verified-scope comparison.
- Scope-inflation detection.
- AI/HUMAN/HYBRID/SYSTEM provenance.

### Assurance and verification

- L0 hypothesis.
- L1 executable/deterministic support.
- L2 independent reproduction.
- L3 formal-verification gate.
- Claim-form-specific deterministic verifiers.
- Independence-vector checking.
- Refutation/demotion-compatible record model.

### Provenance and cryptographic audit

- Hash-linked provenance events.
- Database-level protection against provenance UPDATE/DELETE.
- Domain-separated Merkle tree.
- Inclusion proofs.
- Consistency proofs.
- Authenticated tree heads.
- Ed25519 signatures.
- Optional ML-DSA-65 signing through supported OpenSSL installations.
- Explicit reporting when PQ signing is unavailable.

### Cryptographic inventory

- Deterministic algorithm/OID/string detection.
- Controlled-directory scanning.
- CycloneDX-style CBOM output.
- Algorithm, implementation and protocol records.
- Digital-twin relationship graph.

### HNDL and migration

- Retrospective risk for already-captured data.
- Prospective risk for future flows.
- Sensitivity and exposure inputs.
- Confidentiality-lifetime inputs.
- Migration timing.
- Optimistic/median/pessimistic break-time scenarios.
- Migration evidence records.

### Research execution

- Experiment records.
- Evaluation metric scaffold.
- Synthetic end-to-end dataset.
- Browser dashboard.
- FastAPI REST API with OpenAPI documentation.
- Google Sheets synchronization bridge.
- GitHub CI workflow.
- CLI for local tool operation.

---

## Install as a tool

### Recommended

```bash
python -m venv .venv
# activate the environment
pip install -e .[dev]
```

Then:

```bash
eca-pqfa health
eca-pqfa test
eca-pqfa demo
eca-pqfa serve
```

Browser:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### Without installation

```bash
python -m backend.app demo
python -m backend.app serve
python -m pytest -q
```

---

## CLI reference

```text
eca-pqfa health
eca-pqfa serve [--host HOST] [--port PORT] [--reload]
eca-pqfa demo
eca-pqfa test [-k EXPRESSION]
eca-pqfa hash PATH
eca-pqfa inventory PATH [--no-recursive]
eca-pqfa cbom PATH [--output FILE] [--no-recursive]
eca-pqfa audit
eca-pqfa tree-head
```

Examples:

```bash
eca-pqfa hash data/synthetic/tls_config.txt

eca-pqfa inventory data/synthetic

eca-pqfa cbom data/synthetic --output data/demo/synthetic-cbom.json

eca-pqfa audit
```

---

## Complete end-to-end tool run

The built-in synthetic workflow exercises the major components:

```bash
eca-pqfa demo
```

The workflow creates/uses:

1. a synthetic research case;
2. evidence hashes;
3. a scoped identification claim;
4. deterministic verification;
5. provenance events;
6. a Merkle tree head;
7. classical and optional PQ signatures;
8. inventory and CBOM output;
9. HNDL calculation;
10. evaluation metrics.

Output:

`data/demo/demo_result.json`

The output is labelled as a software-validation run and must not be presented as experimental validation of the manuscript's research hypotheses.

---

## Project layout

```text
ECA-PQFA/
├── .github/
│   ├── workflows/
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── apps-script/
│   ├── Code.gs
│   ├── Index.html
│   └── appsscript.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── security/
│   │   └── services/
│   └── __init__.py
├── data/
│   ├── demo/
│   └── synthetic/
├── docs/
│   ├── TRP_CONTEXT.md
│   ├── TOOL_SPEC.md
│   ├── USING_AS_A_RESEARCH_TOOL.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── SECURITY_MODEL.md
│   ├── THREAT_MODEL.md
│   ├── RESEARCH_INTEGRITY.md
│   ├── REPRODUCIBILITY.md
│   ├── PQC_CAPABILITY.md
│   └── openapi.json
├── frontend/
├── paper/
│   └── ECA-PQFA-Paper.pdf
├── schemas/
├── scripts/
├── tests/
├── AGENTS.md
├── CLAUDE.md
├── GEMINI.md
├── CITATION.cff
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── tool_manifest.json
└── README.md
```

---

## REST API

The FastAPI application exposes case, evidence, claims, verification, provenance, inventory, CBOM, HNDL, digital-twin, metrics and Sheets integration operations.

### Main routes

```text
GET  /api/health
GET  /api/config
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

Swagger UI:

`/docs`

Machine-readable schema:

`docs/openapi.json`

---

## Google Sheets integration

Google Sheets is used as a structured persistence/synchronization layer, not as the authoritative cryptographic log.

Configure:

```text
ECA_PQFA_SPREADSHEET_ID
ECA_PQFA_APPS_SCRIPT_URL
ECA_PQFA_API_KEY
ECA_PQFA_REQUIRE_API_KEY
```

Keep Apps Script secrets in Script Properties. Never commit passwords, API keys, private signing keys, personal data, or confidential evidence.

See:

- `apps-script/`
- `docs/DEPLOYMENT.md`
- `docs/CURRENT_INTEGRATION.txt`

---

## Security model

The software currently provides meaningful integrity and research-governance mechanisms, including:

- content hashing;
- append-only provenance protection;
- Merkle inclusion/consistency proofs;
- signed tree heads;
- optional PQ signing;
- API-key protected mutation routes;
- local-path restrictions;
- security headers and configurable CORS;
- explicit AI provenance;
- claim-scope validation.

For production/high-assurance deployment, additional engineering is required around identity/RBAC, HSM/KMS, encrypted storage, external trusted timestamping, deployment hardening, multi-party authorization and long-term key lifecycle.

---

## Research integrity

The software does not make empirical claims that the manuscript has not demonstrated.

In particular:

- a PASS means the tested proposition passed its selected verification check;
- identification is not proof of compromise;
- implementation evidence does not automatically become a design-level result;
- no observed attack is not a proof of security;
- AI output alone cannot promote a claim;
- synthetic demo output is not a research result.

Read `docs/TRP_CONTEXT.md` and `docs/RESEARCH_INTEGRITY.md` before extending the system.

---

## Research paper and context

The repository contains the manuscript used to define the framework and the machine-readable context files needed by development agents.

Start here:

1. `docs/TRP_CONTEXT.md`
2. `docs/TOOL_SPEC.md`
3. `docs/USING_AS_A_RESEARCH_TOOL.md`
4. `paper/ECA-PQFA-Paper.pdf`

AI/coding agents should also read `AGENTS.md`.

---

## Tests and CI

Local:

```bash
python -m pytest -q
```

CI runs across Python 3.10, 3.11 and 3.12, compiles the project, runs the tests, and executes the synthetic end-to-end workflow.

---

## License and citation

The software is released under the MIT License. See `LICENSE` and `CITATION.cff`.
