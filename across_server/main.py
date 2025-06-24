import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, status
from ratelimit import RateLimitMiddleware
from ratelimit.backends.simple import MemoryBackend

from across_server import db

from . import auth
from .core import config, limiter, logging
from .core.middleware import LoggingMiddleware
from .routes import (
    group,
    instrument,
    observation,
    observatory,
    permission,
    role,
    schedule,
    telescope,
    tle,
    user,
)

# Configure UTC system time
os.environ["TZ"] = "UTC"
time.tzset()

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logging.setup(json_logs=config.LOG_JSON_FORMAT, log_level=config.LOG_LEVEL)
    db.init()

    yield


app = FastAPI(
    title="ACROSS Server",
    summary="Astrophysics Cross-Observatory Science Support (ACROSS)",
    description="Server providing tools and utilities for various NASA missions to aid in coordination of large observation efforts.",
    root_path=config.ROOT_PATH,
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    authenticate=limiter.authenticate_limit,
    backend=MemoryBackend(),
    config=limiter.rules,
    on_blocked=limiter.on_limit_exceeded,
)
# This middleware must be placed after the logging, to populate the context with the request ID
# NOTE: Why last??
# Answer: middlewares are applied in the reverse order of when they are added (you can verify this
# by debugging `app.middleware_stack` and recursively drilling down the `app` property).
app.add_middleware(
    CorrelationIdMiddleware,
    header_name=config.REQUEST_ID_HEADER,
    update_request_header=True,
    generator=lambda: uuid.uuid4().hex,
)


@app.get(
    "/health",
    summary="Health Check",
    description="Health Check Route",
    status_code=status.HTTP_200_OK,
)
async def get() -> str:
    logger.debug("health check!")
    return "ok"


app.include_router(auth.router)
app.include_router(permission.router)
app.include_router(user.router)
app.include_router(user.service_account.router)
app.include_router(user.service_account.group_role.router)
app.include_router(role.router)
app.include_router(group.router)
app.include_router(group.group_role.router)
app.include_router(group.group_invite.router)
app.include_router(schedule.router)
app.include_router(tle.router)
app.include_router(observatory.router)
app.include_router(telescope.router)
app.include_router(instrument.router)
app.include_router(observation.router)
