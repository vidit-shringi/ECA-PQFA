# ECA-PQFA Agent Instructions

Read these files before changing the project:

1. `README.md`
2. `docs/TRP_CONTEXT.md`
3. `docs/TOOL_SPEC.md`
4. `docs/RESEARCH_INTEGRITY.md`
5. `docs/SECURITY_MODEL.md`

## Non-negotiable semantics

- AI generates hypotheses; it is not the assurance authority.
- Never expand verified scope beyond actual evidence.
- L0-L3 are assurance states, not confidence percentages.
- Negative results are not security proofs.
- Identification is not compromise.
- A Merkle root is not an independent trusted timestamp.
- Google Sheets is persistence/synchronisation, not the authoritative immutable provenance ledger.
- Do not fabricate experimental results.
- Synthetic fixtures must remain labelled synthetic.

## Engineering expectations

- Keep deterministic checks reproducible.
- Update tests when semantics change.
- Keep public API behaviour documented.
- Preserve hash/signature verification behaviour.
- Avoid committing secrets or private keys.
