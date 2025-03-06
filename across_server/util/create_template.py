from collections.abc import Callable
from typing import TypeVar, cast

T = TypeVar("T", bound=dict)


def create_template(base: T) -> Callable[[dict | None], T]:
    def template(temp: dict | None = None) -> T:
        base_copy = cast(T, base.copy())
        if temp:
            base_copy.update(temp)
        return base_copy

    return template
