# PR review audit — Spoofiecus / odysseus (10 open PRs)

Date: 2026-11-02. Audited against **upstream `dev` head `4126bea1`** (freshly fetched;
the workspace checkout had been on `3b6c1691`, so every verification below was
re-run on the current upstream tip).

## 1. Reviews and comments on all 10 PRs

Pulled with `gh api repos/odysseus-dev/odysseus/pulls/<n>/{reviews,comments}` and
`.../issues/<n>/comments`.

| PR | Reviews | Inline review comments | Discussion comments |
|----|---------|------------------------|---------------------|
| #6293 | **1 — CHANGES_REQUESTED (alteixeira20, 2026-11-02)** | 0 | 0 |
| #6294 | 0 | 0 | 1 (self, scope note) |
| #6295 | 0 | 0 | 1 (self, scope note) |
| #6301 | 0 | 0 | 0 |
| #6306 | 0 | 0 | 0 |
| #6310 | 0 | 0 | 1 (self, screenshot) |
| #6311 | 0 | 0 | 0 |
| #6317 | 0 | 0 | 0 |
| #6320 | 0 | 0 | 0 |
| #6321 | 0 | 0 | 0 |

There is exactly **one substantive objection**, and it is the one you
remembered: `alteixeira20`'s P2 finding on **#6293**, alleging the PR would
close #6235 without fixing the duplicate upload errors — i.e. that the added
test was a cosmetic guard over the real defect.

## 2. Is that finding true? (verified, not assumed)

**Yes.** Reproduced on fresh `dev` (`4126bea1`) before changing anything:

* `static/js/fileHandler.js` (`uploadPending`) toasted the server's reason on a
  non-OK response: `_showToast('Upload failed' + ...)` — the *attachment-strip*
  channel.
* `static/js/chat.js` independently called
  `uiModule.showError('Upload failed. Attachment kept so you can retry.')` when
  `uploadPending()` returned no ids — the *composer* channel.
  Two notifications, one rejection; the reason landed in the corner users do not
  read first.
* The PR's added assertion only matched the source pattern
  `e.detail || e.error`, so it would keep passing while both messages fired —
  exactly the "test pins source text, not behaviour" failure mode that
  `tests/TESTING_STANDARD.md` calls out.
* Secondary defect found while verifying: `validate_file_upload()` returns
  `detail = {error, message}` while `/api/upload` returns a string. The client
  did `'Upload failed: ' + detail`, so the structured shape would render as
  `[object Object]`.

## 3. Root-cause fix (implemented, tested, pushed)

Branch **`fix/chat-upload-single-error-6235`** (commit `5a25a9d6`, also on
`cline/q0nne79z`) — one owner per concern:

| Layer | Change |
|-------|--------|
| Ownership | `fileHandler.uploadPending()` now **records** the reason (`getLastUploadError()`) and announces nothing; the user-facing message is rendered once, in `chat.js` |
| Policy | new dependency-free `static/js/uploadFeedback.js`: `extractUploadErrorReason()` (string / `{error,message}` / `[{msg}]` / status fallback) and `formatUploadFailure()` (reason + "Attachment kept so you can retry.") |
| Server | `chat_upload_limit_message()` single-sourced in `src/upload_limits.py`, used by **both** enforcement points (`UploadHandler` on `/api/upload`, `validate_file_upload` on the chat send path), and names `ODYSSEUS_CHAT_UPLOAD_MAX_BYTES` so the "10 MB is configurable" gap is closed where the limit is actually known |
| Cache-bust | `fileHandler.js?v=` bumped in `chat.js`, `chatRenderer.js`, `gallery.js`, `app.js`, `sw.js`, `index.html` — otherwise the fix never reaches browsers holding the cached module |

Preserved behaviours (asserted): cancel still emits its single "Upload
cancelled" toast and suppresses the composer message; pending files survive a
failure for a retry; a later success clears the recorded reason. `uploadPending`
has exactly one caller (`chat.js`), so moving the announcement out of
`fileHandler` leaves no path silent.

### Tests (behavioural, not source-text)

`tests/helpers/upload_failure_harness.py` copies the shipped `fileHandler.js`
into a temp dir, rewrites only its two browser import specifiers to stubs, and
runs it under `node --input-type=module` with `fetch`, `FormData`, toast and DOM
stubbed — the assertions are about what the module does.

* `tests/test_upload_failure_notification.py` — 8 tests: oversize rejection →
  0 toasts + recorded reason + files kept; `{error,message}` unwrapped; non-JSON
  body → `HTTP 502`; network error recorded; success clears; cancel keeps one
  toast; message composition; chat.js renders one message from the reason.
* `tests/test_upload_error_surfaced.py` — converted from a source-text check to
  the same behavioural form (the #1346 guarantee: a failure is never swallowed).
* `tests/test_chat_upload_limit_config.py` — asserts the real `/api/upload`
  rejection carries both the reason and the env-var hint.

Result: `58 passed` across the upload-related files; `216 passed, 1 skipped`
across the whole `tests/test_upload_*` + attachments surface.

## 4. PR #6293 — the reviewed one, corrected

Branch **`fix/service-health-next-steps-6293`** (commit `2e90c4de`) is
`p5-degraded` with `tests/test_upload_error_surfaced.py` restored to `dev`
exactly, so the PR is diagnostics-only as the reviewer asked. The diff is now
`src/service_health.py` (+61/−6) plus its two test files (13 tests pass); the PR
body must switch `Fixes #6235` → `Refs #6235` (draft body in
`_pr_audit/pr6293_body.md`; the sandbox token cannot edit someone else's PR, so
the author needs to paste it).

## 5. The other nine PRs — independent findings

All ten branches' own test files pass on their own tips:

```
p1-smoke-gate        10 passed      p4-slice3-5979       6 passed
p2-intent             7 passed      p4-slice4-hfcache    5 passed
p4-cookbook           5 passed      p4_slice5-mlnx-reset 5 passed
p4-cookbook-5978     86 passed      p4-storage-diag     11 passed
p5-degraded          13 passed      p6-smoke-ui         11 passed
```

Three no longer merge cleanly into today's `dev` (they were branched from
`3b6c1691`, forty-plus commits back), so they need a rebase before review:

| Branch | Conflict |
|--------|----------|
| `p1-smoke-gate` (#6294) | `.github/workflows/ci.yml` |
| `p4-cookbook` (#6301) | `routes/cookbook_routes.py` |
| `p4-cookbook-5978` (#6306) | `routes/cookbook_helpers.py` |

Substantive findings:

1. **#6317 (`p4_slice5-mlnx-reset`) is a placebo fix — do not merge as written.**
   Its distinctive change is a runner block that unsets `MLX_ROOT` and
   `MLX_CACHE` "before each serve run". Neither variable is set or read anywhere
   in this repository (`grep -rn 'MLX_ROOT\|MLX_CACHE'` excluding `.git`,
   `.venv`, logs → 0 hits outside the PR's own diff), so the block cannot change
   behaviour. Its test file is the same HF-cache test as #6311 and never
   exercises the unset block at all.
2. **#6311 and #6317 duplicate each other.** Both add the identical HF-cache
   hunk to `routes/cookbook_routes.py`; #6311 also adds the macOS
   `~/Library/Caches/huggingface/hub` root and ships the behavioural test that
   executes the extracted runner lines. Keep #6311, drop #6317.
3. **#6306 and #6311 fix issue #5978 in two different files** (the model-scan
   script in `cookbook_helpers.py` vs the MLX serve resolver in
   `cookbook_routes.py`). Both are legitimate; the platform-default knowledge is
   duplicated, and the durable shape is one helper both scripts call.
4. **#6293's diagnostics change is sound but has two delivery paths**: per-item
   `next_step` from the `_check` closures in `email_health`/`providers_health`,
   and service-level `meta.next_step` from `_enrich_next_step`. Tests cover
   both; worth collapsing to one path in a follow-up.
5. **#6320 (`storage-diagnostics`)** is a large read-only addition (523 lines);
   its 11 tests pass and every probe degrades to `reference_scan_complete=False`
   rather than presenting a partial scan as authoritative — good practice, no
   action needed.
6. **#6294 → #6321 dependency**: #6321 builds on `tests/test_smoke_install.py`,
   which #6294 creates, so it must land after it (or be combined).

## 6. Execution environment note

Docker is **not available** in this sandbox (`docker: command not found`), so
"boot it in Docker and click through" was replaced with the closest equivalents
that actually execute the code:

* `python3 -m venv .venv` + `pip install -r requirements.txt` (the install CI
  performs), then real `pytest` runs of the affected suites plus the full suite
  (`-m "not slow"`).
* the frontend half runs under `node` against the shipped modules (harness
  above), never against a re-implementation.
* the server-side reason text is asserted through the real `UploadHandler`, so
  the string the browser renders is the string that was tested.

To reproduce the container path on a Docker host:
`cp .env.example .env && docker compose up -d --build`, attach a file larger
than 10 MB in chat, and confirm exactly one message:
`Upload failed: File size exceeds 10 MB limit (configurable via ODYSSEUS_CHAT_UPLOAD_MAX_BYTES). Attachment kept so you can retry.`

## 7. Warning hygiene

`pyproject.toml` now pins `asyncio_default_fixture_loop_scope = "function"`,
removing the `PytestDeprecationWarning` that fired on every run (behaviour
unchanged — the implicit default was already `function`). The one remaining
warning is pre-existing, from `core/database.py` (`declarative_base()` moved to
`sqlalchemy.orm`); it is unrelated to this fix and touches a core module
imported everywhere, so it is left as a documented follow-up rather than
smuggled into this PR.
