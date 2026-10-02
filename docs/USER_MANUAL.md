# ECA-PQFA User Manual\n\nVersion 3.2.0

## Browser research console\nStart the service with `eca-pqfa serve` and open `http://127.0.0.1:8000`. The console exposes health, dashboard counts, claim validation, inventory/CBOM and provenance audit operations.\n\n## Dashboard
Use the dashboard to confirm the API is running and inspect high-level counts.

## Cases
Create a case first. Use `SYNTHETIC_TEST` for development data. A case ID is generated automatically.

## Claims
Enter the case ID and claim details.
Use **Validate** first.
The scope status distinguishes:
- `SCOPE_MATCH`
- `VERIFIED_SCOPE_NARROWER`
- `MISSING_VERIFIED_SCOPE`
- `SCOPE_INFLATION`

A claim should not be presented as a broader result than its verified scope.

## Evidence
Use the evidence hashing endpoint for local files. The hash result can be registered in `02_EVIDENCE` with a Drive file ID/URL when the evidence is stored in Google Drive.

## Verification
Record the verifier, version, environment, result and independence notes.
A different Verification ID does not by itself prove independent reproduction.

## Inventory / CBOM
Point the scanner at a controlled directory such as `data/synthetic`.
It detects documented algorithm strings/OIDs and creates a CycloneDX-style inventory representation.

## HNDL
The current module implements the paper's retrospective/prospective structure. Calibrate its probability distributions and measured/elicited inputs before reporting scientific results.

## Provenance
The backend maintains a hash-linked provenance event chain and can audit its continuity.
