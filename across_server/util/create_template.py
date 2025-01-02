from typing import Callable, Dict, Optional, TypeVar, cast

T = TypeVar("T", bound=Dict)


def create_template(base: T) -> Callable[[Optional[Dict]], T]:
    def template(temp: Optional[Dict] = None) -> T:
        base_copy = cast(T, base.copy())
        if temp:
            base_copy.update(temp)
        return base_copy

    return template
