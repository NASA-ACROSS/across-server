import time
import structlog

from fastapi import Request, Response, status
from starlette.types import ASGIApp, Message, Scope, Receive, Send

from ..config import config

logger = structlog.stdlib.get_logger()


class LogResponseMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        start_time = time.perf_counter_ns()

        # If the call_next raises an error, we still want to return our own 500 response,
        # so we can add headers to it (process time, request ID...)
        response = Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            await self.app(scope, receive, send)
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
            logger.info(
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


async def log_response(request: Request, call_next) -> Response:
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
        logger.info(
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
