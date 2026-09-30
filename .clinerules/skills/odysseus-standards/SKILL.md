---
name: odysseus-standards
description: Project conventions for contributing to Odysseus — branch model, PR rules, commit format, and scope discipline. Apply before any change or PR.
---

# Odysseus Contributing Standards

Source of truth: CONTRIBUTING.md, .github/pull_request_template.md, SECURITY.md, tests/TESTING_STANDARD.md.

## Branch model
- **`dev`** is the working branch — all PRs land there. Never open PRs against `main` (curated, maintainer-owned).
- Keep changes focused: **one bug fix or feature per PR**. No broad rewrites, formatting-only changes, or file moves unless the issue is about structure.
- Search existing issues/PRs before starting; for large features, open an issue describing the approach first.
- Every PR must be linked to an issue (`Fixes #NNN` / `Part of #NNN` / `Closes #NNN`).

## Commits
Use Conventional Commits: `type(scope): summary` — e.g. `fix(search): ...`, `feat(notes): ...`, `docs(contributing): ...`.
Types: `fix`, `feat`, `refactor`, `docs`, `test`, `chore`, `ci`. Short imperative subject; "why" in the body when not obvious.

## PR checklist (from the PR template)
- Targets `dev`.
- Scope limited to the described change — no unrelated refactors or whitespace churn.
- Ran the actual app (`docker compose up` or `uvicorn app:app`) and verified end-to-end; unit tests alone are not enough. If not run, say so explicitly in "How to Test".
- "How to Test" section must contain concrete reviewer-followable steps — never empty.
- Mention which checks were run; if a check couldn't be run, say so.

## Agent-specific rule (CONTRIBUTING.md)
LLM agents should open an issue describing the problem before opening a PR. Bulk agent-generated PRs that ignore visual style or contribution format get closed without review.

## Security
Never post secrets, API keys, private logs, personal documents, or public IPs in issues or PRs. See the odysseus-security skill for deployment/handling rules.
