# Reproducibility Guide

## Local replay

```bash
python -m venv .venv
# activate the environment
pip install -e .[dev]
python -m pytest -q
python -m backend.app demo
```

## Runtime metadata

Record:

```bash
python --version
openssl version
pip freeze
```

Then preserve the current Git commit:

```bash
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

The end-to-end run writes:

`data/demo/demo_result.json`

This file is a software-validation output. It must not be cited as an empirical result for the research hypotheses.
