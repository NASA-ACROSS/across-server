import os
import time
import uuid

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, status
from out.python import across_server_sdk as across
from out.python.across_server_sdk import models

from . import auth
from .core import config, logging
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

# 1) Boot‑strap your client config (no token yet)
across_sdk_config = across.Configuration(host="https://api.across-server.com")

with across.ApiClient(across_sdk_config) as client:
    # 2) Get a token
    auth_api = across.AuthApi(client)
    token_res = auth_api.token(
        _headers={"Authorization": "Basic <client_id:client_secret>"}
    )
    access_token = token_res.data.access_token

    # 3) Inject the token into the same Configuration
    client.configuration.access_token = access_token

    observatory_api = across.ObservatoryApi(client)
    res = observatory_api.get_observatories()

    schedule_api = across.ScheduleApi(client)
    schedule_res = schedule_api.create_schedule(across.ScheduleCreate(...))

# Configure UTC system time
os.environ["TZ"] = "UTC"
time.tzset()

logging.setup(json_logs=config.LOG_JSON_FORMAT, log_level=config.LOG_LEVEL)
logger: structlog.stdlib.BoundLogger = structlog.get_logger()

app = FastAPI(
    title="ACROSS Server",
    summary="Astrophysics Cross-Observatory Science Support (ACROSS)",
    description="Server providing tools and utilities for various NASA missions to aid in coordination of large observation efforts.",
    root_path=config.ROOT_PATH,
)


app.add_middleware(LoggingMiddleware)

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
    "/",
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
