"""Issue #5766: a bare 'tool'/'auto' substring match demoted agent mode.

The old test `errText.includes('tool') || errText.includes('auto')` matched
ordinary failures ("tool execution timed out", "MCP server not connected") and
persisted Chat mode to localStorage. Only genuine tool-unsupported errors should
demote.
"""
import re
import subprocess
from pathlib import Path

SOURCE = Path("static/js/chat.js").read_text()


def _run(checks: str):
    const = re.search(r"const TOOL_UNSUPPORTED_RE = (.*?);\n", SOURCE)
    fn = re.search(r"function isToolUnsupportedError\(text\) \{\n(.*?)\n  \}", SOURCE, re.S)
    assert const, "TOOL_UNSUPPORTED_RE not found"
    assert fn, "isToolUnsupportedError not found"
    script = (
        "const TOOL_UNSUPPORTED_RE = " + const.group(1) + ";\n"
        "function isToolUnsupportedError(text) {" + fn.group(1) + "\n}\n"
        + checks
    )
    subprocess.run(["node", "-e", script], check=True)


def test_genuine_tool_unsupported_errors_demote():
    _run(r"""
function assert(c, m) { if (!c) throw new Error(m); }
assert(isToolUnsupportedError("registry.ollama.ai/library/llama:latest does not support tools"), "ollama");
assert(isToolUnsupportedError("This model does not support tools"), "plain");
assert(isToolUnsupportedError("tool calling is not supported"), "calling");
assert(isToolUnsupportedError("Invalid value for 'tools': not supported"), "invalid");
""")


def test_unrelated_errors_do_not_demote():
    _run(r"""
function assert(c, m) { if (!c) throw new Error(m); }
assert(!isToolUnsupportedError("Error 500: tool execution timed out"), "timeout");
assert(!isToolUnsupportedError("MCP server not connected: builtin_browser"), "mcp");
assert(!isToolUnsupportedError("automatic retry scheduled"), "auto");
assert(!isToolUnsupportedError(""), "empty");
assert(!isToolUnsupportedError(null), "null");
""")


def test_bare_substring_test_is_gone():
    assert "errText.includes('tool') || errText.includes('auto')" not in SOURCE
    assert "err.message.includes('tool') || err.message.includes('auto')" not in SOURCE
