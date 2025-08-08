from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import APIRouter

from ...core.config import config


def local_only_route(router: APIRouter, path: str, **route_kwargs: Any) -> Callable:
    """
    Decorator that adds a route to the router only for local environments.
    - Excludes the route from OpenAPI schema in non-local environments.
    - Blocks access to the route with HTTP 403 in non-local environments.
    """

    def decorator(func: Callable) -> Callable:
        if not config.is_local() or config.HIDE_LOCAL_ROUTE:
            # Don't register the route in non-local or if they're hidden
            return func

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await func(*args, **kwargs)

        # Register the route with the router and include in schema if local
        router.add_api_route(
            path,
            wrapper,
            **route_kwargs,
        )

        return wrapper

    return decorator
