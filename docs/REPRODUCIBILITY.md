# Reproducibility Guide

## Local replay

For local development only, authentication may be explicitly disabled. Do not expose that configuration on a shared network.

### Windows PowerShell (local demo)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
$env:ECA_PQFA_REQUIRE_API_KEY = "false"
python -m pytest -q
python -m backend.app demo
```

### Authenticated run

```powershell
$env:ECA_PQFA_REQUIRE_API_KEY = "true"
$env:ECA_PQFA_API_KEY = "<generate-a-unique-random-secret>"
python -m pytest -q
python -m backend.app demo
```

For API mutations, pass the key in the `X-ECA-API-Key` header. Never commit the secret.

## Runtime metadata

Record:

```bash
python --version
openssl version
pip freeze
git rev-parse HEAD
```

## Synthetic evidence

The built-in synthetic artifacts are the default reproducibility corpus:

- `data/synthetic/lab_config.txt`
- `data/synthetic/test_vector.txt`
- `data/synthetic/tls_config.txt`
- `data/synthetic/statistics.csv`
- `data/synthetic/evidence_manifest.json`

Do not replace these files with confidential evidence in a public repository.

## Demo artifact

The end-to-end run writes `data/demo/demo_result.json`. This is a software-validation output, not empirical validation of the manuscript's research hypotheses. Re-running the demo appends synthetic data to the configured database; use a fresh `ECA_PQFA_DB_PATH` when you need a clean, repeatable run.
