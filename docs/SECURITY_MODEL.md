# ECA-PQFA Security Model

## Threats considered

1. Accidental evidence modification.
2. Deletion or alteration of provenance events in the local database.
3. Inconsistent or forged tree-head metadata.
4. Scope inflation in AI-generated claims.
5. AI output being incorrectly treated as verification.
6. Path traversal into arbitrary local files through the API.
7. Unauthorized mutation of the Google Sheets persistence layer.
8. Confusion between cryptographic inventory and cryptographic proof.

## Controls

- SHA-256 + SHA3-256 evidence fingerprints.
- Hash-linked provenance events.
- SQLite triggers preventing UPDATE/DELETE on provenance events.
- RFC-style domain-separated Merkle tree.
- Inclusion and consistency proofs.
- Signed tree heads using Ed25519 and ML-DSA-65 when available.
- API-key authentication for mutation routes.
- Configurable CORS.
- Security response headers.
- Restricted research filesystem roots.
- Google Apps Script secret stored in Script Properties rather than source.
- AI provenance tracked independently from assurance.

## Trust assumptions

The system still requires a trusted execution environment, trusted signing-key custody, trustworthy system time or an external timestamping service, correct OpenSSL/PQC implementations, and an authorized operator. A Merkle root without a trusted authenticated tree head is only a local integrity commitment.

## Hybrid-signature wording

The research tool records both signatures and requires both verification checks when both are present. It does **not** make the unconditional statement that “security of the combination follows if either algorithm is secure.” Composition security depends on the exact construction, verification policy, key handling and threat model.

## Google Sheets

Google Sheets is a persistence/synchronisation layer. It is not the authoritative cryptographic log. Provenance integrity is computed by the Python engine.
