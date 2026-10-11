"""Issue #6171: require_admin trusted the internal-tool header without the
origin check AuthMiddleware applies.

AuthMiddleware honours X-Odysseus-Internal-Token only for a direct loopback
connection with no proxy/tunnel forwarding headers. require_admin accepted the
header from any origin, so a request the middleware would not treat as
in-process could still satisfy the admin gate.
"""
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from core.middleware import INTERNAL_TOOL_HEADER, INTERNAL_TOOL_TOKEN, require_admin


def _auth_manager():
    return SimpleNamespace(is_configured=True, is_admin=lambda user: False, users={})


def _request(host, headers):
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/api/x",
        "raw_path": b"/api/x",
        "query_string": b"",
        "root_path": "",
        "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
        "client": (host, 1234),
        "server": ("test", 80),
        "app": SimpleNamespace(state=SimpleNamespace(auth_manager=_auth_manager())),
    }
    return Request(scope)


@pytest.fixture(autouse=True)
def _auth_enabled(monkeypatch):
    monkeypatch.setenv("AUTH_ENABLED", "true")


def test_direct_loopback_with_token_is_allowed():
    require_admin(_request("127.0.0.1", {INTERNAL_TOOL_HEADER: INTERNAL_TOOL_TOKEN}))


def test_forwarded_loopback_with_token_is_rejected():
    with pytest.raises(HTTPException) as ei:
        require_admin(_request("127.0.0.1", {
            INTERNAL_TOOL_HEADER: INTERNAL_TOOL_TOKEN,
            "x-forwarded-for": "203.0.113.7",
        }))
    assert ei.value.status_code == 403


def test_non_loopback_with_token_is_rejected():
    with pytest.raises(HTTPException) as ei:
        require_admin(_request("203.0.113.7", {INTERNAL_TOOL_HEADER: INTERNAL_TOOL_TOKEN}))
    assert ei.value.status_code == 403


def test_wrong_token_is_rejected():
    with pytest.raises(HTTPException) as ei:
        require_admin(_request("127.0.0.1", {INTERNAL_TOOL_HEADER: "not-the-token"}))
    assert ei.value.status_code == 403
