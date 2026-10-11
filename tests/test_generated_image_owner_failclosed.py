"""Issue #6267: the generated-image route must fail closed.

If the ownership lookup raised (DB down / corrupt / schema drift) the old code
logged a warning and fell through to serve the bytes with no ownership check.
It must now return 503 instead.
"""
import asyncio
import os
import tempfile

os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="odysseus-genimg-"))

import pytest  # noqa: E402
from fastapi import HTTPException  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402

import app as app_module  # noqa: E402
import core.database as cdb  # noqa: E402
from src import auth_helpers  # noqa: E402

_FILENAME = "deadbeef1234.png"


def _call(monkeypatch, tmp_path, user):
    img = tmp_path / _FILENAME
    img.write_bytes(b"image bytes")
    monkeypatch.setattr(app_module, "resolve_generated_image_path", lambda filename: img)
    monkeypatch.setattr(auth_helpers, "get_current_user", lambda request: user)
    return asyncio.run(app_module.serve_generated_image(_FILENAME, None))


def test_ownership_db_failure_returns_503(monkeypatch, tmp_path):
    def _boom(*args, **kwargs):
        raise RuntimeError("database is down")

    monkeypatch.setattr(cdb, "SessionLocal", _boom)

    with pytest.raises(HTTPException) as ei:
        _call(monkeypatch, tmp_path, user="bob")
    assert ei.value.status_code == 503


def test_owner_mismatch_returns_404(monkeypatch, tmp_path):
    class _Row:
        owner = "alice"

    class _Query:
        def filter(self, *a, **k):
            return self

        def first(self):
            return _Row()

    class _DB:
        def query(self, *a, **k):
            return _Query()

        def close(self):
            pass

    monkeypatch.setattr(cdb, "SessionLocal", lambda: _DB())

    with pytest.raises(HTTPException) as ei:
        _call(monkeypatch, tmp_path, user="bob")
    assert ei.value.status_code == 404


def test_unauthenticated_serves_file(monkeypatch, tmp_path):
    # No user to scope to -> ownership check is skipped and the file is served.
    result = _call(monkeypatch, tmp_path, user=None)
    assert isinstance(result, FileResponse)
