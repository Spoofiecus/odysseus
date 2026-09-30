"""SSRF hardening for user-supplied model-endpoint URLs.

``POST /api/model-endpoints`` and ``POST /api/model-endpoints/test`` accept a
caller-supplied ``base_url`` and then probe it server-side via
``_probe_endpoint``. With no validation this is a server-side request forgery
primitive: a caller can point the probe at ``http://169.254.169.254/`` (cloud
instance metadata) or at internal services the server can reach but the caller
cannot.

Every other URL-taking route (embeddings, contacts, gallery, notes, webhooks)
already validates through ``check_outbound_url`` from ``src/url_safety.py``;
these two routes were the only exceptions. These tests pin the guard in place
through the real routes (TestClient), with the probe seams stubbed so no
outbound request is ever made, and the URL-safety resolver stubbed (same
pattern as ``tests/test_url_safety.py``) so no real DNS is involved and the
loopback cases do not depend on how ``localhost`` resolves on the host.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import routes.model_routes as mr
from core.database import Base


def _stub_resolver(mapping):
    """Resolver stub: only the mapped hosts resolve; anything else raises."""
    def resolve(host):
        if host in mapping:
            return mapping[host]
        raise OSError(f"unresolvable: {host}")
    return resolve


LOCALHOST_V4 = _stub_resolver({"localhost": ["127.0.0.1"]})


@pytest.fixture
def client(monkeypatch):
    """TestClient for the model routes with every outbound seam neutralized."""
    # StaticPool: TestClient runs the route on a portal thread; without a
    # shared connection an in-memory sqlite would hand that thread a fresh,
    # empty database and every query would fail with "no such table".
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(bind=engine, autoflush=False)

    monkeypatch.setattr(mr, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(mr, "require_admin", lambda request: None)
    # Outbound probes must never run: the guard under test fires before them,
    # and the accepted-loopback cases would otherwise hit the network.
    monkeypatch.setattr(mr, "_probe_endpoint", lambda *a, **k: ["stubbed-model"])
    monkeypatch.setattr(mr, "_ping_endpoint", lambda *a, **k: {"reachable": True, "error": None})
    # Settings persistence must not touch the real settings file.
    monkeypatch.setattr(mr, "_load_settings", lambda: {})
    monkeypatch.setattr(mr, "_save_settings", lambda settings: None)
    # Keep the URL pipeline hermetic: no Tailscale/DNS fallback, no Docker-host
    # loopback rewriting (both are real functions in src.endpoint_resolver /
    # model_routes and may open sockets or subprocesses).
    monkeypatch.setattr(mr, "_rewrite_loopback_for_docker", lambda url, **k: url)
    import src.endpoint_resolver as er
    monkeypatch.setattr(er, "resolve_url", lambda url: url)

    app = FastAPI()
    app.include_router(mr.setup_model_routes(model_discovery=None))
    return TestClient(app, raise_server_exceptions=False)


# ── POST /api/model-endpoints/test ──


def test_test_route_cloud_metadata_blocked(client):
    """The cloud metadata IP must be rejected before any probe runs."""
    resp = client.post(
        "/api/model-endpoints/test",
        data={"base_url": "http://169.254.169.254/latest/meta-data/"},
    )
    assert resp.status_code == 400
    assert "Rejected" in resp.json()["detail"]


def test_test_route_non_http_scheme_blocked(client):
    """Non-HTTP(S) schemes (file://) must be rejected."""
    resp = client.post(
        "/api/model-endpoints/test",
        data={"base_url": "file:///etc/passwd"},
    )
    assert resp.status_code == 400
    assert "Rejected" in resp.json()["detail"]


def test_test_route_loopback_accepted_by_default(client, monkeypatch):
    """Local-first: loopback is accepted when block_private is unset."""
    import src.url_safety as url_safety
    monkeypatch.setattr(url_safety, "_default_resolver", LOCALHOST_V4)
    resp = client.post(
        "/api/model-endpoints/test",
        data={"base_url": "http://localhost:11434/v1"},
    )
    assert resp.status_code == 200
    # The guard passed; the stubbed probe answered.
    assert resp.json()["models"] == ["stubbed-model"]


def test_test_route_loopback_rejected_in_strict_mode(client, monkeypatch):
    """Strict mode: block_private=True rejects loopback targets."""
    monkeypatch.setenv("MODELENDPOINT_BLOCK_PRIVATE_IPS", "true")
    resp = client.post(
        "/api/model-endpoints/test",
        data={"base_url": "http://127.0.0.1:11434/v1"},
    )
    assert resp.status_code == 400
    assert "Rejected" in resp.json()["detail"]


# ── POST /api/model-endpoints (create) ──


def test_create_route_cloud_metadata_blocked(client):
    """The create route must reject the cloud metadata IP."""
    resp = client.post(
        "/api/model-endpoints",
        data={"base_url": "http://169.254.169.254/latest/meta-data/"},
    )
    assert resp.status_code == 400
    assert "Rejected" in resp.json()["detail"]


def test_create_route_non_http_scheme_blocked(client):
    """The create route must reject non-HTTP(S) schemes."""
    resp = client.post(
        "/api/model-endpoints",
        data={"base_url": "file:///etc/passwd"},
    )
    assert resp.status_code == 400
    assert "Rejected" in resp.json()["detail"]


def test_create_route_loopback_rejected_in_strict_mode(client, monkeypatch):
    """Strict mode: the create route must reject loopback targets."""
    monkeypatch.setenv("MODELENDPOINT_BLOCK_PRIVATE_IPS", "true")
    resp = client.post(
        "/api/model-endpoints",
        data={"base_url": "http://127.0.0.1:11434/v1"},
    )
    assert resp.status_code == 400
    assert "Rejected" in resp.json()["detail"]


def test_create_route_loopback_accepted_by_default(client, monkeypatch):
    """Local-first: a loopback endpoint is created when block_private is unset."""
    import src.url_safety as url_safety
    monkeypatch.setattr(url_safety, "_default_resolver", LOCALHOST_V4)
    resp = client.post(
        "/api/model-endpoints",
        data={"base_url": "http://localhost:11434/v1"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["base_url"] == "http://localhost:11434/v1"
    assert "stubbed-model" in body["models"]
    assert body["online"] is True

