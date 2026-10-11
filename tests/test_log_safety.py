from core.log_safety import redact_url


def test_strips_userinfo():
    assert redact_url("https://user:pass@host.example/v1/models") == "https://host.example/v1/models"


def test_strips_query_and_fragment():
    assert redact_url("https://host.example/v1?api_key=secret#frag") == "https://host.example/v1"


def test_keeps_port_and_path():
    assert redact_url("http://host.example:8080/api/tags") == "http://host.example:8080/api/tags"


def test_ipv6_host_keeps_brackets():
    assert redact_url("https://user:pass@[2001:db8::1]:8443/v1") == "https://[2001:db8::1]:8443/v1"
    assert redact_url("https://[2001:db8::1]/v1") == "https://[2001:db8::1]/v1"


def test_no_credentials_passthrough():
    assert redact_url("https://host.example/v1/models") == "https://host.example/v1/models"


def test_empty_and_none():
    assert redact_url("") == ""
    assert redact_url(None) == ""


def test_garbage_does_not_raise():
    # urlparse is lenient; just assert no credential-looking userinfo survives.
    assert "@" not in redact_url("::::not a url::::")


def test_strips_userinfo_without_scheme():
    # Issue #6266: with no scheme urlparse reads the userinfo's username as the
    # scheme and the credential survived untouched.
    assert redact_url("admin:hunter2@10.0.0.5:11434/v1") == "10.0.0.5:11434/v1"


def test_schemeless_userinfo_drops_password_only():
    out = redact_url("user:secret@host.example:8080/api/tags")
    assert "secret" not in out
    assert "@" not in out
    assert out == "host.example:8080/api/tags"
