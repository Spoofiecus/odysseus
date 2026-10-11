"""Issue #5076: _parse_json_object must only ever return a dict.

json.loads returns any JSON type; a model replying with a JSON array used to
make the helper return a truthy list, and the callers then crashed on
``parsed.get(...)`` with AttributeError.
"""
from src.deep_research import DeepResearcher


def _researcher():
    return DeepResearcher("http://localhost:1/v1", "test-model")


def test_json_array_returns_none():
    assert _researcher()._parse_json_object('["topic1", "topic2"]') is None


def test_json_scalar_returns_none():
    assert _researcher()._parse_json_object("42") is None
    assert _researcher()._parse_json_object('"just a string"') is None
    assert _researcher()._parse_json_object("true") is None


def test_json_object_returns_dict():
    assert _researcher()._parse_json_object('{"sub_questions": ["a"]}') == {
        "sub_questions": ["a"]
    }


def test_embedded_object_still_extracted():
    assert _researcher()._parse_json_object('sure: {"sub_questions": ["a"]} done') == {
        "sub_questions": ["a"]
    }
