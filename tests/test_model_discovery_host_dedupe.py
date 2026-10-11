"""Issue #6221: discovery deduped on (port, models) with the host left out, so
two distinct machines serving the same inventory on the same port collapsed
into one result.
"""
from src.model_discovery import ModelDiscovery


def test_discovery_keeps_distinct_hosts_with_identical_inventory(monkeypatch):
    discovery = ModelDiscovery("127.0.0.1")
    monkeypatch.setattr(discovery, "_get_hosts", lambda: ["10.0.0.10", "10.0.0.11"])

    inventory = {
        ("10.0.0.10", 11434): ["llama3.2"],
        ("10.0.0.11", 11434): ["llama3.2"],  # a second, physically distinct box
    }

    def fake_check(host, port):
        models = inventory.get((host, port))
        if not models:
            return None
        return {
            "host": host,
            "port": port,
            "url": f"http://{host}:{port}/v1/chat/completions",
            "models": models,
            "models_display": models,
        }

    monkeypatch.setattr(discovery, "_check_port", fake_check)

    result = discovery.discover_models()
    found = {(item["host"], item["port"]) for item in result["items"]}
    assert ("10.0.0.10", 11434) in found
    assert ("10.0.0.11", 11434) in found
