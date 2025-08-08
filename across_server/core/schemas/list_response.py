from typing import Generic, TypeVar

from pydantic import RootModel

T = TypeVar("T")


class ListResponse(RootModel[list[T]], Generic[T]):
    """
    Generic Pydantic root model representing a top-level list of items.

    This is useful for OpenAPI documentation and SDK generation when your
    endpoint returns a flat list of objects (primitives or Pydantic models)
    rather than a dictionary.

    Example usage in FastAPI:

        from fastapi import APIRouter
        import uuid

        router = APIRouter()

        @router.post(
            "/schedules",
            response_model=list[uuid.UUID],  # plain list at runtime
            responses={
                201: {
                    "model": ListResponse[uuid.UUID],  # fixes OpenAPI doc & SDK
                    "description": "Created schedule ids",
                }
            }
        )
        def create_schedules():
            # return a plain Python list — no wrapper needed
            return [uuid.uuid4(), uuid.uuid4()]

    Notes:
        - Generic over `T`: can be a list of any kind.
        - Ensures OpenAPI sees a list of items with proper type, avoiding Optional.
        - No extra fields are needed; the entire list is the "root" of the model.
    """

    pass
