# Changelog

## 3.2.0 — Professionalized research tool

- Added a working browser research console under frontend/.
- Added API smoke tests for the root console, health endpoint and claim validation.
- Moved CI ownership to .github/workflows/ci.yml with Python 3.10–3.12, smoke testing and package builds.
- Added monthly Dependabot configuration for Python and GitHub Actions.
- Redacted integration identifiers from the public /api/config response.
- Added explicit host/port configuration and centralized version metadata.
- Updated repository metadata, citation information and documentation for the public GitHub project.
- Removed obsolete placeholder/duplicate repository paths.

## 3.1.0 — Complete research tool packaging

- Reframed the repository as a complete research tool/reference implementation rather than a demo-only prototype.
- Added an installable Python package configuration.
- Added the eca-pqfa CLI.
- Added agent context files: AGENTS.md, CLAUDE.md, GEMINI.md.
- Added machine-readable tool_manifest.json.
- Added TRP context, tool specification, API guide, threat model and reproducibility documentation.
- Added OpenAPI export.
- Added GitHub-ready citation metadata and license.
- Removed live spreadsheet/app-script deployment identifiers from public source files; integrations now use explicit configuration.
- Improved launcher portability so the application runs without a manual PYTHONPATH export.

## 3.0.0

- Evidence hashing, claims, L0-L3 assurance, Merkle provenance, signatures, inventory, CBOM, digital twin, HNDL, migration, metrics, dashboard and Sheets bridge.
