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
            raise NotFoundException("service account")
        if service_account.expiration is None:
            raise NotFoundException("service account expiration")
        if service_account.expiration <= datetime.datetime.now():
            raise AcrossHTTPException(
                422,
                "service account cannot be expired",
                log_data={
                    "service_account": f"{service_account.id}",
                    "expiration": f"{service_account.expiration}",
                },
            )
        if group_role is None:
            raise NotFoundException("group role")
        if user is None:
            raise NotFoundException("user")
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
            raise NotFoundException("service account", None)
        if group_role is None:
            raise NotFoundException("group_role", None)
        if group_role not in service_account.group_roles:
            # when a user requests to remove a role that is not in the service account
            # we should gracefully respond with ok
            return service_account

        service_account.group_roles.remove(group_role)
        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account
