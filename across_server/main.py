import os
import time
import uuid
import structlog

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request, Response, status

from across_server.core.middleware import log_response

from . import auth
from .core import logging, config
from .routes import group, observation, role, schedule, tle, user

# Configure UTC system time
os.environ["TZ"] = "UTC"
time.tzset()

logging.setup(json_logs=config.LOG_JSON_FORMAT, log_level=config.LOG_LEVEL)
access_logger: structlog.stdlib.BoundLogger = structlog.get_logger()

app = FastAPI(
    title="ACROSS Server",
    summary="Astrophysics Cross-Observatory Science Support (ACROSS)",
    description="Server providing tools and utilities for various NASA missions to aid in coordination of large observation efforts.",
    root_path=config.ROOT_PATH,
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    start_time = time.perf_counter_ns()
    # If the call_next raises an error, we still want to return our own 500 response,
    # so we can add headers to it (process time, request ID...)
    response = Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    try:
        response = await call_next(request)
    except Exception:
        # TODO: Validate that we don't swallow exceptions (unit test?)
        structlog.stdlib.get_logger("api.error").exception("Uncaught exception")
        raise
    finally:
        process_time = time.perf_counter_ns() - start_time
        status_code = response.status_code
        route = request.url.path
        client_host = request.client.host if request.client else ""
        client_port = request.client.port if request.client else ""
        http_method = request.method
        http_version = request.scope["http_version"]

        # Recreate the Uvicorn access log format, but add all parameters as structured information
        access_logger.info(
            f"""{client_host}:{client_port} - "{http_method} {route} HTTP/{http_version}" {status_code}""",
            http={
                "url": str(request.url),
                "status_code": status_code,
                "method": http_method,
                "request_id": request.headers[config.REQUEST_ID_HEADER],
                "version": http_version,
            },
            network={"client": {"ip": client_host, "port": client_port}},
            duration=process_time,
        )

        response.headers["X-Process-Time"] = str(process_time / 10**9)

        return response


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
    description="Container Health Check Route",
    status_code=status.HTTP_200_OK,
)
async def get():
    access_logger.debug("hello %s", "world")
    return "ok"


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(user.service_account.router)
app.include_router(role.router)
app.include_router(group.router)
app.include_router(group.group_role.router)
app.include_router(observation.router)
app.include_router(schedule.router)
app.include_router(tle.router)
