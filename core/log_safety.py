"""Helpers for keeping sensitive data out of logs.

Endpoint URLs configured by admins can embed credentials in the userinfo
(``https://user:pass@host``) or query string (``?api_key=...``). Logging them
raw leaks those secrets, so route/diagnostic logs run URLs through
``redact_url`` first. Reconstructing the URL without userinfo/query/fragment
also doubles as a sanitizer barrier for CodeQL's clear-text-logging query.
"""

from urllib.parse import urlparse, urlunparse


def redact_url(url: str) -> str:
    """Return a URL safe for logs by removing userinfo and query/fragment.

    Keeps scheme, host, port and path so logs stay useful for debugging.
    """
    try:
        raw = url or ""
        parsed = urlparse(raw)
        schemeless = False
        if not parsed.netloc and "@" in raw:
            # No scheme (or an opaque one like "admin:"). urlparse then reads the
            # userinfo's "admin" as the scheme and leaves "hunter2@host:port/path"
            # in the path, so urlunparse would reassemble the credential intact.
            # Re-parse as an authority so the userinfo is dropped.
            parsed = urlparse("//" + raw)
            schemeless = True
        host = parsed.hostname or ""
        if ":" in host:  # IPv6 literal — re-bracket so host:port stays unambiguous
            host = f"[{host}]"
        if parsed.port:
            host = f"{host}:{parsed.port}"
        if schemeless:
            return f"{host}{parsed.path}"
        return urlunparse((parsed.scheme, host, parsed.path, "", "", ""))
    except Exception:
        return "<endpoint>"
