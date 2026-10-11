"""Issue #6224: regenerating an earlier message silently destroyed later history.

Both regenerate entry points (``regenerateFrom`` and
``resendUserMessage(..., {replaceFromHere: true})``) call
``POST /api/session/{id}/truncate``, a permanent server-side delete of every
message after the clicked point. They must confirm first when later messages
exist.
"""
from pathlib import Path

SOURCE = Path("static/js/chat.js").read_text()


def test_confirmation_copy_present():
    assert "Regenerate from here?" in SOURCE
    assert "permanently deletes the" in SOURCE
    assert "cannot be undone" in SOURCE


def test_both_regenerate_paths_confirm():
    # regenerateFrom + resendUserMessage(replaceFromHere) each truncate.
    assert SOURCE.count("permanently deletes the ${_laterCount}") == 2


def test_confirmation_is_conditional_on_later_messages():
    assert SOURCE.count("const _laterCount = allMsgs.length - 1 -") == 2
    assert SOURCE.count("if (_laterCount > 0") == 2
