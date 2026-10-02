# Threat Model

## Assets

- Evidence hashes and metadata.
- Claim statements and verified scope.
- Verification records.
- Provenance events and tree heads.
- Signing keys.
- Digital twin relationships.
- HNDL and migration results.
- Google Sheets persistence credentials.

## Adversaries / failure modes

1. Accidental edit of evidence or metadata.
2. Application-level deletion/rewrite of provenance.
3. Unsigned or inconsistent tree-head substitution.
4. Scope inflation.
5. AI hallucination treated as verification.
6. Path traversal to arbitrary files.
7. Unauthorised spreadsheet mutation.
8. Key compromise or signing-key misuse.
9. Environment drift that prevents exact reproduction.
10. Confusing software-validation checks with cryptographic proof.

## Current mitigations

- SHA-256 and SHA3-256 evidence fingerprints.
- Hash-linked provenance.
- SQLite triggers preventing provenance UPDATE/DELETE.
- Merkle inclusion and consistency proofs.
- Authenticated tree heads.
- Ed25519 and optional ML-DSA-65 signatures.
- API-key authentication for mutation routes.
- Restricted filesystem roots.
- Security headers/CORS configuration.
- Explicit AI provenance and independent verification rules.

## Trust assumptions

The system assumes a trustworthy host, operator authorisation, secure signing-key storage, trustworthy software dependencies, correct system configuration, and a reliable trusted-time strategy when long-term external timestamping is required.

## Out of scope

The tool is not a court-certified evidence system, HSM, PKI, production SIEM, or a general-purpose autonomous cryptanalysis platform.
