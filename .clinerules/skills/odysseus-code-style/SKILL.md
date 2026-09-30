---
name: odysseus-code-style
description: Hard code rules for Odysseus — constants in src/constants.py, no hardcoded paths/ports/URLs, no Unicode emoji, and where config lives.
---

# Odysseus Code Rules

## Single source of truth: src/constants.py
- **Filesystem paths:** never build writable paths from `Path(__file__)`, hardcode `/app/...`, or use relative `"data/..."` strings. Every persisted file/dir has a named constant in `src/constants.py` (`AUTH_FILE`, `USER_PREFS_FILE`, `SETTINGS_FILE`, `TTS_CACHE_DIR`, `CHROMA_DIR`, …). Import and use the constant — do not re-derive paths with `os.path.join(DATA_DIR, "x.json")`.
- `DATA_DIR` is the only place that reads `ODYSSEUS_DATA_DIR`; use it directly only for dynamic paths with no fixed name (e.g. per-owner files). If a data file/dir has no constant yet, **add one** to `src/constants.py`. (`core/constants.py` only re-exports for backward compat.)
- Guard directory creation so an unwritable path degrades gracefully — never crash at import. The source tree is read-only in Docker and `/app/...` doesn't exist on native runs.
- **Internal API / loopback URLs:** never hardcode `http://localhost:7000`. Use `internal_api_base()` from `src.constants` (honors `ODYSSEUS_INTERNAL_BASE` / `APP_PORT`).
- **Ports, limits, model lists, etc.:** reuse the existing constant; if none exists and the value is used in more than one place, add a constant instead of copying the literal.

## UI code rules
- **No Unicode emoji in UI or code.** Use inline SVG (monochrome icon style already in `static/index.html`) or plain text.
- Never override the monospaced UI font (Fira Code).
- Dark theme is the default; any light-mode work goes through the existing theme system, not hardcoded values.

## Environment
- Python 3.11+. Manual run: `python -m uvicorn app:app --host 127.0.0.1 --port 7000`.
- Docker is the recommended test path. Windows is not actively tested.
- Configuration lives in `.env` (see `.env.example`); never commit live `.env` values.
