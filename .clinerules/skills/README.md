# Agent Skills for the Odysseus Workspace

Project-level rules extracted from CONTRIBUTING.md, tests/TESTING_STANDARD.md,
tests/README.md, SECURITY.md, .github/pull_request_template.md, and
.github/workflows/ci.yml so the agent always follows the repo's standards.

- `odysseus-rules.md` (root .clinerules file) — always-loaded summary of the
  non-negotiables; points to the skills below.
- `skills/odysseus-standards/SKILL.md` — branch model, PR discipline, Conventional Commits, scope limits.
- `skills/odysseus-testing/SKILL.md` — how to run tests, taxonomy markers, run_focus.py, fast lane, test-writing rules.
- `skills/odysseus-code-style/SKILL.md` — constants in src/constants.py, no hardcoded paths/ports/URLs, graceful degradation, no emoji in code.
- `skills/odysseus-ui-style/SKILL.md` — visual language rules, CSS variables/class reuse, screenshot requirement for rendering changes.
- `skills/odysseus-security/SKILL.md` — secrets handling, pre-push scans, deployment posture.

Keep these in sync when CONTRIBUTING.md, TESTING_STANDARD.md, or the PR
template change.
