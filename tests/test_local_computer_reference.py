"""Regression tests for the local-machine heuristic in ``src.agent_loop``.

Issue #6397: the third alternative of ``_LOCAL_COMPUTER_REFERENCE_RE`` used to
match ``on``/``from`` followed by *any* word, so ordinary prose (for example a
scheduled task that recalls "'waiting on' items") was classified as a
machine-targeted request. That discarded the caller's deliberately composed
toolset and replaced it with the file/shell Terminus toolset.
"""

from src.agent_loop import _looks_like_local_computer_request


def test_ordinary_prose_is_not_a_machine_reference():
    # The exact strings from the issue report must no longer match.
    assert not _looks_like_local_computer_request("recall 'waiting on' items")
    assert not _looks_like_local_computer_request("One line on anything tomorrow")
    assert not _looks_like_local_computer_request("remind me from time to time")
    assert not _looks_like_local_computer_request("working on the report")


def test_named_machine_still_matches():
    assert _looks_like_local_computer_request("run the build on dev-01")
    assert _looks_like_local_computer_request("pull the model from host.local")
    assert _looks_like_local_computer_request("check the cache on build_box")


def test_explicit_phrases_still_match():
    assert _looks_like_local_computer_request("read the file on this computer")
    assert _looks_like_local_computer_request("run it on my machine")
    assert _looks_like_local_computer_request("look at local files")


def test_blank_input_is_falsy():
    assert not _looks_like_local_computer_request("")
    assert not _looks_like_local_computer_request(None)
