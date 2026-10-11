"""Issue #5203: the `/rag` toggle handler was defined but never registered.

`_cmdToggleRag` supported `on`/`off` and a bare quick-toggle, but it was not
reachable: it was absent from the command registry and `rag: 'rag-toggle'` was
missing from the toggle maps, so `/rag on|off` silently no-op'd.
"""
import re
from pathlib import Path

SOURCE = Path("static/js/slashCommands.js").read_text()


def test_toggle_maps_include_rag():
    maps = re.findall(r"const toggleMap = \{([^}]*)\};", SOURCE)
    assert len(maps) >= 2, "expected the _quickToggle/_applyToggle toggle maps"
    assert all("rag: 'rag-toggle'" in m for m in maps), maps


def test_rag_command_registers_on_off_subcommands():
    match = re.search(r"\n  rag: \{[\s\S]*?\n  \},\n", SOURCE)
    assert match, "rag command definition not found"
    block = match.group(0)
    assert "handler: _cmdRagOn" in block
    assert "handler: _cmdRagOff" in block


def test_cmd_toggle_rag_is_reachable():
    assert "return _cmdToggleRag(['on'], ctx)" in SOURCE
    assert "return _cmdToggleRag(['off'], ctx)" in SOURCE
