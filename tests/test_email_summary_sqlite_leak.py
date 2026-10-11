"""Issue #5053: the auto-summary SQLite write leaked one connection per failure.

`_auto_summarize_pass_single` opened a connection, then `execute()`/`commit()`,
then `close()`. If execute/commit raised (disk full, "database is locked",
schema drift) control jumped to the surrounding except and `close()` never ran.
The write now lives in `_persist_email_summary`, whose try/finally always closes.
"""
import os
import sys
import tempfile
import sqlite3
from pathlib import Path

_TMP_DATA = Path(tempfile.mkdtemp(prefix="odysseus-email-summary-leak-"))
os.environ.setdefault("DATA_DIR", str(_TMP_DATA))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TMP_DATA / 'app.db'}")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))




def test_persist_email_summary_closes_connection_on_execute_failure(monkeypatch):
    import routes.email_pollers as email_pollers

    closed = {"n": 0}

    class _Conn:
        def execute(self, *a, **k):
            raise RuntimeError("database is locked")

        def commit(self):  # pragma: no cover - must not be reached
            raise AssertionError("commit must not run after a failed execute")

        def close(self):
            closed["n"] += 1

    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: _Conn())

    try:
        email_pollers._persist_email_summary(
            message_id="m", owner="o", uid="1", folder="INBOX",
            subject="s", sender="x", summary="sum", model="m",
        )
    except RuntimeError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected the execute failure to propagate")

    assert closed["n"] == 1, "connection must be closed even when the write fails"


def test_persist_email_summary_commits_and_closes_on_success(monkeypatch):
    import routes.email_pollers as email_pollers

    calls = {"executed": 0, "committed": 0, "closed": 0}

    class _Conn:
        def execute(self, *a, **k):
            calls["executed"] += 1

        def commit(self):
            calls["committed"] += 1

        def close(self):
            calls["closed"] += 1

    monkeypatch.setattr(sqlite3, "connect", lambda *a, **k: _Conn())

    email_pollers._persist_email_summary(
        message_id="m", owner="o", uid="1", folder="INBOX",
        subject="s", sender="x", summary="sum", model="m",
    )

    assert calls == {"executed": 1, "committed": 1, "closed": 1}
