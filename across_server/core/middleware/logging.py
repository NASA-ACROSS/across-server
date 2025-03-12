import time

import structlog
from fastapi import Request, Response, status
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class LoggingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time.perf_counter_ns()
        response = Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        async def send_wrapper(message: Message) -> None:
            nonlocal response
            if message["type"] == "http.response.start":
                response = Response(status_code=message["status"])

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            structlog.stdlib.get_logger("api.error").exception("Uncaught exception")
            raise
        finally:
            process_time = time.perf_counter_ns() - start_time
            status_code = response.status_code
            route = request.url.path
            client_host = request.client.host if request.client else ""
            client_port = request.client.port if request.client else ""
            http_method = request.method
            http_version = scope.get("http_version", "")

            logger.info(
                f'{client_host}:{client_port} - "{http_method} {route} HTTP/{http_version}" {status_code}',
                http={
                    "url": str(request.url),
                    "status_code": status_code,
                    "method": http_method,
                    "version": http_version,
                },
                network={"client": {"ip": client_host, "port": client_port}},
                duration=process_time,
            )
