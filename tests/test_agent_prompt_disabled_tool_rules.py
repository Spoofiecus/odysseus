"""Issue #6285: rules for disabled tools must not stay in the system prompt.

``_assemble_prompt`` filtered the tool sections through ``included = tool_names
- disabled`` but appended the static rule blocks unchanged, so a disabled tool
lost its schema yet kept its behavioural rule. The model then resolved the
contradiction by making no tool call at all.
"""
from src.agent_loop import _assemble_prompt


def test_disabled_tool_rule_is_removed():
    prompt = _assemble_prompt({"manage_memory", "manage_notes"}, {"manage_memory"})
    assert "`manage_memory`" not in prompt


def test_enabled_tool_rule_is_kept():
    prompt = _assemble_prompt({"manage_memory", "manage_notes"}, set())
    assert "`manage_memory`" in prompt


def test_compact_prompt_drops_disabled_tool_rule():
    prompt = _assemble_prompt(
        {"manage_memory", "manage_notes"}, {"manage_memory"}, compact=True
    )
    assert "`manage_memory`" not in prompt
