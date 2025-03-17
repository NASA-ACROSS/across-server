from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import APIRouter, HTTPException, status

from ...core.config import config


def local_only_route(router: APIRouter, path: str, **route_kwargs: Any) -> Callable:
    """
    Decorator that restricts access to and inclusion in openAPI docs of a route if the environment is local.
    """

    def decorator(func: Callable) -> Callable:
        is_local = config.is_local()

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Callable:
            # Restrict access if not running in local environment
            if is_local:
                return await func(*args, **kwargs)

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This route is only available in the local environment",
            )

        # Register the route with the router and include in schema if local
        router.add_api_route(
            path,
            wrapper,
            include_in_schema=is_local,
            **route_kwargs,
        )

        return wrapper

    return decorator
