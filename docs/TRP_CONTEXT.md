# ECA-PQFA TRP Context

## Project identity

**ECA-PQFA** means **Evidence-Carrying AI-Assisted Cryptanalysis and Post-Quantum Forensic Assurance**.

This repository is the complete software implementation and research tool for the university TRP/major-project framework described in the accompanying manuscript. The repository is deliberately structured so that another student, researcher, reviewer, or coding agent can understand the TRP without needing private conversation context.

## Core research idea

The framework treats an AI-generated cryptanalytic idea as a **hypothesis first**, not as a verified fact. A claim is represented conceptually as:

`C = (H, W, E, V, P)`

where:

- `H` — hypothesis;
- `W` — witness;
- `E` — experimental evidence;
- `V` — verification records;
- `P` — provenance.

The implementation preserves claimed scope separately from verified scope and keeps assurance levels separate from any scalar confidence score.

## Scope taxonomy

The software uses these scope classes:

- **A** — design-level;
- **B** — reduced-parameter / reduced-scope experimental;
- **C** — implementation;
- **D** — protocol.

AI/human assistance is represented as provenance/origin (`AI`, `HUMAN`, `HYBRID`, `SYSTEM`) rather than as an additional cryptanalytic scope.

## Claim forms

The implementation recognises:

`EX`, `ST`, `CX`, `PD`, `IM`, `PR`, `NG`, `ID`.

The claim form determines the kind of evidence that can support the claim and the verifier that can be selected.

## Assurance ladder

- **L0** — hypothesis.
- **L1** — executable or deterministic support.
- **L2** — independent reproduction.
- **L3** — formal verification.

The levels are not a probability or confidence score. AI-generated text alone is never sufficient for promotion.

## Independence

The implementation follows the manuscript's error-propagation idea: independence is evaluated against the dimensions relevant to each claim form. Merely assigning two verifier IDs does not make two checks independent.

Examples:

- `EX`: verifier implementation + hardware;
- `ST`: code base + data source + model family + hardware;
- `CX`: verifier implementation + analyst/organisation;
- `IM`: hardware/device + code base;
- `PR`: verifier implementation + analyst/organisation;
- `NG`: model family + data source;
- `ID`: verifier implementation.

## Provenance

Every material state change can be represented as a provenance event. The implementation provides:

- canonical event payload hashing;
- hash-linked event history;
- append-only database protection for provenance records;
- Merkle tree construction;
- inclusion proofs;
- consistency proofs;
- authenticated tree heads;
- classical Ed25519 signing and optional ML-DSA-65 signing through OpenSSL where supported.

A Merkle tree makes conflicting history detectable relative to an authenticated tree head. It is not, by itself, a trusted clock or an external legal timestamp authority.

## Cryptographic inventory and digital twin

The tool scans controlled evidence/configuration directories and records algorithm, parameter-set, protocol and implementation observations. It can export a CycloneDX-style cryptographic bill of materials (CBOM) representation.

The digital twin is a typed relationship graph representing links such as:

`Asset -> Algorithm -> Implementation -> Protocol -> Claim -> Assurance -> Risk -> Migration`

It is a model of the cryptographic estate, not a cycle-accurate hardware simulator.

## HNDL model

The TRP distinguishes:

- **retrospective risk** — artifacts already captured/stored, where later migration does not undo historical exposure;
- **prospective risk** — future data flows for which migration timing changes the exposure horizon.

Inputs include sensitivity, exposure probability, confidentiality lifetime, migration timing, data-generation rate, and optimistic/median/pessimistic break-time scenarios.

The implementation reports the result as a risk/exposure quantity consistent with the model's interpretation; it must not be described as a bounded probability unless the specific calculation establishes that interpretation.

## Evaluation questions

The manuscript defines eight research questions covering identification, HNDL prioritisation, hypothesis utility, independent reproduction, verification effects, cross-device generalisation, forensic reconstruction, and migration verification.

The implementation provides an experiment/metrics scaffold. It does not fabricate results for those questions.

## Experimental integrity

The repository uses synthetic/controlled data for the built-in end-to-end demonstration. A successful tool check is a software-validation result, not evidence that a cryptographic standard is broken or secure.

The software should therefore distinguish:

- hypothesis vs verified result;
- claimed scope vs verified scope;
- absence of an observed attack vs proof of security;
- algorithm identification vs cryptanalytic compromise;
- inventory presence vs behavioural migration verification.

## Relationship to PQC

The tool models post-quantum migration and evidence using NIST's PQC vocabulary, including ML-KEM, ML-DSA and SLH-DSA. The provenance layer can use ML-DSA-65 for signed tree heads when the local OpenSSL installation supports it.

## Intended use

This tool is intended for:

- university TRP/major projects;
- reproducible cybersecurity research;
- controlled cryptographic inventory experiments;
- evidence/claim verification studies;
- provenance and audit research;
- PQC migration and HNDL experiments;
- development of the EVC-Bench-style evaluation workflow described by the manuscript.

It is not intended to substitute for expert cryptanalysis, formal security proofs, certified forensic systems, HSM-backed key custody, or legal evidence procedures.
