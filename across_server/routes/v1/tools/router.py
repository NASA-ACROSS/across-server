from fastapi import APIRouter, status

from across_server.routes.v1.tools import (
    resolve_object,
    too_toolkit_test,
    visibility_calculator,
)

router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The tool does not exist.",
        },
    },
)

router.include_router(resolve_object.router)
router.include_router(visibility_calculator.router)
router.include_router(too_toolkit_test.router)
