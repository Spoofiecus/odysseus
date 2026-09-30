# Always-on rules for working in the Odysseus repo

Before making any change, check the relevant skills in `.clinerules/skills/`:

- **odysseus-standards** — branch model (PRs target `dev`), Conventional Commits, PR/issue discipline, scope limits. Applies to every change.
- **odysseus-testing** — pytest, taxonomy markers (`area_*`/`sub_*`), `tests/run_focus.py`, fast lane, syntax checks, behavioral-first test writing. Applies to any code/test change.
- **odysseus-code-style** — constants in `src/constants.py` (no hardcoded paths, ports, loopback URLs), no emoji in code, graceful degradation on unwritable paths. Applies to any backend change.
- **odysseus-ui-style** — visual language rules, CSS variable/class reuse, screenshot requirement. Applies to any change touching `static/`, CSS, HTML, SVG, or DOM-drawing JS.
- **odysseus-security** — no secrets in commits, pre-push scan commands, deployment posture. Applies to everything, especially config and auth code.

Non-negotiables (violations get PRs closed):
1. One focused change per PR/commit; target `dev`, never `main`.
2. Conventional Commit messages: `type(scope): summary`.
3. Run the smallest relevant checks (`pytest`, `py_compile`, `node --check`) and the actual app for end-user-visible changes; state what was run in the PR.
4. No hardcoded writable paths/ports/URLs — use `src/constants.py`.
5. No Unicode emoji in UI or code — inline SVG or plain text.
6. Match the existing visual style; reuse CSS variables and component classes.
7. Never commit secrets, `data/`, logs, databases, or tokens.
8. Every PR links an issue and has concrete "How to Test" steps.
