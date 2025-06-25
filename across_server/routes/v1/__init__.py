import uuid

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from ... import auth, core
from ...core.middleware import LoggingMiddleware
from . import (
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

api = FastAPI()

api.add_middleware(LoggingMiddleware)

# This middleware must be placed after the logging, to populate the context with the request ID
# NOTE: Why last??
# Answer: middlewares are applied in the reverse order of when they are added (you can verify this
# by debugging `app.middleware_stack` and recursively drilling down the `app` property).
api.add_middleware(
    CorrelationIdMiddleware,
    header_name=core.config.REQUEST_ID_HEADER,
    update_request_header=True,
    generator=lambda: uuid.uuid4().hex,
)

api.include_router(auth.router)
api.include_router(permission.router)
api.include_router(user.router)
api.include_router(user.service_account.router)
api.include_router(user.service_account.group_role.router)
api.include_router(role.router)
api.include_router(group.router)
api.include_router(group.group_role.router)
api.include_router(group.group_invite.router)
api.include_router(schedule.router)
api.include_router(tle.router)
api.include_router(observatory.router)
api.include_router(telescope.router)
api.include_router(instrument.router)
api.include_router(observation.router)
