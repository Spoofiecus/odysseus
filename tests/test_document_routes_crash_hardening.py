"""Issue #5056: document routes crashed on empty PDF content / malformed tidy.

``content.splitlines()[0]`` raised IndexError on empty content, and the tidy
verdict parse called ``json.loads`` on a non-greedy bracket match without a
guard, surfacing a cryptic JSONDecodeError as a 500.
"""
import pytest
from fastapi import HTTPException

from routes.document.document_routes import _parse_tidy_verdicts, _pdf_extract_head


def test_pdf_extract_head_empty_content_does_not_crash():
    assert _pdf_extract_head("", "My Doc") == "# My Doc\n\n"


def test_pdf_extract_head_preserves_front_matter():
    content = "<!-- pdf_source: abc -->\n# Title\n\nbody text"
    assert _pdf_extract_head(content, "T") == "<!-- pdf_source: abc -->\n# Title\n\n"


def test_pdf_extract_head_falls_back_to_first_line():
    assert _pdf_extract_head("Hello\nmore", "T") == "Hello\n\n# T\n\n"


def test_parse_tidy_verdicts_valid():
    assert _parse_tidy_verdicts('["junk", "keep"]') == ["junk", "keep"]


def test_parse_tidy_verdicts_prose_wrapped_brackets_raise_clean_500():
    with pytest.raises(HTTPException) as ei:
        _parse_tidy_verdicts('I looked [at the docs] and decided: ["junk"]')
    assert ei.value.status_code == 500


def test_parse_tidy_verdicts_missing_array_raises_clean_500():
    with pytest.raises(HTTPException) as ei:
        _parse_tidy_verdicts("42")
    assert ei.value.status_code == 500
