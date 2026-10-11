"""Issue #6326: the manage_endpoints agent tool bypassed SSRF validation.

POST /api/model-endpoints validates user-supplied URLs, but the agent tool is
prompt-injection reachable and wrote any base_url straight to the ModelEndpoint
table. Apply the same check_outbound_url() guard.
"""
import asyncio
import json

import pytest

from src.agent_tools.admin_tools import do_manage_endpoints


def _add(base_url, name="Ollama Backup", **extra):
    payload = {"action": "add", "name": name, "base_url": base_url, **extra}
    return asyncio.run(do_manage_endpoints(json.dumps(payload)))


def test_cloud_metadata_blocked():
    r = _add("http://169.254.169.254/latest/meta-data/")
    assert r.get("exit_code") == 1
    assert "Rejected endpoint URL" in r.get("error", "")
    assert "169.254.169.254" in r.get("error", "")


def test_non_http_scheme_blocked():
    r = _add("gopher://example.com/")
    assert r.get("exit_code") == 1
    assert "Rejected endpoint URL" in r.get("error", "")


def test_empty_url_rejected():
    r = _add("")
    assert r.get("exit_code") == 1
    assert "base_url is required" in r.get("error", "")


def test_loopback_accepted_by_default():
    r = _add("http://127.0.0.1:11434/v1")
    assert r.get("exit_code") == 0, r


def test_strict_mode_blocks_private(monkeypatch):
    monkeypatch.setenv("MODEL_ENDPOINT_BLOCK_PRIVATE_IPS", "true")
    r = _add("http://127.0.0.1:11434/v1")
    assert r.get("exit_code") == 1
    assert "Rejected endpoint URL" in r.get("error", "")


def test_error_does_not_leak_api_key():
    r = _add("http://169.254.169.254/v1", api_key="super-secret-token")
    assert "super-secret-token" not in json.dumps(r)
