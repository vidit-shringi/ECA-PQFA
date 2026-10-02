# ECA-PQFA Architecture v3

```text
                 ┌─────────────────────────────┐
                 │      Research Console       │
                 │ HTML/CSS/JS                 │
                 └──────────────┬──────────────┘
                                │ REST
                 ┌──────────────▼──────────────┐
                 │          FastAPI             │
                 │ auth / CORS / API contracts │
                 └───────┬─────────┬───────────┘
                         │         │
          ┌──────────────▼─┐   ┌──▼──────────────────┐
          │ Verification   │   │ Evidence / Inventory │
          │ claims L0-L3   │   │ hashes / CBOM        │
          └───────┬────────┘   └─────────┬────────────┘
                  │                      │
          ┌───────▼──────────────────────▼────────┐
          │ Provenance + Merkle + Signed Tree Head│
          │ Ed25519 + ML-DSA-65                  │
          └──────────────┬────────────────────────┘
                         │
          ┌──────────────▼───────────────┐
          │ Digital Twin + HNDL + Metrics│
          └──────────────┬───────────────┘
                         │
             ┌───────────▼───────────┐
             │ SQLite / Sheets bridge│
             └───────────────────────┘
```

AI is intentionally not a grading authority. It can generate a hypothesis record, but the assurance ladder requires deterministic/executable evidence and, for L2, an independent verifier.
