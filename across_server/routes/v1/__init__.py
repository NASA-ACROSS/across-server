from fastapi import FastAPI

from ... import __version__, auth
from ...core import config
from . import (
    filter,
    group,
    instrument,
    observation,
    observatory,
    permission,
    role,
    schedule,
    system_service_account,
    telescope,
    tle,
    tools,
    user,
)

api = FastAPI(
    title=config.APP_TITLE,
    summary=config.APP_SUMMARY,
    description=config.APP_DESCRIPTION,
    version=__version__,
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
api.include_router(filter.router)
api.include_router(system_service_account.router)
api.include_router(tools.router)
