from fastapi import FastAPI

from ... import auth
from . import (
    filter,
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
