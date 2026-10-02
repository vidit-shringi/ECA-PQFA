# Paper-to-Code Map

This map connects the manuscript's framework sections to the repository implementation so that a reviewer or coding agent can move from the research text to the executable component.

| Research concept | Repository implementation |
|---|---|
| Evidence acquisition / evidence object | `backend/app/services/utilities.py`, `backend/app/main.py` (`/api/evidence/hash`), `02_EVIDENCE` schema |
| Cryptographic reconnaissance | `backend/app/services/inventory.py`, `backend/app/services/cbom.py` |
| Claim taxonomy | `backend/app/services/claims.py`, `schemas/claim.schema.json`, `03_CLAIMS` |
| Scope A/B/C/D | `backend/app/services/claims.py` |
| Assurance L0/L1/L2/L3 | `backend/app/services/assurance.py`, `backend/app/services/claims.py` |
| Claim-form-specific verifiers | `backend/app/services/verification.py` |
| Independence relation | `backend/app/services/assurance.py` |
| HNDL retrospective/prospective model | `backend/app/services/hndl.py` |
| Digital twin | `backend/app/main.py` relationship endpoints + `10_DIGITAL_TWIN` schema |
| Provenance record | `backend/app/services/provenance.py` |
| Merkle log | `backend/app/services/merkle.py`, `backend/app/services/provenance.py` |
| Signed tree heads | `backend/app/services/signing.py`, `backend/app/services/provenance.py` |
| PQ signing | `backend/app/services/signing.py` via OpenSSL ML-DSA support |
| CBOM | `backend/app/services/cbom.py` |
| Migration verification data model | `12_MIGRATION`, inventory/claim/verification APIs |
| Experiment records | `13_EXPERIMENTS`, `backend/app/services/metrics.py` |
| Evaluation metrics | `backend/app/services/metrics.py` |
| Google Sheets persistence layer | `apps-script/`, `backend/app/services/sheets.py`, `15_ENUMS/16_README` concepts |
| Research dashboard | `frontend/index.html`, `frontend/styles.css` |
| Reproducible lab run | `scripts/demo_pipeline.py`, `data/synthetic/`, `tests/` |

## Semantic rule

The implementation should preserve the manuscript's separation between:

1. AI-generated hypothesis;
2. executable/deterministic evidence;
3. independent reproduction;
4. formal proof.

Changing code that collapses these stages changes the research model and requires documentation and test updates.
