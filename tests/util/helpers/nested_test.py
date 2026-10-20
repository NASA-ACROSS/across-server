from typing import Any

import pytest

from across_server.util.helpers import nested

data = {
    "a": {
        "b": {
            "c": 1,
        }
    }
}


@pytest.mark.parametrize(
    "obj, key, expected",
    [
        (data, "a.b.c", True),
        (data, "a.b.d", False),
        (data, "a.b", True),
        ("str", "a.b.c", False),
        (1, "a.b.c", False),
    ],
)
def test_should_have_key(obj: Any, key: str, expected: bool) -> None:
    assert nested.has_key(obj, key) is expected


@pytest.mark.parametrize(
    "obj, key, expected",
    [
        (data, "a.b.c", 1),
        (data, "a.b.d", None),
        (data, "a.b", {"c": 1}),
        ("str", "a.b.c", None),
        (1, "a.b.c", None),
    ],
)
def test_should_get_value(obj: Any, key: str, expected: Any) -> None:
    assert nested.get_value(obj, key) == expected
