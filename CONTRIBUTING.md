# Contributing to ECA-PQFA

## Before changing code

Read:

- `AGENTS.md`
- `docs/TRP_CONTEXT.md`
- `docs/TOOL_SPEC.md`
- `docs/RESEARCH_INTEGRITY.md`
- `docs/SECURITY_MODEL.md`

## Development

```bash
python -m venv .venv
# activate
pip install -e ".[dev]"
python -m pytest -q
python -m backend.app demo
```

## Pull requests

Every pull request should explain:

1. what changed;
2. which research/tool semantics changed;
3. which tests were added or updated;
4. whether any API/schema compatibility changed.

Do not add real credentials, private keys, confidential evidence or personal data.

## Research contributions

Research claims must be labelled as proposed, expected, or observed according to their actual status. A software test result is not automatically a cryptanalytic result.
