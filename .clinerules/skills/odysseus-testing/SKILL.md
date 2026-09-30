---
name: odysseus-testing
description: How to run and add tests in Odysseus — pytest, taxonomy markers, run_focus.py, fast lane, and testing rules from tests/TESTING_STANDARD.md.
---

# Odysseus Testing Rules

## Running tests
```bash
# Use the project venv, not system Python:
./venv/bin/python -m pytest
python -m pytest -m area_security                 # focused area
python -m pytest -m "area_services and sub_cookbook"

# Focused runner (validates marker names):
./venv/bin/python tests/run_focus.py --area security
./venv/bin/python tests/run_focus.py --area services --sub-area cookbook --fast
./venv/bin/python tests/run_focus.py --last-failed
./venv/bin/python tests/run_focus.py --keyword taxonomy
```

## Syntax checks (smallest relevant check for your change)
```bash
python -m pytest
python -m py_compile app.py routes/*.py src/*.py
node --check static/js/<changed-file>.js
```

## Docker changes
```bash
docker compose config
docker compose up -d --build
docker compose logs --tail=120 odysseus
```

## Taxonomy
- `tests/conftest.py` auto-tags each test with `area_*` and `sub_*` markers from its filename (via `tests/_taxonomy.py`).
- Areas: `security`, `routes`, `services`, `cli`, `js`, `helpers`, `unit`, `uncategorized`.
- `area_*` markers are registered in pyproject.toml; `sub_*` are registered at collection time.

## Fast lane
- `--fast` adds `not slow`. The `slow` marker is **opt-in and requires duration evidence** (from `--durations`), never a guess.
- `--fast` is for quick feedback only — it does not replace the full suite before merge.

## Writing tests (TESTING_STANDARD.md)
- Follow the behavioral-first policy: test observable behavior, not source text.
- Follow determinism & isolation rules: no test may depend on another test's order or shared mutable state (use `tests/run_order_report.py --seed N --` to investigate order sensitivity; report-only).
- Extract shared helpers/factories per the helper extraction rules in tests/README.md — read tests/README.md and tests/TESTING_STANDARD.md before adding a helper under `tests/helpers/`.
- New test files should be named so the taxonomy classifies them correctly (area keyword in filename).

## CI (what will run on your PR)
`.github/workflows/ci.yml`: Python syntax (compileall), JS syntax (node --check), pytest, plus focused-test guidance (report-only). Docs-only changes skip the Python test job. Other gates: codeql, container scans, dependency review, secret-scan.
