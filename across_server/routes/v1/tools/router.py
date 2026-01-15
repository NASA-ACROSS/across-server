from fastapi import APIRouter, status

from across_server.routes.v1.tools import resolve, visibility_calculator

router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The tool does not exist.",
        },
    },
)

router.include_router(resolve.router)
router.include_router(visibility_calculator.router)
