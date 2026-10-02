# GitHub Project Guide

## Repository name

`vidit-shringi/ECA-PQFA`

## Suggested description

`Evidence-Carrying AI-Assisted Cryptanalysis and Post-Quantum Forensic Assurance — complete university research tool and reference implementation.`

## First push

From the extracted repository root:

```bash
git init
git branch -M main
git add .
git commit -m "Release: ECA-PQFA 3.2.0"
git remote add origin https://github.com/vidit-shringi/ECA-PQFA.git
git push -u origin main
```

## First release

```bash
git tag -a v3.2.0 -m "ECA-PQFA complete research tool v3.1.0"
git push origin v3.1.0
```

## GitHub landing page

The landing page should point contributors to:

1. `README.md` for installation and capabilities.
2. `docs/TRP_CONTEXT.md` for the research concept.
3. `docs/TOOL_SPEC.md` for machine-readable/agent-friendly tool semantics.
4. `docs/API.md` for REST usage.
5. `paper/ECA-PQFA-Paper.pdf` for the manuscript.

## Do not commit

- `.env` files containing live values;
- private signing keys;
- SQLite runtime databases;
- real forensic evidence;
- private PCAPs or credentials;
- confidential Google Drive files;
- personal data.

The repository's `.gitignore` already excludes the main runtime categories.
