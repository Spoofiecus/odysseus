"""Issue #6219: the service worker was registered at /static/ scope, so it never
controlled the app root and the offline/PWA shell was inert.

A worker's default scope is the directory it is served from. Serving and
registering it at /sw.js gives it a root scope, matching manifest.json's
"scope": "/".
"""
import os
import tempfile
from pathlib import Path

os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="odysseus-sw-"))

from fastapi.testclient import TestClient  # noqa: E402

import app as app_module  # noqa: E402

INDEX = Path("static/index.html").read_text()


def test_index_registers_service_worker_at_root():
    assert "navigator.serviceWorker.register('/sw.js')" in INDEX
    assert "register('/static/sw.js')" not in INDEX


def test_service_worker_served_from_root_with_root_scope():
    client = TestClient(app_module.app, raise_server_exceptions=False)
    r = client.get("/sw.js")
    assert r.status_code == 200, r.text
    assert r.headers.get("service-worker-allowed") == "/"
    assert "javascript" in r.headers.get("content-type", "")
    assert "CACHE_NAME" in r.text
