"""Issue #6315: model endpoint routes accepted arbitrary SSRF URLs.

POST /api/model-endpoints and /api/model-endpoints/test probed any user-supplied
URL with no scheme/host validation. They now share the check_outbound_url()
guard the other URL-accepting routes use.
"""
import pytest
from fastapi import HTTPException

from routes.model_routes import _validate_endpoint_url_or_400


def test_cloud_metadata_blocked():
    with pytest.raises(HTTPException) as ei:
        _validate_endpoint_url_or_400("http://169.254.169.254/latest/meta-data/")
    assert ei.value.status_code == 400
    assert "Rejected endpoint URL" in ei.value.detail


def test_non_http_scheme_blocked():
    with pytest.raises(HTTPException):
        _validate_endpoint_url_or_400("file:///etc/passwd")


def test_loopback_allowed_by_default():
    # Local-first: a manually added Ollama endpoint on loopback must still work.
    _validate_endpoint_url_or_400("http://127.0.0.1:11434/v1")


def test_strict_mode_blocks_loopback(monkeypatch):
    monkeypatch.setenv("MODEL_ENDPOINT_BLOCK_PRIVATE_IPS", "true")
    with pytest.raises(HTTPException) as ei:
        _validate_endpoint_url_or_400("http://127.0.0.1:11434/v1")
    assert ei.value.status_code == 400
