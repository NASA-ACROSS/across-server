import datetime
import logging
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .....core.exceptions import AcrossHTTPException, NotFoundException
from .....db import models
from .....db.database import get_session

log = logging.getLogger("uvicorn.error")


class ServiceAccountGroupRoleService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def assign(
        self,
        service_account: models.ServiceAccount,
        group_role: models.GroupRole,
        user: models.User,
    ) -> models.ServiceAccount:
        if service_account is None:
            raise NotFoundException("service account", service_account.id)
        if service_account.expiration <= datetime.datetime.now():
            raise AcrossHTTPException(
                422,
                "service account cannot be expired",
                log_data={
                    "service_account": f"{service_account.id}",
                    "expiration": f"{service_account.expiration}",
                },
            )
        if service_account.group_roles is None:
            raise NotFoundException("service account group roles", service_account.id)
        if group_role is None:
            raise NotFoundException("group role", group_role.id)
        if user is None:
            raise NotFoundException("user", user.id)
        if user.group_roles is None:
            raise NotFoundException("user group roles", user.id)
        if group_role not in user.group_roles:
            raise NotFoundException("group role in user group roles", group_role.id)

        service_account.group_roles.append(group_role)
        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account

    async def remove(
        self, service_account: models.ServiceAccount, group_role: models.GroupRole
    ) -> models.ServiceAccount:
        if service_account is None:
            raise NotFoundException("service account", service_account.id)
        if service_account.group_roles is None:
            raise NotFoundException("service account group roles", service_account.id)
        if group_role is None:
            raise NotFoundException("group_role", group_role.id)
        if group_role not in service_account.group_roles:
            raise NotFoundException("group_role", group_role.id)

        service_account.group_roles.remove(group_role)
        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account
