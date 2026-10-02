# Using ECA-PQFA as a Full Research Tool

This repository is not a demo-only application. It is the complete runnable software package for the current ECA-PQFA research framework. The word "research" describes the purpose and epistemic boundary of the system; it does not mean that the software is merely a mock-up.

## Recommended workflow

### 1. Create a case

A case groups evidence, claims, verification records, experiments, risk and migration observations.

### 2. Register evidence

Hash the controlled evidence file. Preserve the SHA-256 and SHA3-256 values and record acquisition metadata.

### 3. Reconnaissance

Run inventory/CBOM generation against a controlled directory. Treat detected algorithms as identification observations until verified.

### 4. Create a claim

Specify:

- claim form;
- target;
- algorithm/parameter set;
- attack model;
- claimed scope;
- evidence/witness;
- origin.

### 5. Verify

Select the verifier associated with the claim form. Save the verifier identifier, version, environment, input hash, result and scope.

### 6. Promote assurance

Use the assurance rules. L1 requires an accepting verifier outside the generator's code path. L2 requires an independent second acceptance according to the claim-form independence vector. L3 requires a checked proof artifact plus human review of model adequacy.

### 7. Seal provenance

Append events, create the Merkle tree head, preserve the signatures and retain the root as an audit reference.

### 8. Assess HNDL and migration

Separate already-captured evidence from future data flows. Record the assumptions/scenarios that produced the risk output.

### 9. Export and reproduce

Use the CBOM output, JSON results, provenance data, experiment records and repository commit to reproduce a run.

## What counts as a result

A software run is a result about the **tested proposition in the tool**, not an automatic result about the underlying cryptographic scheme. Higher-level cryptanalytic conclusions require their corresponding witness, verification and scope evidence.

## Suggested lab modes

- `SYNTHETIC_TEST` — built-in controlled data.
- `RESEARCH_REPLAY` — re-run a saved experiment against fixed hashes and environment metadata.
- `CONTROLLED_ARTIFACT_ANALYSIS` — analyse authorised evidence in a defined laboratory perimeter.
- `MIGRATION_VALIDATION` — test explicitly scoped configuration and migration assertions.

## Reproducibility record

For each reported experiment, preserve:

- Git commit hash;
- operating system;
- Python version;
- package versions;
- OpenSSL version and PQ capability;
- dataset hash;
- evidence hashes;
- configuration;
- random seeds where applicable;
- verifier identifiers;
- output hashes;
- provenance tree head.
