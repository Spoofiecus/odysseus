---
name: odysseus-security
description: Security and secrets rules for Odysseus — what never to commit, deployment posture, and the pre-push secret scan.
---

# Odysseus Security Rules

## Never commit
Live `.env` values, `data/` contents, local databases (`odysseus.db`, `app.db`), uploaded files, generated media, logs, backups, auth/session files, API keys, model/provider tokens, password hashes, personal documents, or public IPs. Only `.env.example`, docs, source, tests, and static assets belong in the repo.

## Pre-push check
```bash
git status --short
git check-ignore -v .env data/auth.json data/app.db logs/compound.log odysseus.db
git grep -n -I -E "(sk-[A-Za-z0-9_-]{20,}|xox[baprs]-|AIza[0-9A-Za-z_-]{20,}|Bearer [A-Za-z0-9._~+/-]{20,})" -- . ':!static/lib/**' ':!package-lock.json'
```

## Code rules
- Odysseus is a self-hosted app with privileged local capabilities (shell, model serving, MCP, email). It must not be run as a public unauthenticated service.
- Defaults to preserve: `AUTH_ENABLED=true` for any network-accessible deployment; `LOCALHOST_BYPASS=false` outside local dev; leave `SECURE_COOKIES` unset (auto-set on HTTPS) unless overriding deliberately.
- Internal-only services/ports: Odysseus 7000, SearXNG 8080, ntfy 8091, ChromaDB 8100, Ollama 11434, model/provider APIs 8000-8200.
- High-risk agent tools (shell, Python, file read/write, email, MCP, app API, task/skill/memory management, settings, tokens, model serving) are admin-restricted functionality.
- Vulnerabilities are reported privately per SECURITY.md — never disclose exploit details in public issues.
- Repo has CI secret scanning (`.github/workflows/secret-scan.yml`, CodeQL, container scans) — these gates must pass.
