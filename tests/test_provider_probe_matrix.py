"""Provider-probe contract matrix guard (Phase 5).

ROADMAP asks for a provider setup/probing audit for Anthropic, Gemini, Groq,
xAI, OpenRouter, OpenAI, and DeepSeek. This test pins the contract so a new
provider or a refactor cannot silently drop one of the seven from either the
setup surface or the model-endpoint probe path without a failing test.

Follows the repo's source-level regression pattern (see
tests/test_upload_error_surfaced.py and tests/test_chat_route_tool_policy.py).
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SLASH_COMMANDS = REPO / "static/js/slashCommands.js"
MODEL_ROUTES = REPO / "routes/model_routes.py"

# The seven providers named in ROADMAP.md's "Provider setup/probing audit".
ROADMAP_PROVIDERS = {
    "anthropic", "gemini", "groq", "xai", "openrouter", "openai", "deepseek",
}


def test_setup_surface_covers_all_roadmap_providers():
    """/setup UI must recognize every ROADMAP provider by its slug."""
    text = SLASH_COMMANDS.read_text(encoding="utf-8")
    m = re.search(r"SETUP_PROVIDER_NAMES\s*=\s*\[([^\]]*)\]", text)
    assert m, "SETUP_PROVIDER_NAMES array not found in slashCommands.js"
    slugs = {s.strip("'\", ") for s in m.group(1).split(",") if s.strip()}
    missing = ROADMAP_PROVIDERS - slugs
    assert not missing, f"providers missing from /setup surface: {sorted(missing)}"


def test_probe_route_special_cases_anthropic_and_google():
    """_probe_endpoint must keep its two non-OpenAI-format branches."""
    text = MODEL_ROUTES.read_text(encoding="utf-8")
    assert "_is_google_api_base(base)" in text
    assert 'provider == "anthropic"' in text
    assert "ANTHROPIC_MODELS" in text


def test_probe_route_handles_openai_compatible_matrix():
    """OpenAI/Groq/xAI/OpenRouter/DeepSeek speak OpenAI-format /models.

    The generic probe path must keep OpenAI-format parsing plus the Ollama
    fallback; dropping either would break discovery for those providers.
    """
    text = MODEL_ROUTES.read_text(encoding="utf-8")
    assert "_openai_model_ids(data)" in text
    assert "_ollama_model_names(data)" in text


def test_provider_curated_lookup_exists():
    """Curated model lists are keyed by provider slug (incl. all seven)."""
    text = MODEL_ROUTES.read_text(encoding="utf-8")
    assert "_PROVIDER_CURATED" in text
    assert "_match_provider_curated" in text