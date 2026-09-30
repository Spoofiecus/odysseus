# Top 50 Issues — Odysseus (odysseus-dev/odysseus)

Ranked from the live issue tracker on 2026-09-30. **1,079 open issues (356 labeled `bug`)**, 1,122 closed.

**Method:** ranked by a blend of (a) engagement — issue comments and reactions, the "most requested" signal; (b) severity — security, data loss, and authorization failures outrank functional bugs; (c) cluster size — related/duplicate issues counted as one entry. Tiers 1–2 are the critical/biggest-impact fixes; tiers 3–5 complete the top 50.

---

## Tier 1 — Critical: security, authorization & data loss (fix regardless of comment count)

| # | Issue | Why it's critical |
|---|-------|-------------------|
| 1 | #2257 | **Stored XSS** — deep-research report renders unsanitized markdown HTML |
| 2 | #6315 | **SSRF** via model endpoint URL — no scheme/host validation on `POST /model-endpoints` |
| 3 | #6352 | **SSRF** — email account routes connect to user-supplied IMAP/SMTP hosts with no guard |
| 4 | #6267 | Generated image **ownership check bypassed** on database failure (authz) |
| 5 | #6350 | Read-only Cookbook agent tools **bypass the non-admin tool policy** (authz) |
| 6 | #6414 | `write_file` **truncates an existing file to 0 bytes** on empty body — data loss |
| 7 | #6324 | `write_file` reports success but produces **0-byte files on NFS** volumes — data loss |
| 8 | #1940 | Silent lost-update race in `memory.json` can **permanently erase user memories** |
| 9 | #6002 | Concurrent preference writes silently **lose independent updates** |
| 10 | #2654 | Session-history compact/run race (conversation content loss); serialize mutations |
| 11 | #6363 | Library navigation can **delete documents** or show them as lost |

## Tier 2 — Most-reported broken core features (highest engagement)

| # | Issue | Engagement | Notes |
|---|-------|------------|-------|
| 12 | #831 — Cookbook Docker NVIDIA: llama.cpp sees GPU but falls back to CPU | 40 comments | Biggest single issue in the repo; cluster: #2659 (docker GPU passthrough), #5606 (missing nvcc in Docker image), #2377, #2380, #2239 (CUDA build/runtime) |
| 13 | #1789 — MCP server is not callable in chat or agent | 21 comments | Core agent feature dead for many users |
| 14 | #2008 — Any download inside the app crashes | 20 comments | Blocks dependencies AND model downloads |
| 15 | #3594 — Cookbook shows models but no obvious way to serve/open them | 19 comments | First-run dead end |
| 16 | #3041 — Agent Mode is broken / barely performs as an agent | 18 comments | Core product function |
| 17 | #337 — Email/calendar not working properly | 16 comments | Core feature |
| 18 | #3029 — Error logging in; no temporary username for first login | 14 comments | Blocks new installs entirely |
| 19 | #344 — Unable to do deep research | 12 comments | Headline feature broken |
| 20 | #465 — Crash on serving model | 11 comments | Cookbook stability |
| 21 | #4234 — Can't use Ollama | 10 comments | Most common local backend |
| 22 | #760 — Web search not working / unexpected gemini calls on local models | 9 comments | Search + privacy concern |
| 23 | #4206 — Agent doesn't know its own tools | 9 comments, 7 reactions | Tool discovery failure |
| 24 | #488 — Cannot get Odysseus to recognize AMD GPU | 8 comments | AMD cluster: #437 (ROCm), #504 (vLLM false-compat), #1504 (ROCm support) |
| 25 | #280 — Only chat works; agent does not | 7 comments | Same family as #3041 |
| 26 | #3180 — Ollama connection problems | 7 comments | With #2147 (localhost in Docker) |
| 27 | #3934 — Tool-RAG low-signal gate hides most tools | 7 comments | Directly caps agent capability |
| 28 | #4510 — Can't click Cookbook button | 7 comments | With #4737 — UI blocks entry to a whole panel |
| 29 | #4663 — Agent mode + shell access fails to create files | 7 comments | With #4127, #4966 — local-model file tools dead |
| 30 | #4541 — KV cache invalidation on every message (llama.cpp) | 6 comments | Major perf regression on local backends |

## Tier 3 — High impact: agent/tooling breakage clusters (biggest blast radius)

| # | Issue | Engagement | Notes |
|---|-------|------------|-------|
| 31 | #5466 — `tools_sent=0` on Ollama endpoints; MCP tools never sent to model | 6 comments | Largest cluster in the repo: #5048, #5602, #4769, #5015, #4127, #4653, #5192 (`supports_tools` NULL + no UI control). Local-model tool calling is silently broken for many setups |
| 32 | #3766 — Non-English queries strip all tools (only 3 always-available sent) | 2 comments | i18n agent-breakage family: #3668 (English-only intent supervisor stalls non-English tasks) |
| 33 | #6412 — Qwen3-Coder `<function=NAME>` markup not parsed → text-mode tool calls never execute | — | New; breaks text-mode tool calling for a major model family (see also #6423, #6012, #6013) |
| 34 | #4939 — Models fake tool calls instead of invoking them; timeline renders wrong | 4 comments, 5 reactions | Trust/UX of the whole tool timeline |
| 35 | #3604 — Ordinary Markdown code fences executed as tool calls (accidental commands) | 3 comments | Safety: unintended command execution; recurrence of a fixed bug |
| 36 | #5294 — Scheduled tasks stuck "waiting for Odysseus to be idle" while any tab is open | 3 comments | With #5536 (heartbeats abort background tasks) — breaks the scheduled-agent feature |
| 37 | #6392 — SearXNG hard-pins `language=en` → wrong results for non-English queries; Deep Research reports become random pages | — | Silently corrupts Deep Research quality |
| 38 | #5193 — Static context-window table overrides endpoint's real context → silent truncation in long sessions | 5 comments | With #3535 (LM Studio variant) — long-session corruption |
| 39 | #3968-family — Fresh install breakage: #6052/#6066 (SearXNG `KeyError: default_doi_resolver` on current tag), #6067 | — | Blocks all new Docker users; ship-blocking |
| 40 | #1967 — Admin "wipe memory" doesn't clear the vector index | 2 comments | Privacy: user data not actually removed |

## Tier 4 — Most-requested bugs by community reaction

| # | Issue | Engagement | Notes |
|---|-------|------------|-------|
| 41 | #1024 — Emojis are not rendering | 13 reactions | Highest-reaction bug in the tracker (rendering, chat/email) |
| 42 | #316 — Cookbook shows "No GPU" with no guidance on enabling GPU | 6 comments | Onboarding wall for non-technical users |
| 43 | #3130 — Attachments cannot be read | 5 comments | Chat attachments unusable for affected users |
| 44 | #6424 — Older email returns blank stuck message instead of an error | — | New; silent failure in a core panel |
| 45 | #4881 — Re-probe ignores user-disabled models; force-loads them, clears disabled state | 4 comments | Settings not respected; with #2664 (mail tasks "No model configured") |
| 46 | #4843 — Probing OpenRouter floods hundreds of /chat/completions requests | 3 comments | Cost + rate-limit hazard on API keys |
| 47 | #5743 — App stuck at 100% CPU due to AnyIO cancellation loop storm | — | Resource exhaustion; server-hostile |
| 48 | #5814 — API model providers gray out in picker ~5s after successful fetch | 3 comments | Appears offline; misleads users (with #3920, #5890-family) |
| 49 | #2959 — Skills are marked "UNTRUSTED SOURCE DATA" | 3 comments | Breaks the skills feature's credibility |
| 50 | #6384 — Round-limit Continue state lost for background sessions and after reload | — | New; agent run resumption broken |

---

## Bonus — Top most-requested features (non-bug, by reactions/comments)

1. **#605** — Architecture & Codebase Structure v3 proposal (51 reactions, 102 comments — most-discussed issue in the repo)
2. **#593** — CODEOWNERS proposal (32 reactions)
3. **#71** — Modernize project setup: pyproject.toml + uv (31 reactions)
4. **#806** — SSO via OIDC (16 reactions); follow-ups: #2446/#5341 LDAP/FreeIPA
5. **#42** — Intel GPU detection (17 reactions); AMD cluster: #488, #1504, #504
6. **#2079** — VS Code extension powered by Odysseus (12 reactions)
7. **#58** — Multilingual/i18n UI support (11 reactions)
8. **#220** — Multiple workspaces (work/personal isolation) (8 reactions)
9. **#3345** — Proton Mail Bridge support (8 comments)
10. **#3024** — Import ChatGPT data dumps (7 reactions); **#5908** Native ComfyUI backend (10 reactions)
11. **#2523** — Test hardening & scalability tracker (22 comments); **#3629**/#2917 tool-registry refactor trackers

## Patterns worth acting on

- **Local-model tool calling is the biggest broken surface**: #5466, #5048, #5602, #4769, #5015, #4127, #4653, #5192, #6412, #6423 all describe the same family — schemas never sent / text-mode calls unparsed.
- **GPU serving on Docker/AMD/Windows is the most-commented family**: #831, #2659, #5606, #2377, #2380, #2239, #488, #437, #504.
- **Security gaps cluster around user-supplied URLs**: #6315, #6352 (SSRF), #2257 (XSS) — one validation pass could close all three.
- **Silent data loss in concurrent writes**: #1940, #6002, #2654, #6414, #6324 — one audit of write paths (locking + atomic writes + empty-body guards) closes the tier-1 data-loss class.
- **Fresh-install breakage** (#6052, #6066, #3029, #3968) costs every new user; pinning + a smoke-test gate (already tracked in #3968/#2523) prevents recurrence.

*Data: `gh api search/issues` over `odysseus-dev/odysseus`, ranked 2026-09-30. Code-comment scan (TODO/FIXME/HACK) found the tree clean — the issue tracker is the real backlog source.*

